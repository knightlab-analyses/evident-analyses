#!/bin/bash

cd /home/grahman/projects/evident-analyses/scripts/agp

jid1=$(sbatch ./1.01-filter_data.py | grep -oP "\d*")

jid2=$(sbatch --dependency=afterok:$jid1 ./2.01-rpca.sh | grep -oP "\d*")
jid3=$(sbatch --dependency=afterok:$jid1 ./2.02-process_metadata.py | grep -oP "\d*")

jid4=$(sbatch --dependency=afterok:$jid2:$jid3 ./3.01-evident_effect_sizes.py | grep -oP "\d*")
jid5=$(sbatch --dependency=afterok:$jid2:$jid3 ./3.02-evident_effect_sizes_pairwise.py | grep -oP "\d*")
jid6=$(sbatch --dependency=afterok:$jid2:$jid3 ./3.03-evident_power_analysis.py | grep -oP "\d*")
jid7=$(sbatch --dependency=afterok:$jid2:$jid3 ./3.04-evident_power_analysis_pairwise.py | grep -oP "\d*")

squeue -u grahman -o "%.8A %.4C %.10m %.20E"
