#!/bin/bash
#Preprocess:dicom to nifty and registration

#loading all the env parameters in the crontab
scriptPath=$(dirname "$(readlink -f "$0")")
source "${scriptPath}/.env.sh"

#activate conda environment
source /opt/miniconda-latest/etc/profile.d/conda.sh
conda activate neuro

dt=$(date '+%d/%m/%Y %H:%M:%S')
today=$(date --date="0 days ago" "+%Y-%m-%d")

#log files
LOGDIR=/app/logs
LOG=/app/logs/brats.log
SKYNETLOG=/app/logs/skynet.log
#create the log files by date
LOGTODAY=$LOGDIR/$today
mkdir -p $LOGTODAY
TOTAL=$LOGTODAY/brats_total.log
SUCCESSED=$LOGTODAY/brats_successed.log
FAILED=$LOGTODAY/brats_failed.log

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
  if (grep -qi $FILENAME $SUCCESSED) || (grep -qi $FILENAME $FAILED)
  then 
	  echo "Already tried to process ${FILENAME}"
	  continue
  elif [ ! -d ${FILENAME}/t1ce ] || [ ! -d ${FILENAME}/flair ] || [ ! -d ${FILENAME}/t2 ] || [ ! -d ${FILENAME}/t1 ] 
  then
	  printf "${FILENAME}  missing one of 4 series, i.e t1,t1ce,t2,flair    ${dt}\n" >> $TOTAL
	  continue
  #tried to preprocessed but failed
  elif [ -d ${FILENAME}/nifti ] && [ ! -f ${FILENAME}/nifti/*_brain_t1ce.nii.gz ]
  then
          printf "Tried to segment ${FILENAME} but failed due to preprocess    ${dt}\n" >> $FAILED
          continue
  elif [ -f ${FILENAME}/nifti/*_brain_t1ce.nii.gz ] 
  then
          printf "Tried to segment ${FILENAME} but no tumor was detected    ${dt}\n" >> $FAILED
          continue
  else
     #get and create the path of processed and segmented dicoms
     PROCESSED=${FILENAME/incoming/processed}
     mkdir -p $PROCESSED
     chmod -R 777 $PROCESSED
     echo "Detected $FILENAME, Brain Tumor Segmentation Pipeline starts"
     echo "Step 1, Coregistration & Skull Striping"
     printf "${FILENAME}    ${dt}\n" >> $TOTAL
     #exec python $PYTHONSCRIPT --input=${FILENAME} 
     #python $PYTHONSCRIPT --input=${FILENAME} && ssh $SSH_USER@$SSH_SERVER sh <<- EOF && /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 $PROCESSED/t1ce && /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 $PROCESSED/flair && exec printf "Processed ${FILENAME} sucessfully    ${dt}\n" >> $SUCCESSED
     python $PYTHONSCRIPT --input=${FILENAME} && ssh $SSH_USER@$SSH_SERVER sh <<- EOF && exec printf "Processed ${FILENAME} sucessfully    ${dt}\n" >> $SUCCESSED
     						set -xe;
						cd $SSH_FOLDER;
						set +x;  echo "Performing segmentation...";
						#cp -r /gpfs/data/luilab/BRATS/data/incoming/${FILENAME##*/} /gpfs/data/luilab/BRATS/data_bak/incoming/;
                                                #use parameter expansion to get the new folder's path
                                                FILENAME_hpc=${FILENAME/app/gpfs/data/luilab/BRATS};
                                                FILENAME_processed=\${FILENAME_hpc/incoming/processed};
                                                FILENAME_processed=\${FILENAME_processed%/*};
                                                FILENAME_bak=\${FILENAME_hpc/BRATS\/data/BRATS/data_bak};
                                                parentdir=\${FILENAME_bak%/*};
                                                FILENAME_bak_processed=\${FILENAME_bak/incoming/processed};
                                                echo \$FILENAME_hpc \$FILENAME_processed \$FILENAME_bak \$parentdir \$FILENAME_bak_processed;
                                                mkdir -p \$FILENAME_bak_processed;
                                                mkdir -p  \$parentdir;
					        cp -r \$FILENAME_hpc \$parentdir;
                                                sleep 30;
						while [ ! -d \$FILENAME_bak/nifti ]
						do
							echo "Waiting copy process to be finished"
							sleep 5
						done;	
						bsub -K -n 1 -q short \
							-o logs/brats_%J.log \
							-gpu "gtile=1:num=1:mode=shared:j_exclusive=yes" \
							sh skullstripping_seg.sh \$FILENAME_bak \$FILENAME_bak_processed; 
                                                #/gpfs/data/luilab/BRATS/data_bak/processed/ is a tempt folder
						while [ ! -d \$FILENAME_bak_processed/t1ce ] || 
							[ ! -d \$FILENAME_bak_processed/flair ]
					        do
							echo "Waiting Segmentation and Post-process to be finished"
							sleep 5
					       	done
						echo "Converted nifti to dicom";
						cp -r \$FILENAME_bak_processed \$FILENAME_processed;
						EOF
						#&& exec /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /gpfs/data/luilab/BRATS/data_bak/processed/${FILENAME##*/}/t1ce
	#printf "Processed ${FILENAME} sucessfully\n" >> $SUCCESSED
  fi
done
#&& exec /app/dcm4che-5.22.6/bin/storescu -c RESEARCH@10.147.124.19:104 /app/data/processed/${FILENAME##*/}/t1ce
