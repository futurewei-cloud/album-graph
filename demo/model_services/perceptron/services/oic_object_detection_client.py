import sys
import json
import requests
sys.path.append('/app/utils')
try:
    from msg import Result
except Exception as e:
    pass

MS_OIC = 'http://10.145.83.59:8085/album-graph/ms/api/v1/oic-object-detection'

def oic_object_detection_by_url(ret, url, need_feature=False):
    if need_feature:
	response = requests.post(MS_OIC, params={'imageurl': url, 'require_features': 1})
    else:
        response = requests.post(MS_OIC, params={'imageurl': url})
    oic_res_postprocessing(ret, response, need_feature)

def oic_object_detection_by_str_stream(ret, str_stream, need_feature=False):
    if need_feature:
        response = requests.post(MS_OIC, files={'imagefile': str_stream}, params={'require_features': 1})
    else:
        response = requests.post(MS_OIC, files={'imagefile': str_stream})
    oic_res_postprocessing(ret, response, need_feature)

def oic_res_postprocessing(ret, response, need_feature=False):
    oic_res = json.loads(response.content).get('detections')
    if need_feature:
        for det in oic_res:
            features = det.get('features', [])
            sources = ['oic-object-detection']
            if features: sources.append('feature-extraction')
            ret.append(Result(det['box'], det['name'], det['score'], \
                features, sources).__dict__)
    else:
        for det in oic_res:
            ret.append(Result(det['box'], det['name'], det['score'], \
                    [], ['oic-object-detection']).__dict__)

if __name__=='__main__':
    sys.path.append('/nfs_2/mingweihe/workspace/model_services/perceptron/utils')
    from msg import Result
    #img_path = '/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    #with open(img_path, 'rb') as f:
    	#print(type(f))
    #    imgbytes=f.read()
    #aws_rekognition_by_str_stream('','', imgbytes)
    res = []
    oic_object_detection_by_url(res, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q', True)
    print json.dumps(res)
    
