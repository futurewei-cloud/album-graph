import os
import sys
import json
import requests
sys.path.append('/app/utils')
import logging
try:
    from msg import Result
except Exception as e:
    pass

MS_URL = 'http://10.145.83.59:8088/album-graph/ms/api/v1/face-detection'

def detection_by_url(ret, url, need_feature=False):
    if need_feature: nf = 1
    else: nf = 0
    response = requests.post(MS_URL, params={'imageurl': url, 'require_features': nf})
    postprocessing(ret, response)

def detection_by_str_stream(ret, str_stream, need_feature=False):
    if need_feature: nf = 1
    else: nf = 0
    response = requests.post(MS_URL, files={'imagefile': str_stream}, params={'require_features': nf})
    postprocessing(ret, response)

def postprocessing(ret, response):
    _res = json.loads(response.content)
    if type(_res) == dict: return
    for det in _res: ret.append(det)

if __name__=='__main__':
    sys.path.append('/nfs_2/mingweihe/workspace/model_services/perceptron/utils')
    from msg import Result
    res = []
    img_path = '/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    with open(img_path, 'rb') as f:
        imgbytes=f.read()
    detection_by_str_stream(res, imgbytes, True)
    #feature_extraction_by_url(res, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q')
    print json.dumps(res)
