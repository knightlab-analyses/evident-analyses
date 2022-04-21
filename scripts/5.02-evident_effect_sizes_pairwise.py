#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=6:00:00

import evident
from evident.effect_size import pairwise_effect_size_by_category
import numpy as np
import pandas as pd
from skbio import DistanceMatrix

from src.helper import get_logger, time_function


@time_function
def main():
    logger = get_logger()

    md_file = "data/processed/metadata.disambig.filt.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)

    logger.info("Loading distance matrix...")
    dm = DistanceMatrix.read(
        "results/distance-matrix-u_unifrac.tsv"
    )
    logger.info("Finished loading distance matrix!")

    bdh = evident.BetaDiversityHandler(dm, md)

    logger.info("Calculating pairwise effect sizes...")
    res = pairwise_effect_size_by_category(
        bdh,
        md.columns,
        n_jobs=4,
        parallel_args={
            "backend": "multiprocessing",
            "batch_size": 1,
            "verbose": 100
        }
    )
    res_df = res.to_dataframe()
    logger.info(f"\n{res_df}")
    res_df.to_csv("results/beta_pairwise_effect_size_by_cat.tsv", sep="\t")
    logger.info("Finished calculating pairwise effect sizes!")


if __name__ == "__main__":
    main()
