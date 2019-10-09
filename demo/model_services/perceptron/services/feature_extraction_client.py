import os
import sys
import json
import requests
sys.path.append('/app/utils')
try:
    from msg import Result
except Exception as e:
    pass

MS_FEATURE_EXT = 'http://10.145.83.59:8084/album-graph/ms/api/v1/feature-extraction'

def feature_extraction_by_url(ret, url):
    response = requests.post(MS_FEATURE_EXT, params={'imageurl': url})
    feature_extraction_postprocessing(ret, response)

def feature_extraction_by_str_stream(ret, str_stream):
    response = requests.post(MS_FEATURE_EXT, files={'imagefile': str_stream})
    feature_extraction_postprocessing(ret, response) 

def feature_extraction_postprocessing(ret, raw_res):
    json_res = json.loads(raw_res.content).get('features', [])
    ret.append(Result([], '', -1, json_res, ['feature-extraction']).__dict__)

if __name__=='__main__':
    sys.path.append('/nfs_2/mingweihe/workspace/model_services/perceptron/utils')
    from msg import Result
    res = []
    img_path = '/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    with open(img_path, 'rb') as f:
        imgbytes=f.read()
    feature_extraction_by_str_stream(res, imgbytes)
    #feature_extraction_by_url(res, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q')
    print json.dumps(res)
