import requests
import argparse


#req = requests.get(
#    'http://49.4.89.32:5000/classify_url?imageurl=http://www.wmvo.com/wp-content/uploads/2018/03/pothole_key-660x330.jpg')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img', help='image')
    parser.add_argument('--url', help='imageurl')
    parser.add_argument('--feature', help='require feature or not (0 or 1)')
    args=parser.parse_args()
    if args.img: filepath=args.img
    else: filepath = '/nfs_1/data/OpenImage/images_from_val/26bff4e2b0a6fb23.jpg'
    req = requests.post(
        'http://10.145.83.59:8086/album-graph/ms/api/v1/aws-rekognition',
        files={
            'imagefile': open(filepath, 'rb')
        }
	,params={
	    'require_features': args.feature,
	    'imageurl': args.url
	}
    )
    print(req.content)
