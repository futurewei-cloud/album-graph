import requests
import argparse
import json

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img', help='image')
    parser.add_argument('--url', help='image url on internet')
    parser.add_argument('--feature', help='feature')
    args=parser.parse_args()
    if args.img: filepath=args.img
    else: filepath = '/nfs_2/mingweihe/workspace/_images/people/16people.jpg'
    req = requests.post(
        'http://10.145.83.59:8087/album-graph/ms/api/v1/visual-relationship-detection',
        files={
            'imagefile': open(filepath, 'rb')
        },
	params={
	    'imageurl': args.url
            ,'require_features': args.feature
	}
    )
    print(req.content)
