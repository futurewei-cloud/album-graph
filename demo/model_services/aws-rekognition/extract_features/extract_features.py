import argparse
import cv2
import os
from MTCNN import face_embedding


parser = argparse.ArgumentParser(description='face model test')
parser.add_argument('--image-size', default='112,96', help='')
parser.add_argument('--model', default='./face_recognition_model/model,250', help='path to load model.')
parser.add_argument('--gpu', default=0, type=int, help='gpu id')
parser.add_argument('--det', default=0, type=int, help='mtcnn option, 0 means using multiscale')
parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
args = parser.parse_args()

model = face_embedding.FaceModel(args)
filepath = "/home/mingweihe/workspace/_images/people"
for root,dirs,files in os.walk(filepath):
    for file in files:
        postfix = os.path.splitext(file)[1].lower()
        if (postfix in ['.jpg', '.jpeg', '.bmp', '.png']):
            img_path = os.path.join(root, file)
            img = cv2.imread(img_path)
            if (img is None):
                print("%s damaged image" % img_path)
                continue

            embed = model.get_feature(img)
            if (embed is None):
                print ("no face feature extracted from the image")
                continue
            else:
	        print (list(embed))
