""" Insert the processed data into gremlin database """

from gremlin_python import statics
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T
from gremlin_python.process.traversal import Order
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Column
from gremlin_python.process.traversal import Direction
from gremlin_python.process.traversal import Operator
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import Pop
from gremlin_python.process.traversal import Scope
from gremlin_python.process.traversal import Barrier
from gremlin_python.process.traversal import Bindings
from gremlin_python.process.traversal import WithOptions

import csv

if __name__ == '__main__':
    g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

    g.V().drop().iterate()
    g.E().drop().iterate()
    print g.V().count().toList()

    vertexcsv_r = csv.reader(open('cache/vertex.csv', 'r'))
    edgecsv_r = csv.reader(open('cache/edge.csv', 'r'))

    for lineindex, line in enumerate(vertexcsv_r):
        if line[1] == 'image':
            g.addV('image').property('id', line[0]).property('gcnid', lineindex).property('image_id', int(line[2]))\
                .property('image_path', line[3]).property('datetime', line[4])\
                .property('latitude', float(line[5])).property('longitude', float(line[6]))\
                .property('address', line[7]).property('event_id', int(line[8])).iterate()
            #print g.V().has('image_id',line[2]).valueMap().toList()

        if line[1] == 'bbox':
            g.addV('bbox').property('id', line[0]).property('gcnid', lineindex).property('x', float(line[2]))\
                .property('y', float(line[3])).property('w', float(line[4]))\
                .property('h', float(line[5])).property('object_id', float(line[6]))\
                .property('face_feature', str(line[7])).property('scene_feature', str(line[8]))\
                .property('face_id', int(line[9])).iterate()
            #print g.V().has('object_id',line[6]).valueMap().toList()

        if line[1] == 'tag':
            g.addV('tag').property('id', line[0]).property(
                'gcnid', lineindex).property('tag_id', line[2]).iterate()
            #print g.V().has('tag_id',line[2]).valueMap().toList()

        if line[1] == 'model':
            g.addV('model').property('id', line[0]).property(
                'gcnid', lineindex).property('model_id', line[2]).iterate()
            #print g.V().has('tag_id',line[2]).valueMap().toList()

        if line[1] == 'country':
            g.addV('country').property('id', line[0]).property(
                'gcnid', lineindex).property('country_id', line[2]).iterate()
            #print g.V().has('tag_id',line[2]).valueMap().toList()

        if line[1] == 'state':
            g.addV('state').property('id', line[0]).property(
                'gcnid', lineindex).property('state_id', line[2]).iterate()
            #print g.V().has('tag_id',line[2]).valueMap().toList()

        if line[1] == 'city':
            g.addV('city').property('id', line[0]).property(
                'gcnid', lineindex).property('city_id', line[2]).iterate()
            #print g.V().has('tag_id',line[2]).valueMap().toList()

        if line[1] == 'face':
            g.addV('face').property('id', line[0]).property(
                'gcnid', lineindex).property('facenode_id', line[2]).iterate()

        if line[1] == 'event':
            g.addV('event').property('id', line[0]).property(
                'gcnid', lineindex).property('eventnode_id', line[2]).iterate()

    edgedict = {}
    for lineindex, line in enumerate(edgecsv_r):
        print line[0]
        stringline = ''
        for l in line:
            stringline += l

        if stringline not in edgedict:
            edgedict[stringline] = 1
            if line[2] == 'edge':
                g.V().has('id', line[0]).as_('a').V().has('id', line[1]).as_('b')\
                    .addE('edge').from_('a').to('b').iterate()
            else:
                g.V().has('id', line[0]).as_('a').V().has('id', line[1]).as_('b')\
                    .addE('relationships').from_('a').to('b')\
                    .property('relationship_id', line[3]).property('predicate', line[4]).iterate()
        print g.E().count().toList()

    print g.V().count().toList()
    print g.E().count().toList()
