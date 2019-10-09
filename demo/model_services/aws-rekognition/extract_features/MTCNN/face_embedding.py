from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
import mxnet as mx
import cv2
from sklearn import preprocessing
from easydict import EasyDict as edict
from MTCNN.mtcnn_detector import MtcnnDetector
import MTCNN.face_preprocess as face_preprocess


def do_flip(data):
  for idx in xrange(data.shape[0]):
    data[idx,:,:] = np.fliplr(data[idx,:,:])

class FaceModel:
  def __init__(self, args):
    self.args = args
    model = edict()
    self.det_minsize = 50
    self.det_threshold = [0.6,0.7,0.8]
    self.det_factor = 0.9
    _vec = args.image_size.split(',')
    assert len(_vec)==2
    image_size = (int(_vec[0]), int(_vec[1]))
    self.image_size = image_size
    _vec = args.model.split(',')
    assert len(_vec)==2
    prefix = _vec[0]
    epoch = int(_vec[1])
    print('loading',prefix, epoch)
    ctx = mx.gpu(args.gpu)
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    all_layers = sym.get_internals()
    sym = all_layers['fc1_output']
    model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
    #model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
    model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
    model.set_params(arg_params, aux_params)
    self.model = model
    mtcnn_path = os.path.join(os.path.dirname(__file__), 'mtcnn-model')
    detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1, accurate_landmark = True, threshold=self.det_threshold)
    self.detector = detector


  def get_feature(self, face_img):
    ret = self.detector.detect_face(face_img, det_type = self.args.det)
    if ret is None:
      return None
    bbox, points = ret
    if bbox.shape[0]==0:
      return None
    bbox = bbox[0,0:4]
    points = points[0,:].reshape((2,5)).T
    nimg = face_preprocess.preprocess(face_img, bbox, points, image_size='%d,%d' % (self.image_size[0], self.image_size[1]))
    nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
    aligned = np.transpose(nimg, (2,0,1))
    embedding = None
    for flipid in [0,1]:
      if flipid==1:
        if self.args.flip==0:
          break
        do_flip(aligned)
      input_blob = np.expand_dims(aligned, axis=0)
      data = mx.nd.array(input_blob)
      db = mx.io.DataBatch(data=(data,))
      self.model.forward(db, is_train=False)
      _embedding = self.model.get_outputs()[0].asnumpy()

      if embedding is None:
        embedding = _embedding
      else:
        embedding += _embedding
    embedding = preprocessing.normalize(embedding).flatten()
    return embedding

  def get_feature_by_bbox(self, face_img, bbox, point):
    if point is not None:
      point = point.reshape((2,5)).T
    nimg = face_preprocess.preprocess(face_img, bbox, point, image_size='%d,%d' % (self.image_size[0], self.image_size[1]))
    nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
    aligned = np.transpose(nimg, (2,0,1))
    embedding = None
    for flipid in [0,1]:
      if flipid==1:
        if self.args.flip==0:
          break
        do_flip(aligned)
      input_blob = np.expand_dims(aligned, axis=0)
      data = mx.nd.array(input_blob)
      db = mx.io.DataBatch(data=(data,))
      self.model.forward(db, is_train=False)
      _embedding = self.model.get_outputs()[0].asnumpy()

      if embedding is None:
        embedding = _embedding
      else:
        embedding += _embedding
    embedding = preprocessing.normalize(embedding).flatten()
    return embedding

  def get_bboxes(self, face_img):
    ret = self.detector.detect_face(face_img, det_type = self.args.det)
    if ret is None:
      return [],[]
    bbox, points = ret
    if bbox.shape[0]==0:
      return [],[]
    return bbox, points
