#!/bin/bash
#Preprocess:dicom to nifty and registration

#loading all the env parameters in the crontab
scriptPath=$(dirname "$(readlink -f "$0")")
source "${scriptPath}/.env.sh"

#activate conda environment
source /opt/miniconda-latest/etc/profile.d/conda.sh
conda activate neuro

MONITORDIR=/app/data/incoming
TOTAL=/app/logs/brats_total.log
LOG=/app/logs/brats.log
SUCCESSED=/app/logs/brats_successed.log
SUCCESSED_flair=/app/logs/brats_successed_flair.log
SKYNETLOG=/app/logs/skynet.log
PROCESSED=/app/data/processed/
PYTHONSCRIPT=/app/preprocess.py
SSH_USER=${SSH_USER:-bz957}
SSH_SERVER=${SSH_SERVER:-skynet.nyumc.org}
SSH_FOLDER=${SSH_FOLDER:-/gpfs/data/luilab/BRATS}

#loop over the MONITORDIR 
for FILENAME in $MONITORDIR/*
do
  if (grep -qi $FILENAME $SUCCESSED_flair)
  then
	  echo "Already sent segmentation with flair background"
	  continue
  elif (grep -qi $FILENAME $SUCCESSED)
  then 
	  echo "Send segmentation with flair background ${FILENAME}"
	  /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /app/data/processed/${FILENAME##*/}/flair && exec printf "Processed ${FILENAME} sucessfully\n" >> $SUCCESSED_flair
  else
	  continue
  fi
done
