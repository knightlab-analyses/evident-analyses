#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=short
#SBATCH --mem=8G
#SBATCH --time=6:00:00

import logging
import re
import time

import biom
import numpy as np
import pandas as pd


def main():
    logger = logging.getLogger("process")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(name)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    md_file = "data/agp/metadata.filt.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)

    disease_map = {
        "I do not have this condition": "No",
        "Diagnosed by a medical professional (doctor, physician assistant)": "Yes"
    }
    disease_cols = [
        "lung_disease",
        "kidney_disease",
        "cardiovascular_disease",
        "liver_disease",
        "skin_condition",
        "ibd",
        "ibs",
        "asd"
    ]

    mental_illness_map = {
        "TRUE": "Yes",
        "FALSE": "No",
        "false": "No",
        "true": "Yes",
        "Yes": "Yes",
        "No": "No"
    }
    other_cols = [
        "sex",
        "mental_illness"
    ]

    for col in disease_cols:
        md[col] = md[col].map(disease_map)

    md["mental_illness"] = md["mental_illness"].map(mental_illness_map)
    md = md[disease_cols + other_cols]

    out_md = "data/agp/metadata.filt.subset.tsv"
    md.to_csv(out_md, sep="\t", index=True)

    logger.info(f"Saved metadata subset to {out_md}!")


if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)
