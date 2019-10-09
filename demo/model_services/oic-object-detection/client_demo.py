import requests
import argparse
import json

#req = requests.get(
#    'http://49.4.89.32:5000/classify_url?imageurl=http://www.wmvo.com/wp-content/uploads/2018/03/pothole_key-660x330.jpg')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img', help='image')
    parser.add_argument('--feature', help='need feature. (0 or 1)')
    args=parser.parse_args()
    if args.img: filepath=args.img
    #else: filepath = '/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg' 
    else: filepath = '/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg' 
    need_feature = args.feature
    req = requests.post(
        'http://10.145.83.59:8085/album-graph/ms/api/v1/oic-object-detection',
        files={
            'imagefile': open(filepath, 'rb')
        }
	,params={
	    'require_features': need_feature if need_feature else 0
	    #,'imageurl': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q'
	}
    )
    print(req.content)
    #data = json.loads(req.content)
    #print data['detections'][0]['box']
