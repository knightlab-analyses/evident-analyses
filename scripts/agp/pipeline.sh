#!/bin/bash

cd /home/grahman/projects/evident-analyses/scripts/agp

jid1=$(sbatch ./0.01-download_data.sh | grep -oP "\d*")
jid2=$(sbatch --dependency=afterok:$jid1 ./1.01-filter_data.py | grep -oP "\d*")

squeue -u grahman -o "%.8A %.4C %.10m %.20E"
