#!/home/grahman/miniconda3/envs/evident-analyses/bin/python
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=long
#SBATCH --nodes=4
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=32G
#SBATCH --time=24:00:00

import unifrac

from src.helper import get_logger, time_function


@time_function
def main():
    logger = get_logger()

    tbl_file = "data/processed/table.disambig.rare.filt.biom"
    tree = "results/sepp_out/tbl_gg_placement.tog.relabelled.tre"

    logger.info("Running UniFrac...")
    dm = unifrac.unweighted(tbl_file, tree)
    logger.info("UniFrac finished!")
    dm.write("results/distance-matrix-u_unifrac.tsv")


if __name__ == "__main__":
    main()
