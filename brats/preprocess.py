##!usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import nipype.interfaces.fsl as fsl
import shutil
import multiprocessing
import time
import glob
import nibabel
import numpy as np
import SimpleITK as sitk
import sys

class Preprocessor:
    def __init__(self, input_dir, num_workers, antsBrainExtraction,template_dir):
        self.input_dir = input_dir
        self.num_workers = num_workers
        self.acc = os.path.basename(self.input_dir)
        self.antsBrainExtraction = antsBrainExtraction
        self.template_dir = template_dir
        self.modelities = ['t1.nii.gz','t1ce.nii.gz','t2.nii.gz','flair.nii.gz']
        #create a folder for nifti files
        self.nifti_dir = os.path.join(self.input_dir, 'nifti')
        if os.path.exists(self.nifti_dir):
            shutil.rmtree(self.nifti_dir)
        os.makedirs(self.nifti_dir,exist_ok=True)
           
    def dicom2nifti(self):
        print(f'\nCovert Dicom to nifti, access_num: {self.acc}')                         
        """
        Compress dicoms to nifty files
        """

        if not os.path.isdir(self.input_dir):
            raise ValueError(f'Dataset directory {self.input_dir} does not exist')
        print("Start to compress dicoms to nifty files...")
        for subf in glob.glob(self.input_dir + '/*'):
            if os.path.isdir(subf) and os.path.basename(subf) in ['t1','t1ce','t2','flair']:
                os.system("dcm2niix -o {} -z y -f %f {}".format(self.nifti_dir, subf))
        os.system("rm {}/*.json".format(self.nifti_dir))
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
    #@staticmethod
    #def coregistration(args_list):
    #    nifty_input = args_list[0]
    #    ref = args_list[1]
    #    nifty_output = args_list[2]
    #    os.system("flirt -in {} -ref {} -dof 6 -cost mutualinfo -out {}".format(nifty_input, ref, nifty_output))
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
                nifty_coreg_input = file
                nifty_coreg_output = file.replace('.nii.gz', '_coreg.nii.gz')
                args_list.append([nifty_coreg_input, t1ce_dir, nifty_coreg_output])
        print(args_list)
        pool.map(self.coregistration, args_list)
        t1ce_coreg_dir = t1ce_dir.replace('.nii.gz','_coreg.nii.gz')
        os.system("cp {} {}".format(t1ce_dir, t1ce_coreg_dir))


    def skullstripping_ants(self):
        """
        Skull stripping by ANTs
        """
        print("Skull strip by ANTs...")
        temp_dir = os.path.join(self.nifti_dir, 'temp')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        T1CE_skull_dir = os.path.join(self.nifti_dir, 't1_coreg.nii.gz')

        subprocess.call(f"{self.antsBrainExtraction} "
            f"-d 3 "
            f"-a {T1CE_skull_dir} "
            f"-e {os.path.join(self.template_dir, 'LPBA40_Template_n2.nii')} "
            f"-m {os.path.join(self.template_dir, 'LPBA40_mask_n2.nii')} "
            f"-o {os.path.join(temp_dir, 'temp_')}",  shell=True)

        T1CE_mask = os.path.join(temp_dir, 'temp_BrainExtractionMask.nii.gz')
        # T1CE_brain = os.path.join(temp_dir, 'temp_BrainExtractionBrain.nii.gz')
        mask = self.load_nifty_volume_as_array(T1CE_mask, with_header = False)
        for file in os.listdir(self.nifti_dir):
            if '_coreg' in file:
                nifty_withskull_dir = os.path.join(self.nifti_dir, file)
                nifty_withskull = self.load_nifty_volume_as_array(nifty_withskull_dir, with_header = False)
                nifty_withskull[mask == 0] = 0
                nifty_brain_dir = os.path.join(self.nifti_dir, file.replace('.nii','') + '_brain.nii.gz' )
                self.save_array_as_nifty_volume(nifty_withskull, nifty_brain_dir, nifty_withskull_dir)

        #Rename the proprocessed files and remove redundant files
        access_num = os.path.basename(self.input_dir)
        for file in os.listdir(self.nifti_dir):
            if file.replace('.nii.gz','').endswith('brain'):
                old_dir = os.path.join(self.nifti_dir, file)
                if 't1ce' in file:
                    new_file = access_num + '_brain_t1ce.nii.gz'
                elif 't1' in file:
                    new_file = access_num + '_brain_t1.nii.gz'
                elif 't2' in file:
                    new_file = access_num + '_brain_t2.nii.gz'
                else:
                    new_file = access_num + '_brain_flair.nii.gz'

                new_dir = os.path.join(self.nifti_dir,new_file)
                os.rename(old_dir, new_dir)

        shutil.rmtree(temp_dir)


    @staticmethod
    def load_nifty_volume_as_array(filename, with_header = False):
        """
        load nifty image into numpy array, and transpose it based on the [z,y,x] axis order
        The output array shape is like [Depth, Height, Width]
        inputs:
            filename: the input file name, should be *.nii or *.nii.gz
            with_header: return affine and hearder infomation
        outputs:
            data: a numpy data array
        """
        img = nibabel.load(filename)
        data = img.get_fdata()
        data = np.transpose(data, [2,1,0])
        if(with_header):
            return data, img.affine, img.header
        else:
            return data

    @staticmethod
    def save_array_as_nifty_volume(data, filename, reference_name = None):
        """
        save a numpy array as nifty image
        inputs:
            data: a numpy array with shape [Depth, Height, Width]
            filename: the ouput file name
            reference_name: file name of the reference image of which affine and header are used
        outputs: None
        """
        img = sitk.GetImageFromArray(data)
        if(reference_name is not None):
            img_ref = sitk.ReadImage(reference_name)
            img.CopyInformation(img_ref)
        sitk.WriteImage(img, filename)
     
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Skull Stripping Pipeline')
    parser.add_argument('-i', '--input', type=str, default='/app/data/incoming/acc',
            help='location of the original dicom files, which has at least one unique access_num folder with subfolder t1ce, t1, t2, flair')
    parser.add_argument('-n', '--num_workers', type=int, default=3, help='Number of workers')
    parser.add_argument('-ants','--ants_path', type=str, default='/app/antsBrainExtraction/antsBrainExtraction.sh',
            help='location of antsBrainExtraction.sh')
    parser.add_argument('-t','--template_dir', type=str, default='/app/antsBrainExtraction/Template',
            help='location of antsBrainExtraction template')

    args = parser.parse_args()
    print(args)
    if not os.path.exists(args.input):
        print('Input folder not exists')
        exit()
    #check 4 series are all in the input_dir
    for i in ['t1','t1ce','t2','flair']:
        print(os.listdir(args.input))
        if not i in os.listdir(args.input):
            print(f'{i} series is missing; Job stopped')
            exit()
    #dicom to nifti, coregisteration
    one_acc = Preprocessor(args.input, args.num_workers,args.ants_path, args.template_dir)
    one_acc.dicom2nifti()
    one_acc.coregisteration_pool()
    one_acc.skullstripping_ants()

    # inputs.append((dicom_dir,output_dir,args.ants_path, args.template_dir, args.nifti_dirs))

    # #todo: write codes for multiple cases coming
