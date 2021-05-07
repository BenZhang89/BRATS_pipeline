#!/bin/bash
#Preprocess:dicom to nifty and registration

#loading all the env parameters in the crontab
scriptPath=$(dirname "$(readlink -f "$0")")
source "${scriptPath}/.env.sh"

TOTAL=/app/brats/logs/brats_total.log
LOG=/app/logs/brats.log
SUCCESSED=/app/brats/logs/brats_successed.log
SKYNETLOG=/app/logs/skynet.log
PYTHONSCRIPT=/app/preprocess.py
SSH_USER=${SSH_USER:-bz957}
SSH_SERVER=${SSH_SERVER:-skynet.nyumc.org}
SSH_FOLDER=${SSH_FOLDER:-/gpfs/data/luilab/BRATS}

#loop over the MONITORDIR
dt=$(date '+%d/%m/%Y %H:%M:%S')
for FILENAME in ./*
do
  echo ${FILENAME#./}
  #if ( $(grep -qi ${FILENAME#./} $TOTAL) || $(grep -qi $FILENAME $SUCCESSED) )
  #then
  #       echo "part satisfied"
  if  ( $(grep -qi ${FILENAME#./} $TOTAL)  && [ $(( ($(date +%s) - $(date -r $FILENAME '+%s') )/(60*60) )) -gt 1 ] )  ||  (grep -qi $FILENAME $SUCCESSED)
  then
          test=$(( ($(date +%s) - $(date -r $FILENAME '+%s') )/(60*60) ))
          echo $test
          echo "Already tried to process ${FILENAME}"
  else
          echo "new"
  fi
done
~      
