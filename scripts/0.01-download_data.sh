#!/usr/bin/bash
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=long
#SBATCH --mem=16G
#SBATCH --time=12:00:00

set -e
date; pwd; hostname

echo "[ $(date) ] :: Start script"

source ~/miniconda3/bin/activate evident-analyses

mkdir -p "data/raw"

CTX="Deblur_2021.09-Illumina-16S-V4-100nt-50b3a2"
SAMPLE_FILE="data/raw/samples.txt"
TABLE="data/raw/table.raw.biom"
MD="data/raw/metadata.raw.tsv"
MD_PREP="data/raw/metadata.prep.raw.tsv"
DM="data/ref/unweighted.txt.gz"

python -c "from skbio import DistanceMatrix; dm = DistanceMatrix.read('${DM}'); x = dm.ids; f = open('${SAMPLE_FILE}', 'w'); f.writelines('\n'.join(x)); f.close()"

echo "[ $(date) ] :: Start redbiom fetch samples"
redbiom fetch samples \
    --from $SAMPLE_FILE \
    --context $CTX \
    --resolve-ambiguities most-reads \
    --output $TABLE

echo "[ $(date) ] :: Start redbiom fetch sample metadata"
redbiom fetch sample-metadata \
    --from $SAMPLE_FILE \
    --context $CTX \
    --resolve-ambiguities \
    --all-columns \
    --output $MD

echo "[ $(date) ] :: Start redbiom fetch sample prep metadata"
redbiom fetch sample-metadata \
    --from $SAMPLE_FILE \
    --context $CTX \
    --tagged \
    --all-columns \
    --output $MD_PREP

echo "[ $(date) ] :: Finished script!"

biom summarize-table -i $TABLE
