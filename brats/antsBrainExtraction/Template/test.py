#!/Users/zhangben/anaconda/bin/python
# encoding: utf-8
import argparse
import os
import numpy as np
import nibabel
import SimpleITK as sitk
import subprocess
import shutil

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
    # data = np.transpose(data, [2,1,0])
    if(with_header):
        return img, data, img.affine, img.header
    else:
        return data

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

nifty_withskull_dir = '/Users/zhangben/Desktop/github/brats17/pipeline/antsBrainExtraction/Template/LPBA40_Template.nii'
nifty_withskull, data, affine, header = load_nifty_volume_as_array(nifty_withskull_dir, with_header = True)
print(header)
# header.set_dim_info(175, 124, 256)
data_new = data[34:224,:,44:234]
print(data_new.shape)
nifty_brain_dir = '/Users/zhangben/Desktop/github/brats17/pipeline/antsBrainExtraction/Template/LPBA40_Template_n2.nii'
# clipped_img = nibabel.Nifti1Image(data_new, affine, header)
# print(clipped_img.header.get_data_shape())
# nibabel.save(clipped_img, 'clipped_image.nii')

nibabel.save(nifty_withskull.__class__(data_new, affine, header), nifty_brain_dir)
# save_array_as_nifty_volume(nifty_withskull_new, nifty_brain_dir, nifty_withskull_dir)