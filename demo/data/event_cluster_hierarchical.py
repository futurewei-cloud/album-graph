import urllib3
import json
import certifi
import os
import csv
import requests
import datetime

from datetime import datetime
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.distance import cdist
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
import PIL.ExifTags
import PIL.Image
import matplotlib.cm as cm
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np


def get_auth_token():
    """get auth-token from ges.
    Args:

    Returns:
        token - auth-token from ges.
    """
    headers = {
        'Content-Type': 'text/plain;charset=UTF-8', }
    data = '{ \
        "auth": { \
          "identity": { \
            "methods": [ \
              "password" \
            ], \
            "password": { \
              "user": { \
                "name": "zheng_zhao", \
                "password": "ZhaoZheng0426", \
                "domain": { \
                  "name": "hwstaff_y00465251" \
                } \
              } \
            } \
          }, \
          "scope": { \
            "project": { \
              "id": "454add6b26d04f53ae5c593551acf1ff" \
          } \
        } \
      } \
    }'

    r = requests.post('https://iam.cn-north-1.myhuaweicloud.com/v3/auth/tokens',
                      headers=headers, data=data)

    # print(r.status_code)
    # print(r.headers)
    token = r.headers.get('X-Subject-Token')

    return token


def gremlin_action(token, query):
    """get the data from the specific gremlin action.
    Args:
        token - ges token.
        query - gremlin action from the user 
    Returns:
        output - data part from ges return.
    """
    http = urllib3.PoolManager(
        cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
    # Headers are how we pass through the token.
    headers = {"Content-Type": "application/json"}
    headers["X-Language"] = "en-us"
    headers["X-Auth-Token"] = token

    my_project_id = "454add6b26d04f53ae5c593551acf1ff"
    my_graph_id = "d12f493e-975b-40e2-b278-76da8fe964fc"  # photos_new
    my_graph_name = "photos_new"
    my_region = "ges.cn-north-1"

    # action = "start"
    # action = "stop"
    action = "execute-gremlin-query"
    base = "{}.myhuaweicloud.com".format(my_region)

    url = "https://{}/v1.0/{}/graphs/{}/action?action_id={}".format(
        base, my_project_id, my_graph_id, action)

    data = {"command": query}
    r = http.request("POST", url, headers=headers, body=json.dumps(data))
    output = json.loads(r.data)
    return output['data']


def get_cmap(n, name='hsv'):
    """ Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name."""
    return plt.cm.get_cmap(name, n)


def load_data(vertexdata_path):
    # read data from vertex.csv and cluster the events
    print "events clustering..."
    vertexcsv_r = csv.reader(open(vertexdata_path, 'r'))
    mindatediff = 999999
    mintimediff = 999999
    maxdatediff = 0
    maxtimediff = 0
    data = []
    time = []
    latitude = []
    longitude = []
    vertexdata = []
    for lineindex, line in enumerate(vertexcsv_r):
        vertexdata.append(line)
        if line[1] == 'image' and line[4] != '' and line[5] != '-999' and line[6] != '-999':
            #print line[3],line[4],line[5],line[6]
            #print '/home/zz/album_graph_data/photos/'+line[3][36:]
            if line[4][11:13] == '24':
                line[4] = line[4][:11]+'00'+line[4][13:]
            #print datetime.strptime(str(line[4]),"%Y/%m/%d %H:%M:%S")
            a = datetime.strptime(str(line[4]), "%Y/%m/%d %H:%M:%S")
            b = datetime.strptime(
                str("1970/01/01 00:00:00"), "%Y/%m/%d %H:%M:%S")
            if (a-b).days < mindatediff or ((a-b).days == mindatediff and (a-b).seconds <= mintimediff):
                mindatediff = (a-b).days
                mintimediff = (a-b).seconds
                mindate = a
            if (a-b).days >= maxdatediff and (a-b).seconds >= maxtimediff:
                maxdatediff = (a-b).days
                maxtimediff = (a-b).seconds
                maxdate = a
            # image_path,datetime,latitude,longitude,lineindex(for rewrite)
            data.append([line[3], a, float(line[5]),
                         float(line[6]), lineindex])
    # clear the data
    newdata = []
    rawdata = []
    for d in data:
        newdata.append([d[0], (d[1]-mindate).days +
                        float((d[1]-mindate).seconds)/(24*60*60), d[2], d[3]])
        time.append((d[1]-mindate).days +
                    float((d[1]-mindate).seconds)/(24*60*60))
        latitude.append(d[2])
        longitude.append(d[3])
        time_weight = 1
        latitude_weight = 10
        longitude_weight = 10
        rawdata.append([(d[1]-mindate).days+float((d[1]-mindate).seconds) /
                        (24*60*60)*time_weight, d[2]*latitude_weight, d[3]*longitude_weight])
    time = np.array(time)
    latitude = np.array(latitude)
    longitude = np.array(longitude)
    rawdata = np.array(rawdata)
    return vertexdata, data, time, latitude, longitude, rawdata


def hierarchical_clustering(rawdata):
    disMat = sch.distance.pdist(rawdata, 'euclidean')

    Z = sch.linkage(disMat, method='single')
    plt.figure(figsize=(10, 7))
    plt.title("events Dendograms")
    P = sch.dendrogram(Z)
    plt.show()
    clt_y = sch.fcluster(Z, t=1, criterion='distance')
    print clt_y
    return clt_y


def write_file(vertexdata_path, clt_y, data, vertexdata):
    for labelindex, label in enumerate(clt_y):
        vertexdata[data[labelindex][4]][8] = label

    vertexcsv_w = csv.writer(open(vertexdata_path, 'w'))
    for line in vertexdata:
        vertexcsv_w.writerow(line)


def add_event_layer(clt_y, data, vertexdata):
    vertexcsv_r = csv.reader(open('vertex_f.csv', 'r'))
    edgecsv_r = csv.reader(open('edge_f.csv', 'r'))
    vertexcsv_w = csv.writer(open('vertex.csv', 'w'))
    edgecsv_w = csv.writer(open('edge.csv', 'w'))
    eventdict = {}
    for lineindex, line in enumerate(vertexcsv_r):
        vertexcsv_w.writerow(line)
    for lineindex, line in enumerate(edgecsv_r):
        edgecsv_w.writerow(line)

    for labelindex, label in enumerate(clt_y):
        eventnodeid = 'event'+str(clt_y[labelindex])
        if eventnodeid not in eventdict:
            eventdict[eventnodeid] = 1
            vertexcsv_w.writerow([eventnodeid, 'event', clt_y[labelindex]])
        imagenodeid = vertexdata[data[labelindex][4]][0]
        edgecsv_w.writerow([eventnodeid, imagenodeid, 'edge'])


def upload_ges(token, clt_y, data, vertexdata):
    for labelindex, label in enumerate(clt_y):
        image_id = vertexdata[data[labelindex][4]][2]
        query = "g.V().has('image_id','{}').property('event_id','{}')".format(image_id, label)
        gremlin_action(token, query)
        print i


def result_plot(clt_y, data, latitude, longitude, time):
    colormap = {}
    color = []
    for i, label in enumerate(clt_y):
        #print label
        if label not in colormap:
            colormap[label] = 1
    cmap = get_cmap(len(colormap))
    for i, label in enumerate(clt_y):
        color.append(cmap(label))
        data[i].append(label)
    data.sort(key=lambda x: x[4])
    clusters = {}
    for d in data:
        if d[5] not in clusters:
            clusters[d[5]] = []
        clusters[d[5]].append(d[0])
    # plot image
    for k in clusters:
        print k, clusters[k]
        f, ax = plt.subplots(4, 5, figsize=(15, 15))
        for j, path in enumerate(clusters[k]):
            if j > 19:
                break
            path = '/home/zz/album_graph_data/Lin/'+path[33:]
            x = (j)/5
            y = (j) % 5
            ax[x][y].set_title("images in cluster: {}".format(k))
            ax[x][y].imshow(mpimg.imread(path))
            #print j, face.image_path,x,y
        plt.tight_layout()
        plt.show()

    color = np.array(color)
    fig4 = plt.figure()
    ax4 = plt.axes(projection='3d')
    ax4.set_xlabel('latitude')
    ax4.set_ylabel('longitude')
    ax4.set_zlabel('time')
    xx = latitude
    yy = longitude
    zz = time

    ax4.scatter(xx, yy, zz, alpha=0.3, c=color)
    plt.show()


def event_cluster(vertexdata_path):
    vertexdata, data, time, latitude, longitude, rawdata = load_data(
        vertexdata_path)
    clt_y = hierarchical_clustering(rawdata)

    add_event_layer(clt_y, data, vertexdata)
    # write to the csv file
    write_file(vertexdata_path, clt_y, data, vertexdata)
    # upload_ges(token,clt_y,data,vertexdata)
    # plot part
    # result_plot(clt_y,data,latitude,longitude,time)


if __name__ == "__main__":
    token = get_auth_token()
    event_cluster('cache/vertex.csv')
    """
    with open('../seatle2/bbox_feature_image_path_label.json','r') as f:
        id_feature_image=json.load(f)
    """
