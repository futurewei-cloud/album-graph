Model Service
====

The computer vision models and services to produce meta data for images.



Get Started
=====

Caveats: you may need to generate keys for accessing AWS services.

1. ag-aws-rekognition
```bash
sudo nvidia-docker build detectron -t detectron
sudo nvidia-docker build . -t ag-aws-rekognition
sudo nvidia-docker run -v /usr/local/cuda-8.0/lib64:/usr/local/cuda-8.0/lib64 \
	-e CUDA_VISIBLE_DEVICES=4 -e LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64 \
	-e AWS_ACCESS_KEY=AKIAIPGQU66D6R5T2QJQ \
	-e AWS_SECRET_ACCESS_KEY=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 \
	-p 8086:5000 ag-aws-rekognition
```

2. ag-face-detection
```bash
sudo nvidia-docker build mxnet -t mxnet
sudo nvidia-docker build . -t ag-face-detection
sudo nvidia-docker run -v /usr/local/cuda-8.0/lib64:/usr/local/cuda-8.0/lib64 \
	-e CUDA_VISIBLE_DEVICES=5 \
	-e LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64 \
	-p 8088:5000 ag-face-detection
```

3. ag-feature-extraction
```bash
sudo nvidia-docker build . -t ag-feature-extraction
sudo nvidia-docker run -v /usr/local/cuda-8.0/lib64:/usr/local/cuda-8.0/lib64 \
	-e CUDA_VISIBLE_DEVICES=5 \
	-e LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64 \
	-p 8084:5000 ag-feature-extraction
```

4. ag-oic-object-detection
```bash
sudo nvidia-docker build . -t ag-oic-object-detection
sudo nvidia-docker run -v /usr/local/cuda-8.0/lib64:/usr/local/cuda-8.0/lib64 \
	-e CUDA_VISIBLE_DEVICES=5 \
	-e LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64 \
	-p 8085:5000 ag-oic-object-detection
```

5. ag-visual-relationship-detection
```bash
sudo nvidia-docker build pytorch -t pytorch
sudo nvidia-docker build . -t ag-visual-relationship-detection
sudo nvidia-docker run -v ~/workspace/vrd-dsr/models:/app/models \
	-v /usr/local/cuda-8.0/lib64:/usr/local/cuda-8.0/lib64 \
	-e CUDA_VISIBLE_DEVICES=6 \
	-e LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64 \
	-p 8087:5000 ag-visual-relationship-detection
```

6. ag-perceptron
```bash
sudo nvidia-docker build . -t ag-perceptron
sudo nvidia-docker run \
	-v /home/mingweihe/workspace/model_services/perceptron/logs:/logs \
	-p 80:5000 ag-perceptron
```
