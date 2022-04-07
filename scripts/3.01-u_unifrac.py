#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=long
#SBATCH --nodes=4
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=32G
#SBATCH --time=24:00:00

import logging
import time

import unifrac


def main():
    logger = logging.getLogger("unifrac")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s - %(name)s - %(levelname)s] :: %(message)s"
    )
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    tbl_file = "data/processed/table.rare.filt.biom"
    tree = "results/processed/sepp/tbl_gg_placement.tog.relabelled.tre"

    logger.info("Running UniFrac...")
    dm = unifrac.unweighted(tbl_file, tree)
    logger.info("UniFrac finished!")
    dm.write("results/distance-matrix-u_unifrac.tsv")


if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)
