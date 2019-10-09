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
import requests

import cv2
from detectron_engine import DetectronEngine
import json
from face_feature_extractor import FaceFeatureExtractor
from scene_feature_extractor import SceneFeatureExtractor
sys.path.append('/app/utils')
from msg import Feature
from tools import oic_box2std

REPO_DIRNAME = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../..')
UPLOAD_FOLDER = '/tmp/detectron_demos_uploads'
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'bmp', 'jpg', 'jpe', 'jpeg', 'gif'])

# Obtain the flask app object
app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html', result={})


@app.route('/classify_url', methods=['GET'])
def classify_url():
    imageurl = flask.request.args.get('imageurl', '')
    try:
	buffer_ = requests.get(imageurl).content
        image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
        #print 'max pixel value: ', image.max(), image.dtype
	
	logging.info('Image: %s', imageurl)
        dets = app.clf.detect(image)
        result = app.clf.post_processing(dets)
        if result['detections']:
            image_show = app.clf.draw_bbox(image, dets)
        else:
            image_show = image[:, :, ::-1]
        return flask.render_template(
            'index.html', result=json.dumps(result, indent=4),
            imagesrc=embed_image_html(image_show))

    except Exception as err:
        # For any exception we encounter in reading the image, we will just
        # not continue.
        logging.info('URL Image open error: %s', err)
        return flask.render_template(
            'index.html',
            result=json.dumps(
                {'status': 'Cannot open image from URL.' + str(err)},
                indent=4
            )
        )

@app.route('/classify_upload', methods=['POST'])
def classify_upload():
    try:
        # We will save the file to disk for possible data collection.
        imagefile = flask.request.files['imagefile']
        filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
                    werkzeug.secure_filename(imagefile.filename)
        filename = os.path.join(UPLOAD_FOLDER, filename_)
        imagefile.save(filename)
        logging.info('Saving to %s.', filename)
        image = cv2.imread(filename)
        #print 'max pixel value: ', image.max(), image.dtype
        dets = app.clf.detect(image)
        result = app.clf.post_processing(dets)
        if result['detections']:
            image_show = app.clf.draw_bbox(image, dets)
        else:
            image_show = image[:, :, ::-1]
        return flask.render_template(
            'index.html', result=json.dumps(result, indent=4),
            imagesrc=embed_image_html(image_show)
        )
    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return flask.render_template(
            'index.html',
            result=json.dumps({'status': 'Cannot open uploaded image.' + str(err)},
                              indent=4)
        )

@app.route('/album-graph/ms/api/v1/oic-object-detection', methods=['POST'])
def classify_api():
    try:
	# add for url processing
        imageurl = flask.request.args.get('imageurl')
        if imageurl:
	    buffer_ = requests.get(imageurl).content
        else:
	    imagefile = flask.request.files['imagefile']
	    buffer_ = imagefile.read()
	image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1) 
	height, width, _ = image.shape
        dets = app.clf.detect(image)
        result = app.clf.post_processing(dets)
        # feature extraction processing
        if flask.request.args.get('require_features') == '1':
            for det in result.get('detections'):
                x1,y1,x2,y2 = tuple(det['box'])
                sub_img = image[int(y1):int(y2), int(x1):int(x2)]
		name = det.get('name')
		features = []
		if name == 'Face':
		    box_4_face = [x1, y1, x2, y2]
                    face_feature = app.face_feature_extractor.get_feature(image, box_4_face, None)
		    if len(face_feature) > 0:
		        features.append(Feature('face', face_feature).__dict__)
		else:
		    sub_img = image[int(y1):int(y2), int(x1):int(x2)]
		    sub_img = cv2.cvtColor(sub_img, cv2.COLOR_BGR2RGB)
		    scene_feature = app.scene_feature_extractor.extract(Image.fromarray(sub_img))
                    features.append(Feature('scene', scene_feature).__dict__)
                det['features'] = features
		# transform to float type box
		det['box'] = oic_box2std(det['box'], width, height)
	else:
	    for det in result.get('detections'):
		# transform to float type box
	        det['box'] = oic_box2std(det['box'], width, height)
        return jsonify(result)

    except Exception as err:
        logging.info('Uploaded image open error: %s', err)
        return jsonify({'status': 'Cannot open uploaded image.' + str(err)})

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

    app.clf = DetectronEngine()
    app.clf.initialization()
    app.face_feature_extractor = FaceFeatureExtractor()
    app.scene_feature_extractor = SceneFeatureExtractor()

    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        start_tornado(app, opts.port)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    start_from_terminal(app)
