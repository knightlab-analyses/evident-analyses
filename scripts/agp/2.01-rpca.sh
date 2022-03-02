#!/usr/bin/bash
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=short
#SBATCH --mem=12G
#SBATCH --time=6:00:00

echo "[ $(date) ] :: Start script"
date; pwd; hostname

source ~/miniconda3/bin/activate evident-analyses

TABLE="data/agp/table.filt.biom"
OUTDIR="results/agp/rpca"
DM="results/agp/rpca/distance-matrix.tsv"

echo "[ $(date) ] :: Starting RPCA..."

gemelli rpca \
    --in-biom $TABLE \
    --output-dir $OUTDIR \
    --n_components 5 \
    --min-sample-count 500

echo "[ $(date) ] :: RPCA finished!"

echo "[ $(date) ] :: Zipping distance matrix..."

gzip $DM

echo "[ $(date) ] :: Zipping finished!"

echo "[ $(date) ] :: Finish script"
