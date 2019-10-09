import flask
from aws_rekognition_client import *
from feature_extraction_client import *
from huawei_img_tagging_client import *
from oic_object_detection_client import *
from visual_relationship_detection_client import visual_relationship_detection_by_url as vrd_by_url, \
visual_relationship_detection_by_str_stream as vrd_by_str_stream
from face_detection_client import detection_by_url as face_detection_by_url, \
detection_by_str_stream as face_detection_by_str_stream
from multiprocessing import Process, Manager

def do_image_recognition():
    args = flask.request.args
    types = args.get('types')
    if types:
        types = types.split()
        if len(types) == 2:
            return do_object_detection_and_feature_extraction()
        else:
            func_no = types[0]
            if func_no == '0':
                return do_object_detection()
            elif func_no == '1':
                return do_feature_extraction()
            elif func_no == '2':
                return do_action_understanding()
            else:
	        return []
    else:
        return do_object_detection()
    
def do_object_detection():
    mgr = Manager()
    ret = mgr.list()
    args = flask.request.args
    imageurl = args.get('url') or args.get('imageurl')
    if imageurl:
	p1 = Process(target=aws_rekognition_by_url, args=(ret, imageurl))
	p2 = Process(target=oic_object_detection_by_url, args=(ret, imageurl))
	p3 = Process(target=vrd_by_url, args=(ret, imageurl))
	p4 = Process(target=face_detection_by_url, args=(ret, imageurl))
        #p5 = Process(target=huawei_image_tagging_by_url, args=(ret, imageurl))
    else:
        imagefile = flask.request.files['imagefile']
        str_stream = imagefile.read()
	p1 = Process(target=aws_rekognition_by_str_stream, args=(ret, str_stream))
        p2 = Process(target=oic_object_detection_by_str_stream, args=(ret, str_stream))
        p3 = Process(target=vrd_by_str_stream, args=(ret, str_stream))
        p4 = Process(target=face_detection_by_str_stream, args=(ret, str_stream))
	#p5 = Process(target=huawei_image_tagging_by_str_stream, args=(ret, str_stream))
    for x in (p1, p2, p3, p4): x.start()
    for x in (p1, p2, p3, p4): x.join()
    return list(ret)

def do_object_detection_and_feature_extraction():
    mgr = Manager()
    ret = mgr.list()
    args = flask.request.args
    imageurl = args.get('url') or args.get('imageurl')
    if imageurl:
	p1 = Process(target=aws_rekognition_by_url, args=(ret, imageurl, True))
        p2 = Process(target=oic_object_detection_by_url, args=(ret, imageurl, True))
        p3 = Process(target=vrd_by_url, args=(ret, imageurl, True))
        p4 = Process(target=face_detection_by_url, args=(ret, imageurl, True))
        #p5 = Process(target=huawei_image_tagging_by_url, args=(ret, imageurl))
    else:
        imagefile = flask.request.files['imagefile']
        str_stream = imagefile.read()
        p1 = Process(target=aws_rekognition_by_str_stream, args=(ret, str_stream, True))
        p2 = Process(target=oic_object_detection_by_str_stream, args=(ret, str_stream, True))
        p3 = Process(target=vrd_by_str_stream, args=(ret, str_stream, True))
        p4 = Process(target=face_detection_by_str_stream, args=(ret, str_stream, True))
        #p5 = Process(target=huawei_image_tagging_by_str_stream, args=(ret, str_stream))
    for x in (p1, p2, p3, p4): x.start()
    for x in (p1, p2, p3, p4): x.join()
    return list(ret)

def do_feature_extraction():
    ret = []
    args = flask.request.args
    imageurl = args.get('url') or args.get('imageurl')
    if imageurl: 
	feature_extraction_by_url(ret, imageurl)
    else:
	imagefile = flask.request.files['imagefile']
	str_stream = imagefile.read() 
	feature_extraction_by_str_stream(ret, str_stream)
    return ret

def do_action_understanding():
    ret = []
    return ret

#========== specific method for image upload =====================#
def do_image_recognition_by_stream(str_stream):
    mgr = Manager()
    ret = mgr.list()
    p1 = Process(target=aws_rekognition_by_str_stream, args=(ret, str_stream))
    p2 = Process(target=oic_object_detection_by_str_stream, args=(ret, str_stream))
    p3 = Process(target=vrd_by_str_stream, args=(ret, str_stream))
    p4 = Process(target=face_detection_by_str_stream, args=(ret, str_stream))
    #p5 = Process(target=huawei_image_tagging_by_str_stream, args=(ret, str_stream))
    for x in (p1, p2, p3, p4): x.start()
    for x in (p1, p2, p3, p4): x.join()
    return list(ret)
