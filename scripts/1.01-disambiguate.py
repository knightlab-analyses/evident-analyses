#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=short
#SBATCH --mem=8G
#SBATCH --time=6:00:00

from collections import defaultdict
import re

import biom
import numpy as np
import pandas as pd

from src.helper import get_logger, time_function


@time_function
def main():
    logger = get_logger()

    na_vals = ["Not provided"]

    ambig_prep_md_file = "data/raw/metadata.raw.prep.ambig.tsv"
    ambig_prep_md = pd.read_table(ambig_prep_md_file, sep="\t", index_col=0,
                                  na_values=na_vals)
    logger.info(f"Ambiguous prep metadata shape: {ambig_prep_md.shape}")

    ambig_tbl = biom.load_table("data/raw/table.raw.ambig.biom")
    logger.info(f"Ambiguous table shape: {ambig_tbl.shape}")

    ambig_tbl_depths = pd.Series(ambig_tbl.sum(axis="sample"),
                                 index=ambig_tbl.ids())
    assert set(ambig_tbl.ids()) == set(ambig_prep_md.index)

    samp_regex = re.compile("(10317\.\d+\w?)\.")

    # ambig -> unambig
    sample_id_disambig = defaultdict(list)
    for idx in ambig_prep_md.index:
        disambig_id = samp_regex.search(idx).groups()[0]
        sample_id_disambig[disambig_id].append(idx)

    samps_to_keep = []
    for ambig_samp, unambig_samp_list in sample_id_disambig.items():
        samps_to_keep.append(ambig_tbl_depths.loc[unambig_samp_list].idxmax())
    logger.info(f"Number of samples to keep: {len(samps_to_keep)}")

    ambig_samp_md_file = "data/raw/metadata.raw.ambig.tsv"
    ambig_samp_md = pd.read_table(ambig_samp_md_file, sep="\t", index_col=0,
                                  na_values=na_vals)
    logger.info(f"Ambiguous sample metadata shape: {ambig_samp_md.shape}")

    disambig_md = ambig_prep_md.loc[samps_to_keep]
    disambig_md["disambig_sample_name"] = [
        samp_regex.search(x).groups()[0]
        for x in disambig_md.index
    ]
    disambig_md = disambig_md.join(ambig_samp_md, how="inner")
    logger.info(f"Disambiguated metadata shape: {disambig_md.shape}")

    disambig_tbl = ambig_tbl.filter(
        disambig_md.index,
        inplace=False
    ).remove_empty()
    logger.info(f"Disambiguated table shape: {disambig_tbl.shape}")

    out_tbl = "data/intermediate/table.disambig.biom"
    with biom.util.biom_open(out_tbl, "w") as f:
        disambig_tbl.to_hdf5(f, "disambiguated")
    logger.info(f"Saved disambiguated table to {out_tbl}!")

    out_md = "data/intermediate/metadata.disambig.tsv"
    disambig_md.to_csv(out_md, sep="\t", index=True)
    logger.info(f"Saved disambiguated metadata to {out_md}!")


if __name__ == "__main__":
    main()
