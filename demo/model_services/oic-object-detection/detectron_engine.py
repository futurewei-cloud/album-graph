from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import argparse
import cv2  # NOQA (Must import before importing caffe2 due to bug in cv2)
import glob
import logging
import os
import sys
import time
import numpy as np
import pandas as pd

from caffe2.python import workspace

from detectron.core.config import assert_and_infer_cfg
from detectron.core.config import cfg
from detectron.core.config import merge_cfg_from_file
from detectron.utils.io import cache_url
from detectron.utils.logging import setup_logging
from detectron.utils.timer import Timer
import detectron.core.test_engine as infer_engine
import detectron.datasets.dummy_datasets as dummy_datasets
import detectron.utils.c2 as c2_utils
import detectron.utils.vis as vis_utils

c2_utils.import_detectron_ops()

# OpenCL may be enabled by default in OpenCV3; disable it because it's not
# thread safe and causes unwanted GPU memory allocations.
cv2.ocl.setUseOpenCL(False)

THIS_FOLDER = os.path.dirname(__file__)

#MODEL_CFG_FILE = os.path.join(THIS_FOLDER, 'models/e2e_mask_rcnn_R-50-FPN_2x.yaml')
#MODEL_WEIGHTS_FILE = os.path.join(THIS_FOLDER, 'models/model_final.pkl')
#LABEL_NAME_FILE = os.path.join(THIS_FOLDER, 'models/names.txt')

logger = logging.getLogger(__name__)

class DetectronEngine:

    def __init__(self):
        self.MODEL_CFG_FILE = 'e2e_mask_rcnn_R-50-FPN_OIC.yaml'
        self.LABEL_NAME_FILE = 'names_oic_388.txt'
        self.MODEL_WEIGHTS_FILE = 'model_170w.pkl'
	#self.MODEL_WEIGHTS_FILE = 'model_iter1779999.pkl'
	self.SCORE_THRESH = .5
	self.THRESHOLDS_FILE = 'oic_score_thresh_170w.csv'
	#self.THRESHOLDS_FILE = 'oic_score_thresh.csv'

    def set_config_files(self, _cfg, _labels, _weight, _score_thresh=.7):
        self.MODEL_CFG_FILE = _cfg
        self.LABEL_NAME_FILE = _labels
        self.MODEL_WEIGHTS_FILE = _weight
	self.SCORE_THRESH = _score_thresh
	self.THRESHOLDS_FILE = 'oic_score_thresh.csv'

    def initialization(self):

        merge_cfg_from_file(self.MODEL_CFG_FILE)
        cfg.NUM_GPUS = 1
        assert_and_infer_cfg(cache_urls=False)

        assert not cfg.MODEL.RPN_ONLY, \
            'RPN models are not supported'
        assert not cfg.TEST.PRECOMPUTED_PROPOSALS, \
            'Models that require precomputed proposals are not supported'
        self.model = infer_engine.initialize_model_from_cfg(self.MODEL_WEIGHTS_FILE)
        self.dummy_coco_dataset = dummy_datasets.get_coco_dataset()
        
        meta_data = pd.read_csv(self.THRESHOLDS_FILE).to_dict(orient='records')
        #print (meta_data)
        classes = ['background']
        thresholds = [1.1]
	for item in meta_data:
            name, thr = item['name'], item['threshold']
	    classes.append(name)
            thresholds.append(thr)

        self.dummy_coco_dataset.classes = {
            i: name for i, name in enumerate(classes)
        }

	self.classes = classes
	self.thresholds = thresholds

    def detect(self, im):
        timers = defaultdict(Timer)
        t = time.time()
        with c2_utils.NamedCudaScope(0):
            cls_boxes, cls_segms, cls_keyps = infer_engine.im_detect_all(
                self.model, im, None, timers=timers
            )
        logger.info('Inference time: {:.3f}s'.format(time.time() - t))
        for k, v in timers.items():
            logger.info(' | {}: {:.3f}s'.format(k, v.average_time))
        return cls_boxes

    def _get_class_string(self, class_index, dataset):
        class_text = dataset.classes[class_index] if dataset is not None else \
            'id{:d}'.format(class_index)
        return class_text

    def post_processing(self, cls_boxes):
        dets = []
        if cls_boxes is None:
            return {'detections': []}
        #print(cls_boxes)
        boxes, _, _, classes = vis_utils.convert_from_cls_format(cls_boxes, None, None)
        #print(boxes)
        if boxes is None:
            return {'detections': []}
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        sorted_inds = np.argsort(-areas)
	#logger.info(len(sorted_inds))
	#logger.info(sorted_inds)
	#logger.info(boxes)
	#logger.info(classes)
        for i in sorted_inds:
            bbox = boxes[i, :4]
            score = boxes[i, -1]
	    threshold = self.thresholds[classes[i]]
            if score < threshold:
                continue

            name = self._get_class_string(classes[i],
                                          self.dummy_coco_dataset)

            x1, y1, x2, y2 = bbox.astype(float)
            dets.append(
                {
                    'name': name,
                    'score': float(score),
                    'box': [x1, y1, x2, y2],
                }
            )
        return {'detections': dets}

    def draw_bbox(self, im, cls_boxes):
        vis_utils.vis_one_image(
            im[:, :, ::-1],  # BGR -> RGB for visualization
            'bbox',
            '/tmp/',
            cls_boxes,
            None,
            None,
            dataset=self.dummy_coco_dataset,
            box_alpha=0.3,
            show_class=True,
            #thresh=0.7,
            thresh=self.SCORE_THRESH,
            kp_thresh=2,
            ext='png',
            out_when_no_box=True
        )
        return cv2.imread('/tmp/bbox.png')[:, :, ::-1]


if __name__ == '__main__':
    im_path = '/home/linchen/data/Infrastructure_dataset/images/damaged_manhole_cover_000002.jpg'
    im = cv2.imread(im_path)

    det = DetectronEngine()
    det.initialization()
    boxes = det.detect(im)
    #print(det.post_processing(boxes))
    print(det.draw_bbox(im, boxes))
