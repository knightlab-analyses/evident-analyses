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
SAMPLE_FILE="data/raw/samples.ambig.txt"
TBL_FILE="data/raw/table.raw.ambig.biom"
MD_PREP_FILE="data/raw/metadata.raw.prep.ambig.tsv"
MD_FILE="data/raw/metadata.raw.ambig.tsv"
DM="data/ref/unweighted.txt.gz"

python -c "from skbio import DistanceMatrix; dm = DistanceMatrix.read('${DM}'); x = dm.ids; f = open('${SAMPLE_FILE}', 'w'); f.writelines('\n'.join(x)); f.close()"

echo "[ $(date) ] :: Start redbiom fetch samples"
redbiom fetch samples \
    --from $SAMPLE_FILE \
    --context $CTX \
    --output $TBL_FILE

echo "[ $(date) ] :: Start redbiom fetch sample prep metadata"
redbiom fetch sample-metadata \
    --from $SAMPLE_FILE \
    --context $CTX \
    --tagged \
    --all-columns \
    --output $MD_PREP_FILE

echo "[ $(date) ] :: Start redbiom fetch sample metadata"
redbiom fetch sample-metadata \
    --from $SAMPLE_FILE \
    --context $CTX \
    --all-columns \
    --output $MD_FILE

echo "[ $(date) ] :: Finished script!"

biom summarize-table -i $TBL_FILE | head
