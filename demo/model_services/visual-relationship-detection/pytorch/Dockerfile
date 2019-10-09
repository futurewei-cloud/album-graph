# Use Caffe2 image as parent image
#FROM caffe2/caffe2:snapshot-py2-cuda9.0-cudnn7-ubuntu16.04
FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
MAINTAINER vsochat@stanford.edu
# docker build -f Dockerfile.py2 -t vanessa/pytorch-dev:py2.7 .
# docker push vanessa/pytorch-dev:py2.7
RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         vim \
         ca-certificates \
         libjpeg-dev \
         libpng-dev &&\
     rm -rf /var/lib/apt/lists/*
ENV PYTHON_VERSION=2.7
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda config --add channels conda-forge && \
     /opt/conda/bin/conda install -y numpy pyyaml scipy ipython mkl && \
     /opt/conda/bin/conda install -y matplotlib scikit-learn scikit-image && \
     /opt/conda/bin/conda install -y typing && \
     /opt/conda/bin/conda install -c intel mkl-include && \
     /opt/conda/bin/conda install -c pytorch magma-cuda90 && \
     /opt/conda/bin/conda clean -ya
RUN /opt/conda/bin/conda update -y conda
ENV PATH /opt/conda/bin:$PATH
# torch 0.2.0
ADD torch-0.2.0.post3-cp27-cp27mu-manylinux1_x86_64.whl torch-0.2.0.post3-cp27-cp27mu-manylinux1_x86_64.whl 
RUN pip install torch-0.2.0.post3-cp27-cp27mu-manylinux1_x86_64.whl
ADD mxnet_cu80-1.4.0-py2.py3-none-manylinux1_x86_64.whl mxnet_cu80-1.4.0-py2.py3-none-manylinux1_x86_64.whl
RUN pip install mxnet_cu80-1.4.0-py2.py3-none-manylinux1_x86_64.whl
RUN apt-get update
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN pip install opencv-python
RUN conda install six=1.10.0
RUN conda install matplotlib=2.0.2
RUN apt-get install -y libgl1-mesa-glx


RUN git clone https://github.com/pytorch/vision.git --branch v0.1.8 /torchvision
# Install torchvision
WORKDIR /torchvision
RUN python setup.py install
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install -U numpy
RUN conda install -c conda-forge scikit-image
