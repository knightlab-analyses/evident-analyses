#!/usr/bin/bash
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/AGP-%x.log
#SBATCH --partition=long
#SBATCH --mem=16G
#SBATCH --time=12:00:00

date; pwd; hostname

source ~/miniconda3/bin/activate evident-analyses

mkdir -p "data/agp"

CTX="Deblur_2021.09-Illumina-16S-V4-150nt-ac8c0b"
SAMPLE_FILE="data/agp/samples.txt"
TABLE="data/agp/table.biom"
MD="data/agp/metadata.tsv"

redbiom search metadata "where qiita_study_id == 10317" | \
    redbiom select samples-from-metadata --context $CTX "where sample_type in ('Stool', 'stool')" | \
    redbiom select samples-from-metadata --context $CTX "where sex in ('male', 'female')" | \
    redbiom select samples-from-metadata --context $CTX "where age_corrected >= 18" | \
    redbiom select samples-from-metadata --context $CTX "where age_corrected <= 70" | \
    redbiom select samples-from-metadata --context $CTX "where bmi <= 30" | \
    redbiom select samples-from-metadata --context $CTX "where bmi >= 18.5" > $SAMPLE_FILE

redbiom fetch samples --from $SAMPLE_FILE --context $CTX --output $TABLE
redbiom fetch sample-metadata --from $SAMPLE_FILE --context $CTX --output $MD
