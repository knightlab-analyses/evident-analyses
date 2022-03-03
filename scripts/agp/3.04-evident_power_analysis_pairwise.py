#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=long
#SBATCH --mem=32G
#SBATCH --time=12:00:00

from itertools import combinations
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

    out_dir = "results/agp/power/pairwise"
    os.makedirs(out_dir, exist_ok=True)

    for col in md:
        logger.info(f"===== Column: {col} =====")
        uniq_grps = md[col].dropna().unique()
        this_out_dir = f"{out_dir}/{col}"
        os.makedirs(this_out_dir, exist_ok=True)
        for grp1, grp2 in combinations(uniq_grps, 2):
            logger.info(f"Group1: {grp1}, Group2: {grp2}")

            # Everything else should be NaN
            pwise_map = {grp: grp for grp in uniq_grps if grp in [grp1, grp2]}
            bdh.metadata["tmp_col"] = bdh.metadata[col].map(pwise_map)
            logger.info(f"\n{bdh.metadata['tmp_col'].value_counts()}")
            res = bdh.power_analysis("tmp_col", alpha=alpha,
                                     total_observations=total_observations)
            res = res.to_dataframe()

            grp1_fname = grp1.replace(" ", "_")
            grp2_fname = grp2.replace(" ", "_")
            fname = f"{this_out_dir}/{grp1_fname}_vs_{grp2_fname}_power.tsv"
            res.to_csv(fname, sep="\t")
            logger.info(f"\n{res.head()}")
            logger.info(f"Saved to {fname}!")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start}")
