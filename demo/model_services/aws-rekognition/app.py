import os, sys
import time
import cPickle
import datetime
import logging
import flask
from flask import jsonify
import werkzeug
import optparse
import tornado.wsgi
import tornado.httpserver
import numpy as np
import pandas as pd
from PIL import Image
import cStringIO as StringIO
import io
import requests
import cv2
import json
#from face_feature_extractor import FaceFeatureExtractor
from scene_feature_extractor import SceneFeatureExtractor
sys.path.append('/app/utils')
from msg import Result, Feature

import boto3
from decouple import config

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'bmp', 'jpg', 'jpe', 'jpeg', 'gif'])
MAX_FILE_SIZE = 5242880.

# Obtain the flask app object
app = flask.Flask(__name__)

@app.route('/album-graph/ms/api/v1/aws-rekognition', methods=['POST'])
def classify_api():
    try:
        # add for url processing
        imageurl = flask.request.args.get('imageurl')
        if imageurl:
            buffer_ = requests.get(imageurl).content
        else:
            imagefile = flask.request.files['imagefile']
            buffer_ = imagefile.read()
        result = aws_rekognition(buffer_)
        return jsonify(result)
    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return jsonify({'status': 'Cannot open uploaded image.' + str(err)})

def get_client():
    client = boto3.client(\
    'rekognition',\
    aws_access_key_id=config('AWS_ACCESS_KEY'),\
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),region_name='us-west-2')
    return client

def aws_preprocessing(buffer_):
    bytes_size = len(buffer_)
    while bytes_size > MAX_FILE_SIZE:
	img = Image.open(io.BytesIO(buffer_))
	downscale = (MAX_FILE_SIZE/bytes_size)**.5
	w,h=img.size
	img_new = img.resize((int(w*downscale), int(h*downscale)))
	imgByteArr = io.BytesIO()
	img_new.save(imgByteArr, format=img.format)
	buffer_ = imgByteArr.getvalue()
	bytes_size = len(buffer_)
    return buffer_

def aws_rekognition(buffer_):
    buffer_ = aws_preprocessing(buffer_)
    ret = []
    client = get_client()
    imgobj = {'Bytes': buffer_}
    response = client.detect_labels(Image=imgobj, MinConfidence=90)
    labels = response.get('Labels')
    if flask.request.args.get('require_features') == '1':
	image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image.shape
        for label in labels:
	    name = label.get('Name')
            instances = label.get('Instances')
	    if len(instances) > 0:
	        for ins in instances:
		    score = round(ins.get('Confidence')/100., 8)
		    bbox = ins.get('BoundingBox')
		    x,y,w,h = bbox.get('Left'), bbox.get('Top'), bbox.get('Width'), bbox.get('Height')
		    sub_img = image[int(height*y):int(height*(y+h)), int(width*x):int(width*(x+w))]
		    #face_feature = app.face_feature_extractor.extract(sub_img)
		    scene_feature = app.scene_feature_extractor.extract(Image.fromarray(sub_img))
		    features = []
		    #if face_feature:
		    #    features.append(Feature('face', face_feature).__dict__)
		    if scene_feature:
		        features.append(Feature('scene', scene_feature).__dict__)
		    if features: sources = ['aws-object-detection', 'feature-extraction']
		    else: sources = ['aws-object-detection']
	            ret.append(Result([x, y, w, h], name, score, features, sources).__dict__)
	    else:
		score = round(label.get('Confidence')/100., 8)
		ret.append(Result([], name, score, [], ['aws-image-tagging']).__dict__)
    else:
        for label in labels:
            name = label.get('Name')
            instances = label.get('Instances')
	    if len(instances) > 0:
                for ins in instances:
                    bbox = ins.get('BoundingBox')
                    x,y,w,h = bbox.get('Left'), bbox.get('Top'), bbox.get('Width'), bbox.get('Height')
                    score = round(ins.get('Confidence')/100., 8)
                    ret.append(Result([x, y, w, h], name, score, [], ['aws-object-detection']).__dict__)
            else:	
                score = round(label.get('Confidence')/100., 8)
                ret.append(Result([], name, score, [], ['aws-image-tagging']).__dict__)
    return ret

def embed_image_html(image):
    """Creates an image embedded in HTML base64 format."""
    # image_pil = Image.fromarray((255 * image).astype('uint8'))
    image_pil = Image.fromarray(image.astype('uint8'))
    # image_pil = image_pil.resize((256, 256))
    string_buf = StringIO.StringIO()
    image_pil.save(string_buf, format='png')
    data = string_buf.getvalue().encode('base64').replace('\n', '')
    return 'data:image/png;base64,' + data


def allowed_file(filename):
    return (
            '.' in filename and
            filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS
    )


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
    #app.face_feature_extractor = FaceFeatureExtractor()
    app.scene_feature_extractor = SceneFeatureExtractor()

    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        start_tornado(app, opts.port)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    start_from_terminal(app)
