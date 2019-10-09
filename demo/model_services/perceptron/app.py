import os
import sys
import logging
import flask
from flask import jsonify
import optparse
import tornado.wsgi
import tornado.httpserver
sys.path.append('/app/utils')
sys.path.append('/app/services')
from msg import Message
from services import do_image_recognition, do_image_recognition_by_stream 
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('perceptron_log')
from datetime import datetime, timedelta
import json
import requests
import cv2
import numpy as np
from PIL import Image
import StringIO
# Obtain the flask app object
app = flask.Flask(__name__)
UPLOAD_FOLDER = '/tmp/perceptron_uploads'
LOG_FOLDER = '/logs'

@app.route('/')
def index():
    return flask.render_template('index.html', result={})

@app.route('/classify_url', methods=['GET'])
def classify_url():
    try:
	start = datetime.now()
	dets = do_image_recognition()
	imageurl=flask.request.args.get('imageurl')
	buffer_ = requests.get(imageurl).content	
	image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image_show = result_post_processing(image, dets)
	end = datetime.now()
        duration = end-start
        logger.info('Total time cost: {}s'.format(duration.total_seconds()))
        return flask.render_template(
            'index.html', result=json.dumps(dets, indent=4),
            imagesrc=embed_image_html(image_show))
    except Exception as err:
        # For any exception we encounter in reading the image, we will just
        # not continue.
        logger.info('URL Image open error: %s', err)
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
	start = datetime.now()
	imagefile = flask.request.files['imagefile']
        buffer_ = imagefile.read()
	dets = do_image_recognition_by_stream(buffer_)
        image = cv2.imdecode(np.asarray(bytearray(buffer_)), 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_show = result_post_processing(image, dets)
        end = datetime.now()
        duration = end-start
        logger.info('Total time cost: {}s'.format(duration.total_seconds()))
        return flask.render_template(
            'index.html', result=json.dumps(dets, indent=4),
            imagesrc=embed_image_html(image_show))
    except Exception as err:
        logger.info('Uploaded image open error: %s', err)
        return flask.render_template(
            'index.html',
            result=json.dumps({'status': 'Cannot open uploaded image.' + str(err)},
                              indent=4)
        )

@app.route('/album-graph/api/v1/perceptron', methods=['POST'])
def classify_api():
    try:
	ret = verify_request_parameters()
	if ret.code != '200': return ret.to_json()
	args = flask.request.args
        start = datetime.now()
	ret.res = do_image_recognition()
	end = datetime.now()
	duration = end-start
	logger.info('Total time cost: {}s'.format(duration.total_seconds()))
    except Exception as err:
        logger.error(str(err))
        ret = Message('500', str(err))
    return ret.to_json()

# verification
def verify_request_parameters():
    ret = Message('200', 'OK')
    # basic parameters verification
    args = flask.request.args
    req_types = args.get('types')
    req_language = args.get('language')
    req_url = args.get('url')
    req_roi = args.get('roi')
    req_max_lbs = args.get('max_labels')
    req_threshold = args.get('threshold')
    # image verification
    if not req_url:
        imagefile = flask.request.files['imagefile']
	if not imagefile:
	    ret.code = '420'
	    ret.msg = 'The requested resource does not support one or more of the given parameters.'
	    return ret
    return ret

def result_post_processing(image, dets):
    height, width, _ = image.shape
    for det in dets:
	box = det.get('box')
	if len(box) > 0:
	    name = det.get('name')
            x1, y1, x2, y2 = int(box[0]*width), int(box[1]*height), int((box[0]+box[2])*width), int((box[1]+box[3])*height)
            #sub_img = image[y1:y2, x1:x2]
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
	    cv2.putText(image, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    return image

def embed_image_html(image):
    """Creates an image embedded in HTML base64 format."""
    # image_pil = Image.fromarray((255 * image).astype('uint8'))
    image_pil = Image.fromarray(image.astype('uint8'))
    # image_pil = image_pil.resize((256, 256))
    string_buf = StringIO.StringIO()
    image_pil.save(string_buf, format='png')
    data = string_buf.getvalue().encode('base64').replace('\n', '')
    return 'data:image/png;base64,' + data

def start_tornado(app, port=5000):
    http_server = tornado.httpserver.HTTPServer(
        tornado.wsgi.WSGIContainer(app))
    http_server.listen(port)
    logger.info("Tornado server starting on port {}".format(port))
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

    if opts.debug:
        app.run(debug=True, host='0.0.0.0', port=opts.port)
    else:
        start_tornado(app, opts.port)

def pst(sec, what):
    pst_time = datetime.now() + timedelta(hours=-7)
    return pst_time.timetuple()

if __name__ == '__main__':
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    logger.setLevel(logging.INFO)
    logging.Formatter.converter = pst
    handler = RotatingFileHandler(os.path.join(LOG_FOLDER, 'perceptron_log.log'), maxBytes=10*1024*1024, backupCount=100)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', \
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    if not os.path.exists(UPLOAD_FOLDER):
    	os.makedirs(UPLOAD_FOLDER)
    start_from_terminal(app)
