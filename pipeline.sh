#!/bin/bash

cd /home/grahman/projects/evident-analyses

# Download raw data
jid1=$(sbatch scripts/0.01-download_data.sh | grep -oP "\d*")

# Disambguate raw data
jid2=$(sbatch --dependency=afterok:$jid1 scripts/1.01-disambiguate.py | grep -oP "\d*")

# Filter disambiguated data
jid3=$(sbatch --dependency=afterok:$jid2 scripts/2.01-filter_data.py | grep -oP "\d*")

# Run SEPP
jid4=$(sbatch --dependency=afterok:$jid3 scripts/3.01-sepp.sh | grep -oP "\d*")

# Run unweighted UniFrac
jid5=$(sbatch --dependency=afterok:$jid4 scripts/4.01-u_unifrac.py | grep -oP "\d*")

# Run evident analyses
jid6=$(sbatch --dependency=afterok:$jid5 scripts/5.01-evident_effect_sizes.py | grep -oP "\d*")
jid7=$(sbatch --dependency=afterok:$jid5 scripts/5.02-evident_effect_sizes_pairwise.py | grep -oP "\d*")
jid8=$(sbatch --dependency=afterok:$jid5 scripts/5.03-evident_power_analysis.py | grep -oP "\d*")

squeue -u grahman -o "%.8A %.4C %.10m %.20E"
