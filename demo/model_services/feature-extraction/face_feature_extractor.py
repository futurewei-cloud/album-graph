import cv2
import sys
sys.path.append('extract_features')
from MTCNN import face_embedding

class FaceFeatureExtractor:
    def __init__(self):
	self.image_size='112,96'
	self.model='./extract_features/face_recognition_model/model,250'
	self.gpu=0
	self.det=0
	self.flip=0
	self.model=face_embedding.FaceModel(self)
    
    def extract(self, image):
	res=self.model.get_feature(image)
	if res is None: return []
	else: return list(res.astype(float))

    def extract_by_image_path(self, path):
	image=cv2.imread(path)
	#image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	res=self.model.get_feature(image)
	if res is None: return []
	else: return list(res.astype(float))


if __name__=='__main__':
    extractor=FaceFeatureExtractor()
    print(extractor.extract_by_image_path('/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg'))
