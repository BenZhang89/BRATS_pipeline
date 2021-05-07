docker run --rm repronim/neurodocker:0.7.0 generate docker \
           --base debian:stretch --pkg-manager apt \
           --install git vim inotify-tools cron dcmtk \
           --dcm2niix  method=source version=latest \
           --fsl version=5.0.10 \
	   --ants version=2.3.0 \
           --miniconda create_env=neuro \
                       conda_install="python=3.6 traits" \
                       pip_install="nipype"  > Dockerfile

#--fsl version=5.0.10
