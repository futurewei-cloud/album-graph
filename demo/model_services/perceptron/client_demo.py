import requests
import argparse
import json

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--types', help='recognition types, divided by space')
    parser.add_argument('--img', help='image')
    parser.add_argument('--url', help='image url on internet')
    args=parser.parse_args()
    if args.img: filepath=args.img
    else: filepath = '/nfs_1/data/OpenImage/images_from_val/0af4326e3db0c11a.jpg'
    req = requests.post(
        'http://10.145.83.59/album-graph/api/v1/perceptron',
        files={
            'imagefile': open(filepath, 'rb')
        },
	params={
	    'types': args.types if args.types else '0',
	    'url': args.url
	}
    )
    print(req.content)
    #with open('result.json', 'w') as f:
    #    json.dump(json.loads(req.content), f)
