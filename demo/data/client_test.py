import requests
import argparse
import json
import os
import glob
import csv
import PIL.Image
import PIL.ExifTags
import geopy.geocoders
from geopy.geocoders import Photon
# req = requests.get(
#    'http://49.4.89.32:5000/classify_url?imageurl=http://www.wmvo.com/wp-content/uploads/2018/03/pothole_key-660x330.jpg')

if __name__ == '__main__':
    # write file
    vertexout = open('vertex_stable.csv', 'w')
    edgeout = open('edge_stable.csv', 'w')
    vertex_write = csv.writer(vertexout, dialect='excel')
    edge_write = csv.writer(edgeout, dialect='excel')
    geopy.geocoders.options.default_timeout = None

    # get data from seatle cv server
    parser = argparse.ArgumentParser()
    parser.add_argument('--types', help='recognition types, divided by space')
    parser.add_argument('--img', help='image')
    parser.add_argument('--url', help='image url on internet')
    args = parser.parse_args()

    if args.img:
        filepath = args.img
    else:
        filepath = '/nfs_3/data/album_graph_data/Lin/G0010356.JPG'

    # Set the path of your image forder
    path = '/home/zhaoxi/nfs_3/data/album_graph_data/Lin/'  # 33
    # path='/home/zz/Lin/' #for test
    image_id = 0
    object_id = 0
    relationship_id = 0
    tagdict = {}
    modeldict = {}
    countrydict = {}
    statedict = {}
    citydict = {}
    addressdict = {}
    idtofeature = []
    for f in glob.iglob(os.path.join(path, '*')):  # '*.jpeg' for test
        # if image_id==1:break#for test
        if f == path+'tmp.jpg':
            continue
        if os.path.isfile(f):
            # f=path+'2017-03-21_10-32-03_000.jpeg' #for test
            print f
            # cv
            req = requests.post(
                'http://10.145.83.59/album-graph/api/v1/perceptron',
                files={
                    'imagefile': open(f, 'rb')
                },
                params={
                    'types': args.types if args.types else '0 1',
                    'url': args.url
                }
            )

            # extract exif info
            lat = -999
            lon = -999
            datetime = ''
            model = ''
            try:
                img = PIL.Image.open(f)
                if img.format == 'JPEG':
                    exif_data = img._getexif()
                    if img._getexif() is not None:
                        exif = {
                            PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS
                        }

                        for key in exif:
                            if key == 'GPSInfo':
                                hasgpsinfo = 0
                                for k in exif[key].keys():
                                    decode = PIL.ExifTags.GPSTAGS.get(k, k)
                                    if decode == 'GPSLatitudeRef':
                                        hasgpsinfo += 1
                                    if decode == 'GPSLatitude':
                                        hasgpsinfo += 1
                                    if decode == 'GPSLongitudeRef':
                                        hasgpsinfo += 1
                                    if decode == 'GPSLongitude':
                                        hasgpsinfo += 1

                                if hasgpsinfo == 4:
                                    lat = [float(x)/float(y)
                                           for x, y in exif[key][2]]
                                    latref = exif[key][1]
                                    lon = [float(x)/float(y)
                                           for x, y in exif[key][4]]
                                    lonref = exif[key][3]
                                    #print lat
                                    lat = lat[0] + lat[1]/60 + lat[2]/3600
                                    lon = lon[0] + lon[1]/60 + lon[2]/3600
                                    if latref == 'S':
                                        lat = -lat
                                    if lonref == 'W':
                                        lon = -lon
                                    #print 'gpslatitude',lat
                                    #print 'gpslongitude',lon

                            if key == 'DateTimeOriginal':
                                datetime = exif[key].__str__()
                                datetime = datetime[:4]+'/' + \
                                    datetime[5:7]+'/'+datetime[8:]
                                print 'datetime', datetime
                            if key == 'Model':
                                model = exif[key].__str__()
                                #print 'model',model
            except IOError:
                print 'can not open and get exif'

            # locate the address from coordinates
            country = ''
            state = ''
            city = ''
            address = ''
            event_id = -1
            if lat != -999 and lon != -999:
                geolocator = Photon()
                #print str(lat)+','+str(lon)
                location = geolocator.reverse(str(lat)+','+str(lon))
                if location != None:
                    address = location.address.encode("utf-8")
                    for key in location.raw['properties']:
                        if key == 'country':
                            country = location.raw['properties'][key].encode(
                                "utf-8")
                        if key == 'state':
                            state = location.raw['properties'][key].encode(
                                "utf-8")
                        if key == 'city':
                            city = location.raw['properties'][key].encode(
                                "utf-8")

            # write image data into csv
            imagedata = json.loads(req.content)['res']
            imagenodeid = 'image'+str(image_id)
            image_path = f
            vertex_write.writerow(
                [imagenodeid, 'image', image_id, image_path, datetime, lat, lon, address, event_id])

            modelnodeid = 'model'+model
            if modelnodeid not in modeldict:
                modeldict[modelnodeid] = 1
                if model != '':
                    vertex_write.writerow([modelnodeid, 'model', model])
            edge_write.writerow([modelnodeid, imagenodeid, 'edge'])

            boxname_to_id = {}
            for obj in imagedata:
                if obj == 'status':
                    continue
                if obj['name'] != '':
                    bboxnodeid = 'bbox'+str(object_id)
                    if len(obj['box']) != 0:
                        x = obj['box'][0]
                        y = obj['box'][1]
                        w = obj['box'][2]
                        h = obj['box'][3]
                    else:
                        x, y, w, h = 0, 0, 0, 0
                    face_feature = ''
                    scene_feature = ''
                    for feature in obj['features']:
                        if feature['type'] == 'face' and len(feature['value']) != 0:
                            idtofeature.append(
                                [object_id, feature['value'], image_id, image_path])
                            for num in feature['value']:
                                if face_feature != '':
                                    face_feature += (';'+str(num))
                                else:
                                    face_feature += str(num)
                            if 'tagFace' not in tagdict:
                                tagdict['tagFace'] = 1
                                vertex_write.writerow(
                                    ['tagFace', 'tag', 'Face'])
                            edge_write.writerow(
                                ['tagFace', bboxnodeid, 'edge'])
                        '''
                        if feature['type']=='scene':
                            # print 'scene',feature['value']
                            for num in feature['value']:
                                if scene_feature!='':
                                    scene_feature+=(';'+str(num))
                                else: scene_feature+=str(num)
                        '''
                    face_id = -1
                    vertex_write.writerow([bboxnodeid, 'bbox', x, y, w, h, object_id,
                                           face_featrank-order_distance_cluster.pyure, scene_feature, face_id])
                    tag = ''
                    if obj['name'][0].isupper():  # from tag model,like 'Tree'
                        tag = obj['name']
                    else:  # from relationship model,like 'tree1'
                        # help us find the corresponding bbox, when we build the relationship edge
                        boxname_to_id[obj['name']] = object_id
                        for i in range(len(obj['name'])):
                            if i == 0:
                                tag += obj['name'][i].upper()
                            else:
                                if obj['name'][i].isalpha():
                                    tag += obj['name'][i]
                    tagnodeid = 'tag'+tag
                    if tagnodeid not in tagdict:
                        tagdict[tagnodeid] = 1
                        vertex_write.writerow([tagnodeid, 'tag', tag])
                    if tag != 'Face':
                        # tagFace is added in feature step above
                        edge_write.writerow([tagnodeid, bboxnodeid, 'edge'])
                    edge_write.writerow([bboxnodeid, imagenodeid, 'edge'])
                    object_id += 1

            #print 'boxname_to_id:',boxname_to_id
            for obj in imagedata:
                if obj == 'status':
                    continue
                if len(obj['visual_relationships']) != 0:
                    for relationship, val in obj['visual_relationships']:
                        words = []  # divide the relationship 'pants3-on-person0' in to 3 parts
                        word = ''
                        for i in range(len(relationship)):
                            if relationship[i] != '-':
                                word += relationship[i]
                            else:
                                words.append(word)
                                word = ''
                        words.append(word)
                        relsubj_id = 'bbox'+str(boxname_to_id[words[0]])
                        relobj_id = 'bbox'+str(boxname_to_id[words[2]])
                        edge_write.writerow(
                            [relsubj_id, relobj_id, 'relationships', relationship_id, words[1]])
                        relationship_id += 1

            countrynodeid = 'country'+country
            if countrynodeid not in countrydict:
                countrydict[countrynodeid] = 1
                vertex_write.writerow([countrynodeid, 'country', country])
            if state == '':
                statenodeid = 'state of'+country
            else:
                statenodeid = 'state'+state
            if statenodeid not in statedict:
                statedict[statenodeid] = 1
                vertex_write.writerow([statenodeid, 'state', state])
            if city == '':
                citynodeid = 'city of'+state
            else:
                citynodeid = 'city'+city
            if citynodeid not in citydict:
                citydict[citynodeid] = 1
                vertex_write.writerow([citynodeid, 'city', city])

            edge_write.writerow([countrynodeid, statenodeid, 'edge'])
            edge_write.writerow([statenodeid, citynodeid, 'edge'])
            edge_write.writerow([citynodeid, imagenodeid, 'edge'])
            print image_id
            image_id += 1

    with open('cache/bbox_feature_image_path.json', 'w') as f:
        json.dump(idtofeature, f)
