#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=16G
#SBATCH --time=6:00:00

import evident
from joblib import Parallel, delayed
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

    alpha = [0.01, 0.05, 0.10]
    total_observations = np.arange(20, 1501, step=40)

    parallel_args = {
        "backend": "multiprocessing",
        "verbose": 100,
        "batch_size": 1
    }
    results = Parallel(n_jobs=8, **parallel_args)(
        delayed(bdh.power_analysis)(
            col,
            alpha=alpha,
            total_observations=total_observations
        )
        for col in md.columns
    )
    res_df = pd.concat([x.to_dataframe() for x in results])
    logger.info(f"\n{res_df.head()}")
    res_df.to_csv("results/power_analysis.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
