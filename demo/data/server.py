from flask import Flask
from flask import jsonify
from flask import make_response
from flask import abort
from flask import request
from flask import send_from_directory
from PIL import Image
from flask_cors import CORS

from gremlin_server import get_result


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return 'Welcome to Album Graph data server'


@app.route('/albumgraph')
def albumgraph():
    need = request.args.get('need')
    arg = request.args.get('arg')
    if need == 'img':
        output = request.args.get('output')
        arg = [output, arg]
    if need == 'date' or need == 'entities':
        start = request.args.get('start')
        end = request.args.get('end')
        arg = [start, end]
    if need == 'gpsrange':
        lat_lb = request.args.get('lat_lb')
        lat_ub = request.args.get('lat_ub')
        lon_lb = request.args.get('lon_lb')
        lon_ub = request.args.get('lon_ub')
        arg = [[lat_lb, lat_ub], [lon_lb, lon_ub]]
    if need == 'semantic':
        subj = request.args.get('subj')
        predicate = request.args.get('predicate')
        obj = request.args.get('obj')
        arg = [subj, predicate, obj]
    if need == 'recommendation':
        num = request.args.get('num')
        arg = [arg, num]
    dataset = request.args.get('dataset')
    return jsonify(get_result(need, arg, dataset))


@app.route('/simages')
def s_result_file():
    prefix = request.args.get('prefix')
    filename = request.args.get('filename')
    RESULT_FOLDER = prefix+'simages/'
    app.config['RESULT_FOLDER'] = RESULT_FOLDER
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


@app.route('/mimages')
def m_result_file():
    prefix = request.args.get('prefix')
    filename = request.args.get('filename')
    RESULT_FOLDER = prefix+'mimages/'
    app.config['RESULT_FOLDER'] = RESULT_FOLDER
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


@app.route('/oimages')
def o_result_file():
    prefix = request.args.get('prefix')
    filename = request.args.get('filename')
    RESULT_FOLDER = prefix
    app.config['RESULT_FOLDER'] = RESULT_FOLDER
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
