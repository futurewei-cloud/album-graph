import urllib3
import json
import certifi
import os
import glob
import sys
import requests
import csv
import numpy as np

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import networkx as nx
import scipy


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
    my_graph_name = "photos_lin_feature"
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


class Face:
    """
    This is a data structure to store the faces and the relevant information to cluster it later on

    """

    def __init__(self, bboxid, feature, imageid, image_path,
                 absolute_distance_neighbours=None, rank_order_neighbours=None,
                 label=None):

        self.bboxid = bboxid
        self.image_path = image_path
        self.absolute_distance_neighbours = absolute_distance_neighbours
        self.rank_order_neighbours = rank_order_neighbours
        self.feature = feature
        self.imageid = imageid
        self.label = label

    def __str__(self):
        return("bboxid: {}\nimageid: {}\nLabel: {}".format(self.bboxid, self.imageid, self.label))


class Neighbour:
    def __init__(self, entity, distance):
        self.entity = entity
        self.distance = distance


# Create nearest neighbours list of absolute distance
def assign_absolute_distance_neighbours_for_faces(faces):
    for i, face1 in enumerate(faces):
        nearest_neighbour = []
        print 'faces:', i, '/', len(faces)
        for j, face2 in enumerate(faces):
            distance = np.linalg.norm(face1.feature - face2.feature, ord=1)
            neighbour = Neighbour(face2, distance)
            nearest_neighbour.append(neighbour)
        nearest_neighbour.sort(key=lambda x: x.distance)
        face1.absolute_distance_neighbours = nearest_neighbour


def find_rank_order(entity1, entity2):

    distance_entity1_entity2, num_neighbours_entity1 = find_asym_rank_order(
        entity1, entity2)
    distance_entity2_entity1, num_neighbours_entity2 = find_asym_rank_order(
        entity2, entity1)
    min_neighbours = min(num_neighbours_entity1, num_neighbours_entity2)
    return((distance_entity1_entity2 + distance_entity2_entity1)/min_neighbours)


def find_asym_rank_order(entity1, entity2):
    penalty = 0
    for i, neighbour1 in enumerate(entity1.absolute_distance_neighbours):
        #         print("i is: {}".format(i))
        for j, neighbour2 in enumerate(entity2.absolute_distance_neighbours):
            #             print("j is: {}".format(j))
            if neighbour1.entity is neighbour2.entity:
                #                 print("found match")
                #                 print("add penalty: {}".format(j))
                if j == 0:  # this means that we found the rank of entity2 in entity1's neighbouts
                    return(penalty, i + 1)
                else:
                    penalty += j
#         print("penalty is: {}".format(penalty))
    return(penalty, i+1)


def assign_rank_order(entities):
    for entity1 in entities:
        nearest_neighbours = []

        for entity2 in entities:

            # Get rank order distance between entity1 and face 2
            rank_order = find_rank_order(entity1, entity2)
            nearest_neighbours.append(Neighbour(entity2, rank_order))

        nearest_neighbours.sort(key=lambda x: x.distance)
        entity1.rank_order_neighbours = nearest_neighbours


def peek_at_top_k_neighbours_for_face(face, top_k):
    """
    Look at the first num_faces faces for each of the top_k nearest neighbours from the specified face
    """
    top_k = top_k if top_k < len(face.absolute_distance_neighbours) else len(
        face.absolute_distance_neighbours)

    f, ax = plt.subplots(1, top_k, figsize=(15, 15))

    for i, neighbour in enumerate(face.absolute_distance_neighbours[0:top_k]):
        if i == 0:
            ax[i].set_title("Original Cluster")
            ax[i].imshow(mpimg.imread(neighbour.entity.image_path))
        else:
            distance = str(np.around(neighbour.distance, 2))
            ax[i].set_title("L1 Distance: {}".format(distance))
            ax[i].imshow(mpimg.imread(neighbour.entity.image_path))
    plt.tight_layout()
    plt.show()


class Cluster:
    def __init__(self):
        self.faces = list()
        self.absolute_distance_neighbours = None
        self.rank_order_neighbours = None
        self.normalized_distance = None
        self.majority_face = None
        self.num_of_majority_face = None

    def faces_in_cluster(self):
        faces_dict = {}
        for face in self.faces:
            if face.bboxid not in faces_dict.keys():
                faces_dict[face.bboxid] = 1
            else:
                faces_dict[face.bboxid] += 1

        return(faces_dict)

    def debug(self):
        print("Faces in cluster:")
        for face in self.faces:
            print(face.name)

# Assigning each face to a cluster


def initial_cluster_creation(faces):
    clusters = []
    for face in faces:
        cluster = Cluster()
        cluster.faces.append(face)
        clusters.append(cluster)
    return(clusters)

# Now we need to find the nearest neighbours for each of the vectors
# Note here that even though it looks like it's O(N^4) it's only N(O^2) due to the fact
# we really are only iterating through the faces


def find_nearest_distance_between_clusters(cluster1, cluster2):
    nearest_distance = sys.float_info.max
    for face1 in cluster1.faces:
        for face2 in cluster2.faces:
            distance = np.linalg.norm(face1.feature - face2.feature, ord=1)

            if distance < nearest_distance:
                nearest_distance = distance

            # If there is a distance of 0 then there is no need to continue
            if distance == 0:
                return(0)
    return(nearest_distance)


def assign_absolute_distance_neighbours_for_clusters(clusters):
    for i, cluster1 in enumerate(clusters):
        nearest_neighbours = []
        for j, cluster2 in enumerate(clusters):
            distance = find_nearest_distance_between_clusters(
                cluster1, cluster2)
#             print("Calculating neighbour {}/{} for cluster {}".format(j + 1, len(faces), i + 1), end = "\r")

            neighbour = Neighbour(cluster2, distance)
            nearest_neighbours.append(neighbour)
        nearest_neighbours.sort(key=lambda x: x.distance)
        cluster1.absolute_distance_neighbours = nearest_neighbours


def peek_at_top_k_neighbours_for_cluster(cluster, top_k, num_faces):
    """
    Look at the first num_faces faces for each of the top_k nearest neighbours from the specified cluster
    """
    top_k = top_k if top_k < len(cluster.absolute_distance_neighbours) else len(
        cluster.absolute_distance_neighbours)
    num_faces = num_faces if 1 < num_faces else 2

    f, ax = plt.subplots(top_k, num_faces, figsize=(15, 15))

    for i, neighbour in enumerate(cluster.absolute_distance_neighbours[0:top_k]):
        for j, face_in_cluster in enumerate(neighbour.entity.faces[0:num_faces]):
            if i == 0:
                ax[i][j].set_title("Original Cluster")
                ax[i][j].imshow(mpimg.imread(face_in_cluster.image_path))
            else:
                distance = str(np.around(neighbour.distance, 2))
                ax[i][j].set_title("L1 Distance: {}".format(distance))
                ax[i][j].imshow(mpimg.imread(face_in_cluster.image_path))
    plt.tight_layout()
    plt.show()


def find_normalized_distance_between_clusters(cluster1, cluster2, K=9):
    all_faces_in_clusters = cluster1.faces + cluster2.faces
    normalized_distance = 0

    for face in all_faces_in_clusters:
        total_absolute_distance_for_top_K_neighbours = sum(
            [neighbour.distance for neighbour in face.absolute_distance_neighbours[0:K]])
#         print("Face: {}".format(face.name))
#         print("Total distance to top {}: {}".format(K, total_absolute_distance_for_top_K_neighbours))
        normalized_distance += total_absolute_distance_for_top_K_neighbours

#     print("Normalized distance: {}".format(normalized_distance))
    # Now average the distance
    K = min(len(face.absolute_distance_neighbours), K)
    normalized_distance = normalized_distance/K

    # then divide by all the faces in the cluster
    normalized_distance = normalized_distance/len(all_faces_in_clusters)
    normalized_distance = (1/normalized_distance) * \
        find_nearest_distance_between_clusters(cluster1, cluster2)
    return(normalized_distance)


def find_rank_order_distance_between_clusters(cluster1, cluster2):
    return(find_rank_order(cluster1, cluster2))


def find_clusters(faces, t=14, K=9):
    clusters = initial_cluster_creation(faces)
    assign_absolute_distance_neighbours_for_clusters(clusters)
    prev_cluster_number = len(clusters)
    num_created_clusters = prev_cluster_number
    is_initialized = False

    while (not is_initialized) or (num_created_clusters):
        print("Number of clusters in this iteration: {}".format(len(clusters)))
    #     print(clusters)

        G = nx.Graph()
        for cluster in clusters:
            G.add_node(cluster)
        num_pairs = sum(range(len(clusters) + 1))
        processed_pairs = 0

    #     Find the candidate merging pairs
        for i, cluster1 in enumerate(clusters):

            # Order does not matter of the clusters since rank_order_distance and normalized_distance is symmetric
            # so we can get away with only calculating half of the required pairs
            for j, cluster2 in enumerate(clusters[i:]):
                processed_pairs += 1
                print "Processed {}/{} pairs\n".format(
                    processed_pairs, num_pairs)
                # No need to merge with yourself
                if cluster1 is cluster2:
                    continue
                else:
                    normalized_distance = find_normalized_distance_between_clusters(
                        cluster1, cluster2, K)
                    if (normalized_distance >= 1):
                        continue
                    rank_order_distance = find_rank_order_distance_between_clusters(
                        cluster1, cluster2)
                    if (rank_order_distance >= t):
                        continue
                    G.add_edge(cluster1, cluster2)
        clusters = []
        for _clusters in nx.connected_components(G):
            new_cluster = Cluster()
            for cluster in _clusters:
                for face in cluster.faces:
                    new_cluster.faces.append(face)
            clusters.append(new_cluster)

        current_cluster_number = len(clusters)
        num_created_clusters = prev_cluster_number - current_cluster_number
        prev_cluster_number = current_cluster_number

        # Recalculate the distance between clusters
#         print("assigning absolute distances")
        assign_absolute_distance_neighbours_for_clusters(clusters)


#         for i, cluster in enumerate(clusters):
#             print("Cluster: {}".format(i))
#             print("Faces in cluster")
#             for face in cluster.faces:
#                 print(face.name)
#             print("Distances to other clusters")
#             for neighbour in cluster.absolute_distance_neighbours:
#                 print(neighbour.distance)

        # Count the number of faces
#         num_faces = 0
#         for cluster in clusters:
#             for face in cluster.faces:
#                 num_faces += 1
#         print("Number of faces: {}".format(num_faces))

        is_initialized = True

    # Now that the clusters have been created, separate them into clusters that have one face
    # and clusters that have more than one face
    unmatched_clusters = []
    matched_clusters = []

    for cluster in clusters:
        if len(cluster.faces) == 1:
            unmatched_clusters.append(cluster)
        else:
            matched_clusters.append(cluster)

    matched_clusters.sort(key=lambda x: len(x.faces), reverse=True)
    return(matched_clusters, unmatched_clusters)

# Show the faces in each cluster


def peek_at_biggest_k_clusters(clusters, num_clusters, num_faces):
    num_clusters = num_clusters if num_clusters < len(
        clusters) else len(clusters)
    num_faces = num_faces if 1 < num_faces else 2
    f, ax = plt.subplots(num_clusters, num_faces, figsize=(15, 15))
    for i, cluster in enumerate(matched_clusters[0:num_clusters]):
        imagedict = {}
        for j, face in enumerate(cluster.faces[0:num_faces]):
            if face.image_path not in imagedict:
                imagedict[face.image_path] = 1
                ax[i][j].set_title(
                    "Faces in cluster: {}".format(len(cluster.faces)))
                ax[i][j].imshow(mpimg.imread(face.image_path))
    plt.tight_layout()
    plt.show()

# Show the faces in cluster_i


def peek_at_biggest_k_clusters(clusters, cluster_i):
    f, ax = plt.subplots(4, 5, figsize=(15, 15))
    imagedict = {}
    print len(clusters[cluster_i].faces)
    for j, face in enumerate(clusters[cluster_i].faces):
        imagedict[face.image_path] = 1
        x = (j)/5
        y = (j) % 5
        ax[x][y].set_title("Faces in cluster: {}".format(
            len(clusters[cluster_i].faces)))
        ax[x][y].imshow(mpimg.imread(face.image_path))
        #print j, face.image_path,x,y
    plt.tight_layout()
    plt.show()


def face_clustering():
    with open('cache/bbox_feature_image_path.json', 'r') as f:
        id_feature_image = json.load(f)
    faces = []
    for d in id_feature_image:
        path = '/home/zz/album_graph_data/Lin'+d[3][36:]
        print path
        face = Face(int(d[0]), np.array(d[1]), int(d[2]), path)
        faces.append(face)
    assign_absolute_distance_neighbours_for_faces(faces)
    #f, ax = plt.subplots(1, 1, figsize = (15, 15))
    print faces[109].imageid, faces[109].bboxid
    matched_clusters, unmatched_clusters = find_clusters(faces, 14, 18)
    num_clusters = 2
    num_faces = 10
    for i, cluster in enumerate(matched_clusters):
        print i, len(cluster.faces)
        #peek_at_biggest_k_clusters(matched_clusters, i)
    #peek_at_biggest_k_clusters(matched_clusters, num_clusters, num_faces)
    return matched_clusters, unmatched_clusters, id_feature_image


def write_file(vertexdata_path, matched_clusters, unmatched_clusters, id_feature_image):
    # write data to vertex.csv
    vertexcsv_r = csv.reader(open(vertexdata_path, 'r'))
    vertexdata = []
    csvbbox_line_map = {}  # from bbox index to line index of vertexdata
    jsonbbox_line_map = {}  # from image index to line index of id_feature_image
    for lineindex, line in enumerate(vertexcsv_r):
        vertexdata.append(line)
        if line[1] == 'bbox':
            csvbbox_line_map[int(line[6])] = lineindex
    for lineindex, line in enumerate(id_feature_image):
        jsonbbox_line_map[int(line[0])] = lineindex
    for i, cluster in enumerate(matched_clusters):
        for face in cluster.faces:
            csvline_to_change = csvbbox_line_map[face.bboxid]
            vertexdata[csvline_to_change][9] = i

            jsonline_to_change = jsonbbox_line_map[face.bboxid]
            if len(id_feature_image[jsonline_to_change]) == 5:
                id_feature_image[jsonline_to_change][4] = i
            else:
                id_feature_image[jsonline_to_change].append(i)

    for i, cluster in enumerate(unmatched_clusters):
        for face in cluster.faces:
            csvline_to_change = csvbbox_line_map[face.bboxid]
            vertexdata[csvline_to_change][9] = -1

            jsonline_to_change = jsonbbox_line_map[face.bboxid]
            if len(id_feature_image[jsonline_to_change]) == 5:
                id_feature_image[jsonline_to_change][4] = i
            else:
                id_feature_image[jsonline_to_change].append(i)

    vertexcsv_w = csv.writer(open(vertexdata_path, 'w'))
    for line in vertexdata:
        vertexcsv_w.writerow(line)
    with open('./cache/bbox_feature_image_path_label.json', 'w') as f:
        json.dump(id_feature_image, f)


def upload_ges(token, matched_clusters, unmatched_clusters):
    # upload data to ges
    for i, cluster in enumerate(matched_clusters):
        for face in cluster.faces:
            query = "g.V().has('object_id','{}').property('cluster_id','{}')".format(face.bboxid, i)
            gremlin_action(token, query)
            print i
    for i, cluster in enumerate(unmatched_clusters):
        for face in cluster.faces:
            query = "g.V().has('object_id','{}').property('cluster_id','{}')".format(face.bboxid, -1)
            gremlin_action(token, query)
            print i


def add_face_layer(matched_clusters, unmatched_clusters):
    vertexcsv_r = csv.reader(open('cache/vertex_stable.csv', 'r'))
    edgecsv_r = csv.reader(open('cache/edge_stable.csv', 'r'))
    vertexcsv_w = csv.writer(open('cache/vertex_f.csv', 'w'))
    edgecsv_w = csv.writer(open('cache/edge_f.csv', 'w'))
    for lineindex, line in enumerate(vertexcsv_r):
        vertexcsv_w.writerow(line)
    for lineindex, line in enumerate(edgecsv_r):
        edgecsv_w.writerow(line)

    for i, cluster in enumerate(matched_clusters):
        facenodeid = 'face'+str(i)
        vertexcsv_w.writerow([facenodeid, 'face', i])
        for face in cluster.faces:
            bboxnodeid = 'bbox'+str(face.bboxid)
            edgecsv_w.writerow([facenodeid, bboxnodeid, 'edge'])

    facenodeid = 'face'+str(-1)
    vertexcsv_w.writerow([facenodeid, 'face', -1])
    for i, cluster in enumerate(unmatched_clusters):
        for face in cluster.faces:
            bboxnodeid = 'bbox'+str(face.bboxid)
            edgecsv_w.writerow([facenodeid, bboxnodeid, 'edge'])


if __name__ == "__main__":
    # get auth token
    token = get_auth_token()
    # print(token)
    matched_clusters, unmatched_clusters, id_feature_image = face_clustering()
    vertexdata_path = 'cache/vertex.csv'
    edgedata_path = 'cache/edge.csv'
    add_face_layer(matched_clusters, unmatched_clusters)
    write_file(vertexdata_path, matched_clusters,
               unmatched_clusters, id_feature_image)
    #upload_ges(token,matched_clusters, unmatched_clusters)

    # upload data to ges
    """
    for i,cluster in enumerate(matched_clusters):
        for face in cluster.faces:
            query = "g.V().has('object_id','{}').property('cluster_id','{}')".format(face.bboxid,i)
            gremlin_action(token,query)
            print i
    for i,cluster in enumerate(unmatched_clusters):
        for face in cluster.faces:
            query = "g.V().has('object_id','{}').property('cluster_id','{}')".format(face.bboxid,-1)
            gremlin_action(token,query)
            print i
    """
