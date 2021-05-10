# Pipeline of Brain Tumor Segmentation

This is a practical implementation of a deep learning-based pipeline for automated pre- and postoperative glioma segmentation. 

## Description
Accurate segmentation of tumor sub-regions (enhancement, edema) can offer the basis for quantitative image analysis towards precision medicine and improvements in individual prognostication. Bringing such tools to clinical reality requires thoughtful implementation. We describe the components required towards clinical deployment of a deep learning-based glioma segmentation model.

### An end-to-end pipeline
We create a pipeline which can route brain tumor DICOM, automate the segmentation algorithm, and push quantitative results back for clinical viewing. This pipeline is composed of 2 servers:
* Data Transit Server:
Receive brain tumor DICOM + push processed DICOM back to PACS
* Inference Server:
(1) pre-processor; 
(2) segmentation ; 
(3) post-processor. A result incorporating segmentation visualization and volumetrics is routed to the clinical PACS environment.

![](https://github.com/abenpy/BRATS_pipeline/blob/master/png/pipeline-1.png?raw=true)

### Detailed introduction about Data Transit Server
![](https://github.com/abenpy/BRATS_pipeline/blob/master/png/pipeline-2.png?raw=true)
An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
