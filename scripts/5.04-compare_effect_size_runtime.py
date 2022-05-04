#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=6:00:00

import time

import evident
from evident.effect_size import effect_size_by_category
import numpy as np
import pandas as pd
from skbio import DistanceMatrix

from src.helper import get_logger, time_function


def run_parallel(logger):
    logger.info("Starting parallel function...")
    md_file = "data/processed/metadata.disambig.filt.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)
    md.index = md.index.astype(str)

    logger.info("Loading distance matrix...")
    dm = DistanceMatrix.read(
        "results/distance-matrix-u_unifrac.tsv"
    )
    logger.info("Finished loading distance matrix!")

    bdh = evident.BetaDiversityHandler(dm, md)

    logger.info("Calculating effect sizes...")
    start_time = time.time()
    res = effect_size_by_category(
        bdh,
        bdh.metadata.columns,
        n_jobs=4,
        parallel_args={
            "backend": "multiprocessing",
            "batch_size": 1,
            "verbose": 100
        }
    )
    res_df = res.to_dataframe()
    end_time = time.time()
    logger.info(f"Parallel runtime: {end_time - start_time}")


def run_serial(logger):
    logger.info("Starting serial function...")
    md_file = "data/processed/metadata.disambig.filt.tsv"
    md = pd.read_table(md_file, sep="\t", index_col=0)
    md.index = md.index.astype(str)

    logger.info("Loading distance matrix...")
    dm = DistanceMatrix.read(
        "results/distance-matrix-u_unifrac.tsv"
    )
    logger.info("Finished loading distance matrix!")

    bdh = evident.BetaDiversityHandler(dm, md)

    logger.info("Calculating effect sizes...")
    start_time = time.time()
    res = effect_size_by_category(
        bdh,
        bdh.metadata.columns,
        n_jobs=1,
    )
    res_df = res.to_dataframe()
    end_time = time.time()
    logger.info(f"Serial runtime: {end_time - start_time}")


@time_function
def main():
    logger = get_logger()
    run_parallel(logger)
    run_serial(logger)


if __name__ == "__main__":
    main()
