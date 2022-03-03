#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=long
#SBATCH --mem=32G
#SBATCH --time=12:00:00

import os
import logging
import re
import time

import evident
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

    alpha = [0.01, 0.05, 0.10]
    total_observations = np.arange(20, 501, step=20)

    out_dir = "results/agp/power"
    os.makedirs(out_dir, exist_ok=True)

    for col in md:
        logger.info(f"Column: {col}")
        res = bdh.power_analysis(col, alpha=alpha,
                                 total_observations=total_observations)
        res = res.to_dataframe()
        fname = f"{out_dir}/{col}_power.tsv"
        res.to_csv(fname, sep="\t")
        print(res.head())


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start}")
