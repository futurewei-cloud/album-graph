from __future__ import print_function, division
import torchvision
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from torch.autograd import Variable
import numpy as np

def resnet50_conv():
    model = torchvision.models.resnet50(pretrained=True)
    modules = list(model.children())[:-1]
    model = nn.Sequential(*modules)
    for param in model.parameters():
        param.requires_grad = False
    return model


class SceneFeatureExtractor(object):

    def __init__(self, gpu_id=None):
        self.gpu_id = gpu_id
        self.model = resnet50_conv()
        #self.data_transform = transforms.Compose([
        #    transforms.Resize(256),
        #    transforms.CenterCrop(224),
        #    transforms.ToTensor(),
        #    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        #])
	self.data_transform = transforms.Compose([
            transforms.Scale(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        if self.gpu_id is not None and self.gpu_id >= 0:
            self.model.cuda(self.gpu_id)

        with open('scene_pca_weight.txt') as f:
            weight = [map(float, _.strip().split(',')) for _ in f]
            self.weight = np.array(weight).T

    def _preprocess(self, image):
        image = self.data_transform(image)
        if self.gpu_id is not None and self.gpu_id >= 0:
            image = image.cuda(self.gpu_id)
        return image[None, :, :, :]

    def extract(self, image):
        image = self._preprocess(image)
        #print(image.shape)
        output = self.model(Variable(image))
        output = output.view(output.size(0), -1)
	output =  output.data.tolist()[0]
        output = np.matmul(self.weight, output)
        return output.tolist()
	#res = output.cpu().numpy()[0]
	#if res:
	#    return list(res.astype(float))
	#else:
	#    return []

if __name__ == '__main__':
    engine = SceneFeatureExtractor(gpu_id=0)

    # test 1
    image_file = '/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg'
    with open(image_file, 'rb') as f:
        image_data = Image.open(f).convert('RGB')
    feature = engine.extract(image_data)
    print(feature)
    print(len(feature))

    #image_file = '/nfs_3/data/album_graph_data/Lin/2016-05-07_193200513_CB8FC_iOS.jpg'
    #with open(image_file, 'rb') as f:
    #    image_data = f.read()
    #    from io import BytesIO
    #    image_data = Image.open(BytesIO(image_data)).convert('RGB')
    #feature = engine.process_image(image_data)
    #print(feature.shape)
    #print(feature)
