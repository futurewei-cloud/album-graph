# Use Caffe2 image as parent image
#FROM caffe2/caffe2:snapshot-py2-cuda9.0-cudnn7-ubuntu16.04
FROM pytorch
COPY . /app
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["app.py"]
