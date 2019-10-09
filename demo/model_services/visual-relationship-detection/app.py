import os
import sys
import time
import cPickle
import datetime
import logging
import flask
from flask import jsonify, make_response
import werkzeug
import optparse
import tornado.wsgi
import tornado.httpserver
import numpy as np
import pandas as pd
from PIL import Image
import cStringIO as StringIO
import cv2
#from detectron_engine import DetectronEngine
import json
import requests
import uuid
from visual_relationship_detector import VisualRelationshipDetector
import tarfile
sys.path.append('/app/utils')
from msg import Result, Feature
from face_feature_extractor import FaceFeatureExtractor
from scene_feature_extractor import SceneFeatureExtractor

# Obtain the flask app object
app = flask.Flask(__name__)
#UPLOAD_FOLDER = '/tmp/feature_extraction_uploads'

@app.route('/album-graph/ms/api/v1/visual-relationship-detection', methods=['POST'])
def classify_api():
    try:
        # add for url processing
        imageurl = flask.request.args.get('imageurl')
        if imageurl:
	    buffer_ = requests.get(imageurl).content
        else:
            # We will save the file to disk for possible data collection.
            imagefile = flask.request.files['imagefile']
	    buffer_ = imagefile.read()
	result = vrd_detecion(buffer_)
	#logging.info(result)
	#boxes,  = app.detector.detect(image)
        #result['visual_relationships'] = visual_relationships
        return jsonify(result)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return jsonify({'status': 'Cannot open uploaded image.' + str(err)})

def vrd_detecion(buffer_): 
    ret = []
    image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
    det_boxes, rels = app.detector.detect(image)
    if len(rels) > 0:
    	ret.append(Result([], '', -1, [], ['vrd-relationship-detection'], rels).__dict__)
    if flask.request.args.get('require_features') == '1':
        height, width, _ = image.shape
	for i, ins in enumerate(det_boxes):
	    tag = ins.get('name')
            name = tag + str(i)
            score = ins.get('confidence')
            box = ins.get('box')
	    x,y,w,h = box[0], box[1], box[2], box[3]
	    features = []
	    if tag == 'face':
		box_4_face = [x*width, y*height, (x+w)*width, (y+h)*height]
	        face_feature = app.face_feature_extractor.get_feature(image, box_4_face, None)
                if len(face_feature) > 0:
		    features.append(Feature('face', face_feature).__dict__)
	    else:
		sub_img = image[int(height*y):int(height*(y+h)), int(width*x):int(width*(x+w))]
		sub_img = cv2.cvtColor(sub_img, cv2.COLOR_BGR2RGB)
	        scene_feature = app.scene_feature_extractor.extract(Image.fromarray(sub_img))
                features.append(Feature('scene', scene_feature).__dict__)
	    if features: sources = ['vrd-object-detection', 'feature-extraction']
            else: sources = ['vrd-object-detection']
            ret.append(Result(box, name, score, features, sources).__dict__)
    else:
        for i, ins in enumerate(det_boxes):
	    name = ins.get('name') + str(i)
	    score = ins.get('confidence')
	    box = ins.get('box')
	    ret.append(Result(box, name, score, [], ['vrd-object-detection']).__dict__)
    return ret    

def start_tornado(app, port=5000):
    http_server = tornado.httpserver.HTTPServer(
        tornado.wsgi.WSGIContainer(app))
    http_server.listen(port)
    print("Tornado server starting on port {}".format(port))
    tornado.ioloop.IOLoop.instance().start()


def start_from_terminal(app):
    """
    Parse command line options and start the server.
    """
    parser = optparse.OptionParser()
    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)
    parser.add_option(
        '-p', '--port',
        help="which port to serve content on",
        type='int', default=5000)
    parser.add_option(
        '-g', '--gpu',
        help="use gpu mode",
        action='store_true', default=False)

    opts, args = parser.parse_args()
    app.detector = VisualRelationshipDetector()
    app.face_feature_extractor = FaceFeatureExtractor()
    app.scene_feature_extractor = SceneFeatureExtractor(0)

    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        start_tornado(app, opts.port)


if __name__ == '__main__':
    #tf = tarfile.open("extract_features.tar.gz")
    #tf.extractall()
    logging.getLogger().setLevel(logging.INFO)
    #if not os.path.exists(UPLOAD_FOLDER):
    #    os.makedirs(UPLOAD_FOLDER)
    start_from_terminal(app)
