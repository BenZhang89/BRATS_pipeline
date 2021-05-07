#!/bin/bash
#Preprocess:dicom to nifty and registration

#loading all the env parameters in the crontab
scriptPath=$(dirname "$(readlink -f "$0")")
source "${scriptPath}/.env.sh"
PYTHONSCRIPT=/app/filter.py
python $PYTHONSCRIPT 
