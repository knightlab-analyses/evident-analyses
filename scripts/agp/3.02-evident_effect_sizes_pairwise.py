#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=long
#SBATCH --mem=32G
#SBATCH --time=12:00:00

import logging
import re
import time

import evident
from evident.effect_size import pairwise_effect_size_by_category
import numpy as np
import pandas as pd
from skbio import DistanceMatrix


def main():
    logger = logging.getLogger("evident")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(name)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    md_file = "data/agp/metadata.filt.subset.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)

    logger.info("Loading distance matrix...")
    dm = DistanceMatrix.read("results/agp/rpca/distance-matrix.tsv.gz")
    logger.info("Finished loading distance matrix!")

    bdh = evident.BetaDiversityHandler(dm, md)

    logger.info("Calculating pairwise effect sizes...")
    res = pairwise_effect_size_by_category(bdh, md.columns)
    res_df = res.to_dataframe()
    print(res_df)
    res_df.to_csv("results/agp/beta_pairwise_effect_size_by_cat.tsv", sep="\t")
    logger.info("Finished calculating pairwise effect sizes!")

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start}")
