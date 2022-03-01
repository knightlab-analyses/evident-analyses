#!/home/grahman/miniconda3/envs/matchlock/bin/python
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
    logger = logging.getLogger("filter")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(name)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    tbl = biom.load_table("data/agp/table.biom")
    md_file = "data/agp/metadata.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)

    logger.info(f"Original table shape: {tbl.shape}")

    # Update names of samples with S for string coercion
    samp_name_dict = {k: "S" + k for k in tbl.ids()}
    tbl.update_ids(samp_name_dict, axis="sample")
    md.index = "S" + md.index.astype(str)

    samps_in_common = list(set(md.index).intersection(tbl.ids()))
    md = md.loc[samps_in_common]
    tbl.filter(samps_in_common)

    prev = tbl.pa(inplace=False).sum(axis="observation")
    feats_to_keep = tbl.ids(axis="observation")[np.where(prev >= 50)]
    tbl.filter(feats_to_keep, "observation")

    logger.info(f"Filtered table shape: {tbl.shape}")
    logger.info(f"Filtered metadata shape: {md.shape}")

    out_tbl = "data/agp/table.filt.biom"
    out_md = "data/agp/metadata.filt.tsv"

    with biom.util.biom_open(out_tbl, "w") as f:
        tbl.to_hdf5(f, "filtered")
    logger.info(f"Saved filtered table to {out_tbl}!")

    md.to_csv(out_md, sep="\t", index=True)
    logger.info(f"Saved filtered metadata to {out_md}!")

if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)
