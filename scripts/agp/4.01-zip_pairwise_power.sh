#!/usr/bin/bash
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=short
#SBATCH --mem=12G
#SBATCH --time=6:00:00

set -e

echo "[ $(date) ] :: Start script"
date; pwd; hostname

source ~/miniconda3/bin/activate evident-analyses

PW_POWER_DIR="results/agp/power/pairwise"
cd $PW_POWER_DIR

DIRS=$(find . -maxdepth 1 -mindepth 1 -type d | grep -oP "\w+")
for D in $DIRS
do
    # https://stackoverflow.com/a/3035446
    tar -czvf "${D}.tar.gz" -C $D .
done

echo "[ $(date) ] :: Finish script"
