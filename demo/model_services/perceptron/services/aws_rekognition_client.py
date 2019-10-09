import sys
import json
import requests
import logging
sys.path.append('/app/utils')
try:
    from msg import Result
except Exception as e:
    pass

MS_AWS = 'http://10.145.83.59:8086/album-graph/ms/api/v1/aws-rekognition'

def aws_rekognition_by_url(ret, url, need_feature=False):
    if need_feature:
	response = requests.post(MS_AWS, params={'imageurl': url, 'require_features': 1})
    else:
        response = requests.post(MS_AWS, params={'imageurl': url})
    aws_res_postprocessing(ret, response)

def aws_rekognition_by_str_stream(ret, str_stream, need_feature=False):
    if need_feature:
        response = requests.post(MS_AWS, files={'imagefile': str_stream}, params={'require_features': 1})
    else:
        response = requests.post(MS_AWS, files={'imagefile': str_stream})
    aws_res_postprocessing(ret, response)

def aws_res_postprocessing(ret, response):
    aws_res = json.loads(response.content)
    if type(aws_res) == dict: return
    for det in aws_res: ret.append(det)

if __name__=='__main__':
    sys.path.append('/nfs_2/mingweihe/workspace/model_services/perceptron/utils')
    from msg import Result
    res = []
    img_path = '/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    #img_path = '/nfs_3/data/album_graph_data/Lin/2017-03-30_12-41-36_502.jpeg'
    #img_path = '/nfs_3/data/album_graph_data/photos/2018-09-09_15-56-11_011.heic'
    with open(img_path, 'rb') as f:
        imgbytes=f.read()
    aws_rekognition_by_str_stream(res, imgbytes, True)
    #aws_rekognition_by_url(res, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q',)
    print json.dumps(res)
    
