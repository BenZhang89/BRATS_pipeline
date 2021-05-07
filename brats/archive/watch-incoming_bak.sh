#!/bin/bash
#Preprocess:dicom to nifty and registration
echo "$(pwd)" >> /var/log/brats.log
source /opt/miniconda-latest/etc/profile.d/conda.sh
conda activate neuro
#python preprocess.py --input='./data/incoming/10124132'
#conda deactivate

MONITORDIR=/app/data/incoming_test/
PROCESSED=/app/data/processed/
set -xe
SSH_USER=${SSH_USER:-bz957}
SSH_SERVER=${SSH_SERVER:-skynet.nyumc.org}
SSH_FOLDER=${SSH_FOLDER:-/gpfs/data/luilab/BRATS}

inotifywait -m -e create -e moved_to --format "%f" $MONITORDIR | while read FILENAME
    do  echo "Detected ${FILENAME}, Brain Tumor Segmentation Pipeline starts"
        echo "Step 1, Coregistration & Skull Striping"
        exec python preprocess.py --input="/app/data/incoming_test/${FILENAME}"	
        exec ssh $SSH_USER@$SSH_SERVER sh <<-EOF
		set -xe;
		cd $SSH_FOLDER;
		set +x;  echo "Performing segmentation...";
		bsub -K -n 5 -q inference \
			-o logs/brats_%J.log \
			-gpu "gtile=2:num=4:mode=shared:j_exclusive=yes" \
			sh skullstripping_seg.sh "data/incoming_test/$FILENAME"  "data/processed/$FILENAME";
		EOF
    done
