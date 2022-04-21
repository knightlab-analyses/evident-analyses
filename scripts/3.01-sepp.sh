#!/usr/bin/bash
#SBATCH --chdir=/home/grahman/projects/evident-analyses
#SBATCH --output=/home/grahman/projects/evident-analyses/log/%x.log
#SBATCH --partition=long
#SBATCH --nodes=8
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=16G
#SBATCH --time=24:00:00

echo "[ $(date) ] :: Start script"
date; pwd; hostname

source ~/miniconda3/bin/activate evident-analyses

TBL="data/processed/table.disambig.rare.filt.biom"
FNA=$(realpath "data/processed/seqs.fna")
python -c "import biom; t = biom.load_table('$TBL'); f = open('$FNA', 'w'); f.write(''.join(['>%s\n%s\n' % (i, i.upper()) for i in t.ids(axis='observation')]))"

SEPP="/home/grahman/software/sepp-package/run-sepp.sh"

OUTDIR="results/sepp_out"
mkdir -p $OUTDIR
cd $OUTDIR

echo "[ $(date) ] :: Running SEPP..."

$SEPP $FNA tbl_gg -x 64

echo "[ $(date) ] :: Finished script!"
