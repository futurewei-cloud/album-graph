1. 依赖

   - opencv
   - cudnn
   - mxnet
   - cuda

2. 运行方式

   python extract_features.py

   参数含义：

   --image-size  人脸识别网络输入大小，不需要修改

   --model		人脸识别模型路径

   --gpu		gpu参数

   --det		MTCNN检测是否采用金字塔方式（PNET），0表示采用，详情参考mtcnn_detector.py 	

   ​			detect_face函数

   --flip		是否提取图像水平flip特征

3. 注意点

   - 人脸检测采用的公开MTCNN方法，阈值设置在class FaceModel，PNET多尺度检测构建在mtcnn_detector.py 
   - 人脸识别模型输入为112*96*3，输出特征为256维归一化后的向量

