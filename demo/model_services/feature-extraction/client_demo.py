import requests
import argparse
import json


#req = requests.get(
#    'http://49.4.89.32:5000/classify_url?imageurl=http://www.wmvo.com/wp-content/uploads/2018/03/pothole_key-660x330.jpg')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img', help='image')
    parser.add_argument('--url', help='image url on internet')
    args=parser.parse_args()
    if args.img: filepath=args.img
    else: filepath = '/nfs_2/mingweihe/workspace/_images/people/16people.jpg'
    req = requests.post(
        'http://10.145.83.59:8084/album-graph/ms/api/v1/feature-extraction',
        files={
            'imagefile': open(filepath, 'rb')
        },
	params={
	    'imageurl': args.url
	}
    )
    print(req.content)
