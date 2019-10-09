import os
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
from face_feature_extractor import FaceFeatureExtractor
from scene_feature_extractor import SceneFeatureExtractor
import tarfile

# Obtain the flask app object
app = flask.Flask(__name__)
UPLOAD_FOLDER = '/tmp/feature_extraction_uploads'

@app.route('/album-graph/ms/api/v1/feature-extraction', methods=['POST'])
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
        image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
	#logging.info(image)
        result = {}
        # float data like -0.03827 is not serializable, so convert the whole list to string intead
        face_feature = app.face_feature_extractor.extract(image)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        scene_feature = app.scene_feature_extractor.extract(Image.fromarray(image))
        features = []
        if face_feature:
            features.append({
                'type': 'face',
                'value': face_feature
            })
        if scene_feature:
            features.append({
                'type': 'scene',
                'value': scene_feature
            })
        result['features'] = features
        return jsonify(result)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return jsonify({'status': 'Cannot open uploaded image.' + str(err)})
    

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
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    start_from_terminal(app)
