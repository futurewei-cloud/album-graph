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
    
    # detection->max score bbox->feature
    def extract(self, image):
	res=self.model.get_feature(image)
	if res is None: return []
	return list(res.astype(float))

    def extract_by_image_path(self, path):
	image=cv2.imread(path)
	return self.extract(image)

    def detect(self, image, threshold):
        res, points=self.model.get_bboxes(image)
        output = [[x, points[i]] for i, x in enumerate(res) if x[4] >= threshold]
	return output

    def detect_by_image_path(self, path, threshold):
	image=cv2.imread(path)
	return self.detect(image, threshold)

    def get_feature(self, image, bbox, point):
	res = self.model.get_feature_by_bbox(image, bbox, point)
	if res is None: return []
	return list(res.astype(float))

if __name__=='__main__':
    import os, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help='image path')
    parser.add_argument('output_dir', help='output directory')
    args = parser.parse_args()
    extractor=FaceFeatureExtractor()
    #image_path='/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg'
    #print(extractor.extract_by_image_path(image_path))
    #image_path='/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    #image_path='/nfs_3/data/album_graph_data/Lin/2017-01-11_19-02-17_395.jpeg'
    if not os.path.exists(args.output_dir):
	os.makedirs(args.output_dir)
    image=cv2.imread(args.image_path)
    res = extractor.detect(image, .99)
    print(res)
    for i, x in enumerate(res):
	x, point = x[0], x[1]
        x1, y1, x2, y2 = int(x[0]), int(x[1]), int(x[2]), int(x[3])
        sub_img = image[y1:y2, x1:x2]
	name = str(i) + '.jpeg'
       	cv2.imwrite(os.path.join(args.output_dir, name), sub_img)
	cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    cv2.imwrite(os.path.join(args.output_dir, 'det.jpeg'), image)
