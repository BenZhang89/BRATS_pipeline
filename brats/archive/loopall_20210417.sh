#!/bin/bash
#Preprocess:dicom to nifty and registration

#loading all the env parameters in the crontab
scriptPath=$(dirname "$(readlink -f "$0")")
source "${scriptPath}/.env.sh"

#activate conda environment
source /opt/miniconda-latest/etc/profile.d/conda.sh
conda activate neuro

dt=$(date '+%d/%m/%Y %H:%M:%S')
today=$(date '+%Y-%m-%d')

#log files
LOGDIR=/app/logs
LOG=/app/logs/brats.log
SKYNETLOG=/app/logs/skynet.log
#create the log files by date
LOGTODAY=$LOGDIR/$today
mkdir -p $LOGTODAY
TOTAL=$LOGTODAY/brats_total.log
SUCCESSED=$LOGTODAY/brats_successed.log

MONITORDIR=/app/data/incoming
#PROCESSED=/app/data/processed/
PYTHONSCRIPT=/app/preprocess.py

SSH_USER=${SSH_USER:-bz957}
SSH_SERVER=${SSH_SERVER:-skynet.nyumc.org}
SSH_FOLDER=${SSH_FOLDER:-/gpfs/data/luilab/BRATS}

#loop over the MONITORDIR 
#if a file already is completed or tried once but received more dicom series
for FILENAME in $MONITORDIR/*/$today/*
do
  #if  ( $(grep -qi $FILENAME $TOTAL)  && [ $(( ($(date +%s) - $(date -r $FILENAME '+%s') )/(60*60) )) -gt 1 ] )  ||  (grep -qi $FILENAME $SUCCESSED)
  #if  ( $(grep -qi $FILENAME $TOTAL)  && ( [ ! -d ${FILENAME}/t1ce ] || [ ! -d ${FILENAME}/flair ] || [ ! -d ${FILENAME}/t2 ] || [ ! -d ${FILENAME}/t1 ] ) ) ||  (grep -qi $FILENAME $SUCCESSED)
  #if  (grep -qi $FILENAME $TOTAL) || (grep -qi $FILENAME $SUCCESSED)
  if (grep -qi $FILENAME $SUCCESSED)
  then 
	  echo "Already tried to process ${FILENAME}"
	  continue
  elif [ ! -d ${FILENAME}/t1ce ] || [ ! -d ${FILENAME}/flair ] || [ ! -d ${FILENAME}/t2 ] || [ ! -d ${FILENAME}/t1 ] 
  then
	  printf "${FILENAME}  missing one of 4 series, i.e t1,t1ce,t2,flair    ${dt}\n" >> $TOTAL
	  continue
  else
     #get and create the path of processed and segmented dicoms
     PROCESSED=${FILENAME/incoming/processed}
     mkdir -p $PROCESSED
     echo "Detected $FILENAME, Brain Tumor Segmentation Pipeline starts"
     echo "Step 1, Coregistration & Skull Striping"
     printf "${FILENAME}    ${dt}\n" >> $TOTAL
     #exec python $PYTHONSCRIPT --input=${FILENAME} 
     python $PYTHONSCRIPT --input=${FILENAME} && ssh $SSH_USER@$SSH_SERVER sh <<- EOF && /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /app/data/processed/${FILENAME##*/}/t1ce && /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /app/data/processed/${FILENAME##*/}/flair && exec printf "Processed ${FILENAME} sucessfully    ${dt}\n" >> $SUCCESSED
     						set -xe;
						cd $SSH_FOLDER;
						set +x;  echo "Performing segmentation...";
						#cp -r /gpfs/data/luilab/BRATS/data/incoming/${FILENAME##*/} /gpfs/data/luilab/BRATS/data_bak/incoming/;
                                                FILENAME=${FILENAME/app/gpfs/data/luilab/BRATS};
                                                FILENAME_bak=${FILENAME/%data/data_bak};
                                                parentdir="$(dirname "$FILENAME_bak")";
                                                mkdir -p $parentdir;
					        cp -r $FILENAME $FILENAME_bak;
                                                sleep 30;
						while [ ! -d /gpfs/data/luilab/BRATS/data_bak/incoming/${FILENAME##*/}/nifti ]
						do
							echo "Waiting copy process to be finished"
							sleep 5
						done;	
						bsub -K -n 5 -q inference \
							-o logs/brats_%J.log \
							-gpu "gtile=2:num=4:mode=shared:j_exclusive=yes" \
							sh skullstripping_seg.sh "/gpfs/data/luilab/BRATS/data_bak/incoming/${FILENAME##*/}" "/gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}";
						while [ ! -d /gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}/t1ce ] || 
							[ ! -d /gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}/flair ]
					        do
							echo "Waiting Segmentation and Post-process to be finished"
							sleep 5
					       	done
						echo "Converted nifti to dicom";
						cp -r "/gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}" "/gpfs/data/luilab/BRATS/data/processed/";
						EOF
						#&& exec /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}/t1ce
	#printf "Processed ${FILENAME} sucessfully\n" >> $SUCCESSED
  fi
done
#&& exec /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /app/data/processed/${FILENAME##*/}/t1ce
