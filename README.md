# Pipeline of Brain Tumor Segmentation

This is a practical implementation of a deep learning-based pipeline for automated pre- and postoperative glioma segmentation. 

## Description
Accurate segmentation of tumor sub-regions (enhancement, edema) can offer the basis for quantitative image analysis towards precision medicine and improvements in individual prognostication. Bringing such tools to clinical reality requires thoughtful implementation. We describe the components required towards clinical deployment of a deep learning-based glioma segmentation model.

### An end-to-end pipeline
We create a pipeline which can route brain tumor DICOM, automate the segmentation algorithm, and push quantitative results back for clinical viewing. This pipeline is composed of 2 servers:
* **Data Transit Server:**
Receive brain tumor DICOM + filter the right input series + push processed DICOM back to PACS
* **Inference Server:**
  This server is composed of 3 modules, i.e. (1) pre-processor (2) segmentation (3) post-processor. The deep learning model used in the pipeline can be found here:https://github.com/abenpy/ARCNet. A result incorporating segmentation visualization and volumetrics is routed to the clinical PACS environment.

![](https://github.com/abenpy/BRATS_pipeline/blob/master/png/pipeline-1.png?raw=true)

### Detailed introduction about Data Transit Server
We deployed 4 docker containers with daily logs: 
* **Pre-OP Receiver:** receive DICOM using “pynetdicom”
    * Rules: this docker will receive any DICOM sending to it. So the rules should be set from the sending side, i.e the Vendor Neural Archive, which is not included in this git repository. The DICOM series should be like BraTs inputs(https://www.med.upenn.edu/sbia/brats2018/data.html). We suggested to changing is accordingly due to the different naming convention in different organizations. Rules for pre-op receiver in our organisation is: brain tumor protocol; study descriptions ends in Head; study descriptions contains “AX T1 PRE”, “AX T2”, ”SAG 3D FLAIR”, ”SAG MPR” etc.
    * Due to the storage limitation, currently keep only one week original DICOM files.
* **Post-OP Receiver:** receive DICOM using “pynetdicom”
    * Rules: same logic as pre-op receiver. Rules for pre-op receiver in our organisation is:brain tumor protocol; study descriptions ends in Head; study descriptions contains “PERFUSION”(a key series to identify the follow-up/post-op studies), “AX T1 PRE”, “AX T2”, ”SAG 3D FLAIR”, ”SAG MPR” etc.
    * Due to the storage limitation, currently keep only one week original DICOM files.
* **DICOM Filter:** 
    * Setting filter rules to select studies with all the 4 input series only, and rename it in BraTs convention, i.e. t1ce, t1, t2, flair. Exclude study which misses any of t1ce, t1, t2, flair.
* **DICOM Sender:** push processed DICOM back to PACS, using “dcm4che”.(currently was encapusated in Inference Server)

![](https://github.com/abenpy/BRATS_pipeline/blob/master/png/pipeline-2.png?raw=true)

### Template of View in PACS


## Getting Started

### Dependencies

* Docker
* GPU for Inference Server

### Installing and set up the server

* Pre-OP Receiver: 
    * docker-compose build brats_receive_mri/docker/preop/docker-compose.yml
    * docker-compose up -d
* Post-OP Receiver: 
    * docker-compose build brats_receive_mri/docker/postop/docker-compose.yml
    * docker-compose up -d
* DICOM Filter: 
    * docker-compose build brats_filter/docker/docker-compose.yml
    * docker-compose up -d
* Inference Server:
    * generate Dockerfile: bash brats/docker/generate_dockerfile.sh. Using **neurodocker:0.7.0** to generate a customized Dockerfile which including "fsl", "ants", "dcm2niix". Refer to https://github.com/ReproNim/neurodocker to get more information about "neurodocker".
    * docker-compose build brats/docker-compose.yml
    * docker-compose up -d


## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

Ben Zhang [dongshangshi@gmail.com]

## Version History

* 0.1
    * Initial Release

## Acknowledgments

Inspiration, code snippets, etc.
* [CACNN](https://github.com/taigw/brats17)
* [Third Party implementation of 1st BraTs 2018](https://github.com/black0017/MedicalZooPytorch)
* [neurodocker](https://github.com/ReproNim/neurodocker)
