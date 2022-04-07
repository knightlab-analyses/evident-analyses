#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=short
#SBATCH --mem=8G
#SBATCH --time=6:00:00

import logging
import time

import biom
from bloom import remove_seqs, trim_seqs
import numpy as np
import pandas as pd
import skbio

def get_replacements_dict():
    replacements = dict()

    # For age, we'll oonly look at people up to the age of 69, so we'll ignore
    # the "70+" category, which is unbounded.
    replacements["age_cat"] = {"70+": np.nan}
    # We dropped people who were uncertain about their stool quality for the
    # comparison, since this was a special category.
    replacements["bowel_movement_quality"] = {
        "I don't know, I do not have a point of reference": np.nan}
    replacements["exercise_location"] = {"None of the above": np.nan}
    # There are also several ordinal categories where the extremes are too
    # small to be analyzed on their own, but could be combined.
    replacements["antibiotic_history"] = {"Week": "Month"}
    replacements["sleep_duration"] = {
        "Less than 5 hours": "Less than 6", "5-6 hours": "Less than 6"}
    replacements["bowel_movement_frequency"] = {
        "Four": "Four or more", "Five or more": "Four or more"}
    replacements["diet_type"] = {"Vegan": "Vegetarian"}
    replacements["last_move"] = {
        "Within the past month": "Within the past 3 months"}
    replacements["pool_frequency"] = {
        "Occasionally (1-2 times/week)": "Weekly",
        "Regularly (3-5 times/week)": "Weekly", "Daily": "Weekly"}
    replacements["smoking_frequency"] = {
        "Occasionally (1-2 times/week)": "Weekly",
        "Regularly (3-5 times/week)": "Weekly", "Daily": "Weekly"}
    replacements["sugar_sweetened_drink_frequency"] = {
        "Occasionally (1-2 times/week)": "Weekly",
        "Regularly (3-5 times/week)": "Weekly", "Daily": "Weekly"}
    replacements["vivid_dreams"] = {
        "Occasionally (1-2 times/week)": "Weekly",
        "Regularly (3-5 times/week)": "Weekly", "Daily": "Weekly"}
    replacements["frozen_dessert_frequency"] = {
        "Occasionally (1-2 times/week)": "Weekly",
        "Regularly (3-5 times/week)": "Weekly", "Daily": "Weekly"}
    # We"ll also combine vegans and vegetarians into a single category.
    replacements["vegetable_frequency"] = {
        "Never": "Less than weekly",
        "Rarely (less than once/week)": "Less than weekly"}
    # New additions
    replacements["bmi_cat"] = {
        "Underweight": np.nan
    }

    return replacements


def main():
    logger = logging.getLogger("filter")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(name)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    tbl = biom.load_table("data/raw/table.raw.biom")
    samp_rename_dict = {x: f"S{x}" for x in tbl.ids()}
    tbl.update_ids(samp_rename_dict)

    na_vals = ["Not provided"]
    orig_md_file = "data/ref/ag_map_with_alpha.txt.quartiles.tsv"
    orig_md = pd.read_table(orig_md_file, sep="\t", index_col=0,
                            na_values=na_vals)
    orig_md.index = "S" + orig_md.index
    cols_to_remove = [
        "roommates",
        "age_cat",
        "bmi_corrected",
        "height_cm",
        "latitude",
        "longitude",
        "elevation",
        "collection_time",
        "allergic_to_i_have_no_food_allergies_that_i_know_of"
    ]
    cols_to_remove += [x for x in orig_md.columns if "vioscreen" in x]
    cols_to_remove += [x for x in orig_md.columns if "alcohol" in x]
    logger.info(
        "Dropping the following columns from original metadata:"
        f"\n{cols_to_remove}"
    )
    orig_md = orig_md.drop(columns=cols_to_remove)

    new_md_file = "data/raw/metadata.raw.tsv"
    new_md = pd.read_table(new_md_file, sep="\t", index_col=0,
                           na_values=na_vals)
    new_md.index = "S" + new_md.index

    cols_in_common = set(orig_md.columns).intersection(new_md.columns)
    new_md = new_md[cols_in_common]

    prep_md_file = "data/raw/metadata.prep.raw.tsv"
    prep_md = pd.read_table(prep_md_file, sep="\t", index_col=0,
                            na_values=na_vals)

    prep_md.index = prep_md.index.str.extract("(10317\.\d+)", expand=False)
    prep_md.index = "S" + prep_md.index
    idx_to_keep = ~prep_md.index.duplicated(keep="first")
    prep_cols_to_use = [
        "center_project_name",
        "extraction_robot",
        "plating",
        "processing_robot"
    ]
    prep_md = prep_md[prep_cols_to_use]
    prep_md = prep_md.iloc[idx_to_keep]
    logger.info(
        "Including the following columns from redbiom prep metadata:"
        f"\n{prep_cols_to_use}"
    )
    new_md = new_md.join(prep_md, how="inner")

    bloom_seqs_file = "/home/grahman/software/bloom-analyses/data/newbloom.all.fna"
    seqs = skbio.read(bloom_seqs_file, format="fasta")
    length = min(map(len, tbl.ids(axis="observation")))
    seqs = trim_seqs(seqs, seqlength=length)

    logger.info(f"Original table shape: {tbl.shape}")

    samps_in_common = list(set(new_md.index).intersection(tbl.ids()))
    new_md = new_md.loc[samps_in_common]
    tbl.filter(samps_in_common)

    cond_map = {
        "I do not have this condition": "No",
        "Diagnosed by a medical professional (doctor, physician assistant)": "Yes",
        "Self-diagnosed": np.nan,
        "Diagnosed by an alternative medicine practitioner": np.nan
    }

    def replace_cond(item_1):
        if item_1 in cond_map:
            return cond_map[item_1]
        else:
            return item_1

    tf_map = {
        "True": "Yes",
        "true": "Yes",
        "TRUE": "Yes",
        "Yes": "Yes",
        "yes": "Yes",
        "false": "No",
        "False": "No",
        "FALSE": "No",
        "No": "No",
        "no": "No",
        True: "Yes",
        False: "No"
    }
    def replace_tf(item):
        if str(item) in tf_map:
            return tf_map[str(item)]
        else:
            return item

    def to_quartiles(values, q1, q2, q3):
        quartiles = []
        for val in values:
            if np.isnan(val):
                q = np.nan
            elif val < q1:
                q = "q1"
            elif q1 <= val < q2:
                q = "q2"
            elif q2 <= val < q3:
                q = "q3"
            else:
                q = "q4"
            quartiles.append(q)
        return quartiles

    bowel_movement_quality_map = {
        "I tend to be constipated (have difficulty passing stool) - Type 1 and 2": "I tend to be constipated (have difficulty passing stool)",
        "I tend to have normal formed stool - Type 3 and 4": "I tend to have normal formed stool",
        "I tend to have diarrhea (watery stool) - Type 5, 6 and 7": "I tend to have diarrhea (watery stool)"
    }
    new_md["bowel_movement_quality"] = (
        new_md["bowel_movement_quality"].replace(bowel_movement_quality_map)
    )
    logger.info("Replacing bowel_movement_quality values")

    country_map = {
        "USA": "USA",
        "United Kingdom": "United Kingdom",
        "Australia": "Australia",
        "Canada": "Canada"
    }
    new_md["country"] = new_md["country"].map(country_map)
    logger.info(f"Subsetting countries to only include:\n{list(country_map.keys())}")

    replacement_dict = get_replacements_dict()
    for col in new_md.columns:
        new_md[col] = new_md[col].map(replace_tf)
        new_md[col] = new_md[col].map(replace_cond)
        if new_md[col].dtype == np.dtype("float"):
            q1, q2, q3 = new_md[col].quantile([0.25, 0.5, 0.75])
            new_md[col] = to_quartiles(new_md[col], q1, q2, q3)

        if col in replacement_dict:
            col_dict = replacement_dict[col]
            new_md[col] = [
                col_dict[x]
                if col_dict.get(x)
                else x
                for x in new_md[col]
            ]

        vc = new_md[col].value_counts()
        if len(vc) == 1:
            new_md = new_md.drop(columns=[col])
            logger.info(f"Dropping {col} since it has only one level.")
            continue

        logger.info(f"\n{new_md[col].value_counts()}")

    logger.info(f"Filtered metadata shape: {new_md.shape}")

    # Bloom filtering
    # github.com/knightlab-analyses/bloom-analyses/
    logger.info("Bloom filtering...")
    tbl = remove_seqs(tbl, seqs)
    logger.info(f"Bloom filtered table shape: {tbl.shape}")

    # Rarefying
    logger.info("Rarefying to 1250...")
    tbl_rare = tbl.subsample(1250)
    logger.info(f"Rarefied filtered table shape: {tbl.shape}")

    tbl_out = "data/processed/table.rare.filt.biom"
    with biom.util.biom_open(tbl_out, "w") as f:
        tbl_rare.to_hdf5(f, "rarefied")
    logger.info(f"Saved table to {tbl_out}!")

    md_out = "data/processed/metadata.filt.tsv"
    new_md.to_csv(md_out, sep="\t", index=True)
    logger.info(f"Saved metadata to {md_out}!")


if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)
