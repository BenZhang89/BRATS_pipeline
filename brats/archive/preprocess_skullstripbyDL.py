# -*- coding: utf-8 -*-
import argparse
import os
import nipype.interfaces.fsl as fsl
import shutil
import multiprocessing
import time
import glob

class Preprocessor:
    def __init__(self, input_dir, num_workers):
        self.input_dir = input_dir
        self.num_workers = num_workers
        self.acc = os.path.basename(self.input_dir)
        self.modelities = ['t1.nii.gz','t1ce.nii.gz','t2.nii.gz','flair.nii.gz']

    def dicom2nifti(self):
        print(f'\nCovert Dicom to nifti, access_num: {self.acc}')                         
        """
        Compress dicoms to nifty files
        """
        temp_dir = os.path.join(self.input_dir, 'nifti')

        if not os.path.isdir(self.input_dir):
            raise ValueError(f'Dataset directory {self.input_dir} does not exist')

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        print("Start to compress dicoms to nifty files...")
        for subf in glob.glob(self.input_dir + '/*'):
            if os.path.isdir(subf) and not subf.startswith('nifti'):
                os.system("dcm2niix -o {} -z y -f %f {}".format(temp_dir, subf))
        os.system("rm {}/*.json".format(temp_dir))
    #using fsl
    @staticmethod 
    def coregistration(args_list):
        applyxfm = fsl.preprocess.ApplyXFM()
        applyxfm.inputs.in_file = args_list[0]
        applyxfm.inputs.reference = args_list[1]

        applyxfm.inputs.out_file = args_list[0].replace(".nii.gz", "_coreg.nii.gz")
        applyxfm.inputs.uses_qform = True

        applyxfm.inputs.cost = 'mutualinfo'
        applyxfm.inputs.dof = 6
        result = applyxfm.run() 


    def coregisteration_pool(self):
        """
        Coregistration with Skulls, using flair as benchmark
        """
        #Find t1ce.nii.gz
        t1ce_dir = os.path.join(self.input_dir,'nifti','t1ce.nii.gz')
        assert (os.path.isfile(t1ce_dir))

        #multiprocess for each Nifty files
        print(f'Start the coregistration case {self.acc}...')
        pool = multiprocessing.Pool(self.num_workers)
        args_list = []
        for file in glob.glob(self.input_dir + '/nifti/*'):
            if os.path.basename(file) in self.modelities:
                nifty_coreg_input = nifty_coreg_output = file
                args_list.append([nifty_coreg_input, t1ce_dir])
        print(args_list)
        pool.map(self.coregistration, args_list)
        t1ce_coreg_dir = t1ce_dir.replace('.nii.gz','_coreg.nii.gz')
        os.system("cp {} {}".format(t1ce_dir, t1ce_coreg_dir))
     
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Skull Stripping Pipeline')
    parser.add_argument('-i', '--input', type=str, default='/gpfs/data/luilab/BRATS/data/incoming',
        help='location of the original dicom files, which has at least one unique access_num folder with subfolder t1ce, t1, t2, flair')
    parser.add_argument('-n', '--num_workers', type=int, default=3, help='Number of workers')

    args = parser.parse_args()
    print(args)
    if not os.path.exists(args.input):
        print('Input folder not exists')
        exit()

    #dicom to nifti, coregisteration
    one_acc = Preprocessor(args.input, args.num_workers)
    one_acc.dicom2nifti()
    one_acc.coregisteration_pool()
    
    # inputs.append((dicom_dir,output_dir,args.ants_path, args.template_dir, args.nifti_dirs))

    # #todo: write codes for multiple cases coming
