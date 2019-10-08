import urllib3
import json
import certifi
import os
import requests
import argparse
from datetime import datetime

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


def search_tagalbum(g, tag, dataset):
    """search the image with the specific tag from the albumgraph.
    Args:
        g - graph from gremlin server
        tag - image tag user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        tag_album - an album of images with same tag.
    """
    print "searching for: ", tag
    tag_album = {}
    image_id = g.V().has('tag_id', tag).out().hasLabel(
        'bbox').out().hasLabel('image').values('image_id').toList()
    image_path = g.V().has('tag_id', tag).out().hasLabel(
        'bbox').out().hasLabel('image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in tag_album:
            tag_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]

    return tag_album


def search_modelalbum(g, model, dataset):
    """search the image with the specific model from the albumgraph.
    Args:
        g - graph from gremlin server
        model - the model user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        model_album - an album of images with same model.
    """
    print "searching for: ", model
    model_album = {}
    image_id = g.V().has('model_id', model).out().hasLabel(
        'image').values('image_id').toList()
    image_path = g.V().has('model_id', model).out().hasLabel(
        'image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in model_album:
            model_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return model_album


def search_countryalbum(g, country, dataset):
    """search the image with the specific country from the albumgraph.
    Args:
        g - graph from gremlin server
        country - the country user want    
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        country_album - an album of images with same country.
    """
    print "searching for: ", country
    country_album = {}
    image_id = g.V().has('country_id', country).out().hasLabel('state').out(
    ).hasLabel('city').out().hasLabel('image').values('image_id').toList()
    image_path = g.V().has('country_id', country).out().hasLabel('state').out(
    ).hasLabel('city').out().hasLabel('image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in country_album:
            country_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return country_album


def search_statealbum(g, state, dataset):
    """search the image with the specific state from the albumgraph.
    Args:
        g - graph from gremlin server
        state - the state user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        state_album - an album of images with same state.
    """
    print "searching for: ", state
    state_album = {}
    image_id = g.V().has('state_id', state).out().hasLabel(
        'city').out().hasLabel('image').values('image_id').toList()
    image_path = g.V().has('state_id', state).out().hasLabel(
        'city').out().hasLabel('image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in state_album:
            state_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return state_album


def search_cityalbum(g, city, dataset):
    """search the image with the specific city from the albumgraph.
    Args:
        g - graph from gremlin server
        city - the city user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        city_album - an album of images with same city.
    """
    print "searching for: ", city
    city_album = {}
    image_id = g.V().has('city_id', city).out().hasLabel(
        'image').values('image_id').toList()
    image_path = g.V().has('city_id', city).out().hasLabel(
        'image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in city_album:
            city_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return city_album


def search_facealbum(g, face, dataset):
    """search the image with the face_id from the albumgraph.
    Args:
        g - graph from gremlin server
        face - the face_id user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        face_album - an album of images with same face_id.
    """
    print "searching for: ", face
    face_album = {}
    face = int(face)
    image_id = g.V().has('face_id', face).out().hasLabel(
        'image').values('image_id').toList()
    image_path = g.V().has('face_id', face).out().hasLabel(
        'image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in face_album:
            face_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return face_album


def search_eventalbum(g, event, dataset):
    """search the image with the event_id from the albumgraph.
    Args:
        g - graph from gremlin server
        event - the event_id user want 
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        event_album - an album of images with same event_id.
    """
    print "searching for: ", event
    event_album = {}
    event = int(event)
    image_id = g.V().has('event_id', event).values('image_id').toList()
    image_path = g.V().has('event_id', event).values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in event_album:
            event_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return event_album


def search_allmodels(g, dataset):
    """return all the models uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        modellist - a list of differnt models .
    """
    print "searching for models: "
    modellist = []
    modellist = g.V().hasLabel('model').values('model_id').toList()
    print modellist
    return modellist


def search_alltags(g, dataset):
    """return all the tags uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        taglist - a list of differnt tags .
    """
    print "searching for tags: "
    taglist = []
    taglist = g.V().hasLabel('tag').values('tag_id').toList()
    print taglist
    return taglist


def search_allcities(g, dataset):
    """return all the cities uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        citylist - a list of differnt cities .
    """
    print "searching for citys: "
    citylist = []
    citylist = g.V().hasLabel('city').values('city_id').toList()
    print citylist
    return citylist


def search_allstates(g, dataset):
    """return all the states uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        statelist - a list of differnt states .
    """
    print "searching for states: "
    statelist = []
    statelist = g.V().hasLabel('state').values('state_id').toList()
    print statelist
    return statelist


def search_allcountries(g, dataset):
    """return allcountries uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        countrylist - a list of differnt countries .
    """
    print "searching for countries: "
    countrylist = []
    countrylist = g.V().hasLabel('country').values('country_id').toList()
    print countrylist
    return countrylist


def search_allsemanticwords(g, dataset):
    """return all the predicates uesd in the albumgraph.
    Args:
        g - graph from gremlin server
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        taglist - a list of differnt tags .
    """
    print "searching for predicates: "
    result = {}
    predicatelist = []
    predicate = g.E().hasLabel('relationships').values('predicate').toList()
    for p in predicate:
        if p not in predicatelist:
            predicatelist.append(p)

    subjlist = []
    subj = g.E().hasLabel('relationships').outV(
    ).in_().hasLabel('tag').values('tag_id').toList()
    for s in subj:
        if s not in subjlist:
            subjlist.append(s)

    objlist = []
    obj = g.E().hasLabel('relationships').inV().in_().hasLabel(
        'tag').values('tag_id').toList()
    for o in obj:
        if o not in objlist:
            objlist.append(o)
    result = {'subjects': subjlist,
              'predicates': predicatelist, 'objects': objlist}
    print result
    return result


def search_allrelationships(g, dataset):
    """search the semantic relationships  from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        relationshiplist - a list of relationships for all image.
    """
    print "searching for: allrelationships"
    relationshiplist = []
    relationship = g.V().in_().as_('bbox1').in_().hasLabel('tag').values('tag_id').as_('tag1').select('bbox1').outE('relationships').as_('edge').values('predicate').as_('p')\
        .select('edge').inV().in_().hasLabel('tag').values('tag_id').as_('tag2').select('tag1', 'p', 'tag2').toList()
    for r in relationship:
        tag1 = r['tag1']
        predicate = r['p']
        tag2 = r['tag2']
        if tag1 == 'Face' or tag2 == 'Face':
            continue
        if [tag1, predicate, tag2] not in relationshiplist:
            relationshiplist.append([tag1, predicate, tag2])
    print relationshiplist
    return relationshiplist


def search_tag(g, img, dataset):
    """search the tag of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        taglist - a list of tags for this image.
    """
    #print "searching for: ",img
    taglist = []
    img = int(img)
    tag = g.V().has('image_id', img).in_().hasLabel(
        'bbox').in_().hasLabel('tag').values('tag_id').toList()
    for i in range(len(tag)):
        if tag[i] not in taglist:
            taglist.append(tag[i])
            print tag[i]
    return taglist


def search_model(g, img, dataset):
    """search the model of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        modellist - a list of tags for this image.
    """
    print "searching for: ", img
    img = int(img)
    modellist = []
    model = g.V().has('image_id', img).in_().hasLabel(
        'model').values('model_id').toList()
    for i in range(len(model)):
        if model[i] not in modellist:
            modellist.append(model[i])
            print model[i]
    return modellist


def search_relationship(g, img, dataset):
    """search the semantic relationships of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        relationshiplist - a list of relationships for this image.
    """
    #print "searching for: ",img
    img = int(img)
    relationshiplist = []
    relationship = g.V().has('image_id', img).in_().as_('bbox1').in_().hasLabel('tag').values('tag_id').as_('tag1').select('bbox1').outE('relationships').as_('edge').values('predicate').as_('p')\
        .select('edge').inV().in_().hasLabel('tag').values('tag_id').as_('tag2').select('tag1', 'p', 'tag2').toList()
    for r in relationship:
        tag1 = r['tag1']
        predicate = r['p']
        tag2 = r['tag2']
        if tag1 == 'Face' or tag2 == 'Face':
            continue
        if [tag1, predicate, tag2] not in relationshiplist:
            relationshiplist.append([tag1, predicate, tag2])
    #print relationshiplist
    return relationshiplist


def search_bbox(g, img, dataset):
    """search the bboxs of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        bboxlist - a list of bboxs for this image.
    """
    print "searching for: ", img
    img = int(img)
    bboxlist = []
    x = g.V().has('image_id', img).in_().hasLabel('bbox').values('x').toList()
    y = g.V().has('image_id', img).in_().hasLabel('bbox').values('y').toList()
    w = g.V().has('image_id', img).in_().hasLabel('bbox').values('w').toList()
    h = g.V().has('image_id', img).in_().hasLabel('bbox').values('h').toList()
    for i in range(len(x)):
        bboxlist.append({'x': x[i], 'y': y[i], 'w': w[i], 'h': h[i]})
    print bboxlist
    return bboxlist


def search_city(g, img, dataset):
    """search the city of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        citylist - a list of citys for this image.
    """
    print "searching for: ", img
    img = int(img)
    citylist = []
    city = g.V().has('image_id', img).in_().hasLabel(
        'city').values('city_id').toList()
    for i in range(len(city)):
        if city[i] not in citylist:
            citylist.append(city[i])
    print citylist
    return citylist


def search_state(g, img, dataset):
    """search the state of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        statelist - a list of states for this image.
    """
    print "searching for: ", img
    img = int(img)
    statelist = []
    state = g.V().has('image_id', img).in_().hasLabel(
        'city').in_().hasLabel('state').values('state_id').toList()
    for i in range(len(state)):
        if state[i] not in statelist:
            statelist.append(state[i])
    print statelist
    return statelist


def search_country(g, img, dataset):
    """search the country of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        countrylist - a list of countrys for this image.
    """
    print "searching for: ", img
    countrylist = []
    img = int(img)
    country = g.V().has('image_id', img).in_().hasLabel('city').in_().hasLabel(
        'state').in_().hasLabel('country').values('country_id').toList()
    for i in range(len(country)):
        if country[i] not in countrylist:
            countrylist.append(country[i])
    print countrylist
    return countrylist


def search_datetime(g, img, dataset):
    """search the datetime of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        datetime - datetime of this image.
    """
    print "searching for: ", img
    img = int(img)
    datetime = g.V().has('image_id', img).values('datetime').toList()
    print datetime
    return datetime


def search_gps(g, img, dataset):
    """search the gps of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        gps - gps of this image.
    """
    print "searching for: ", img
    img = int(img)
    latitude = g.V().has('image_id', img).values('latitude').toList()
    longitude = g.V().has('image_id', img).values('longitude').toList()
    result = [latitude, longitude]
    print result
    return result


def search_allimginfo(g, img, dataset):
    """search the gps of image from the albumgraph.
    Args:
        g - graph from gremlin server
        img - image tag user want(img_id)
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        gps - gps of this image.
    """
    print "searching for: ", img
    result = {}
    img = int(img)
    result['image_id'] = g.V().has('image_id', img).values('image_id').toList()
    result['image_path'] = g.V().has(
        'image_id', img).values('image_path').toList()
    result['datetime'] = g.V().has('image_id', img).values('datetime').toList()
    result['latitude'] = g.V().has('image_id', img).values('latitude').toList()
    result['longitude'] = g.V().has(
        'image_id', img).values('longitude').toList()
    result['address'] = g.V().has('image_id', img).values('address').toList()
    result['event_id'] = g.V().has('image_id', img).values('event_id').toList()
    result['tag'] = search_tag(g, img, dataset)
    result['model'] = search_model(g, img, dataset)
    result['city'] = search_city(g, img, dataset)
    result['state'] = search_state(g, img, dataset)
    result['country'] = search_country(g, img, dataset)
    print result
    return result


def search_gpsalbum(g, gpsrange, dataset):
    """search the image with the specific gps range from the albumgraph.
    Args:
        g - graph from gremlin server
        gpsrange - gps range user want [[latitude_lb,latitude_ub],[longitude_lb,longitude_ub]]
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        gps_album - an album of images with same tag.
    """
    print "searching for: ", gpsrange
    gps_album = {}
    image_id = g.V().has('latitude', P.inside(gpsrange[0][0], gpsrange[0][1])).has(
        'longitude', P.inside(gpsrange[1][0], gpsrange[1][1])).values('image_id').toList()
    image_path = g.V().has('latitude', P.inside(gpsrange[0][0], gpsrange[0][1])).has(
        'longitude', P.inside(gpsrange[1][0], gpsrange[1][1])).values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in gps_album:
            gps_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return gps_album


def search_timealbum(g, timerange, dataset):
    """search the image with the specific timerange from the albumgraph.
    Args:
        g - graph from gremlin server
        time - time user want ('2017','2017:03','2017:03:31')
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        time_album - an album of images with same tag.
    """
    print "searching for: ", timerange
    time_album = {}
    image_id = g.V().has('datetime', P.inside(
        timerange[0], timerange[1])).values('image_id').toList()
    image_path = g.V().has('datetime', P.inside(
        timerange[0], timerange[1])).values('datetime').order().toList()
    for i in range(len(image_id)):
        if image_id[i] not in time_album:
            time_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return time_album


def search_semanticalbum(g, semantic_pair, dataset):
    """search the image with the specific description from the albumgraph.
    Args:
        g - graph from gremlin server
        semantic_pair - semantic_pair user want ('Pants','on','Person')
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        semantic_album - an album of images with same tag.
    """
    print "searching for: ", semantic_pair
    semantic_album = {}
    image_id = g.V().has('tag_id', semantic_pair[0]).out().outE().has('predicate', semantic_pair[1]).inV().as_('T').in_(
    ).hasLabel('tag').has('tag_id', semantic_pair[2]).select('T').out().hasLabel('image').values('image_id').toList()
    image_path = g.V().has('tag_id', semantic_pair[0]).out().outE().has('predicate', semantic_pair[1]).inV().as_('T').in_(
    ).hasLabel('tag').has('tag_id', semantic_pair[2]).select('T').out().hasLabel('image').values('image_path').toList()
    for i in range(len(image_id)):
        if image_id[i] not in semantic_album:
            semantic_album[image_id[i]] = image_path[i]
            print image_id[i], image_path[i]
    return semantic_album


def entities_timeline(g, timerange, dataset):
    result = []

    person_count = g.V().has('face_id', P.gte(0)).order().by('face_id', Order.desc)\
        .values('face_id').limit(1).toList()[0]+1
    print person_count
    for i in range(person_count):
        image_id = g.V().has('face_id', i).out().hasLabel('image')\
            .has('datetime', P.inside(timerange[0], timerange[1])).order().by('datetime', Order.asc)\
            .dedup().valueMap().toList()
        if len(image_id) != 0:
            result.append(image_id)
    print 'sad', result
    tags = g.V().hasLabel('tag').values('tag_id').toList()
    for tag in tags:
        print tag
        image_id = g.V().has('tag_id', tag).out().hasLabel('bbox').out().hasLabel('image')\
            .has('datetime', P.inside(timerange[0], timerange[1])).order().by('datetime', Order.asc)\
            .dedup().valueMap().toList()
        if len(image_id) != 0:
            result.append(image_id)
    print 'sadd', {'nodes': result}
    return result


def albumgraph(g, dataset):
    result = {'nodes': [], 'links': []}
    nodes = g.V().valueMap().toList()

    # image nodes
    imagenodes = g.V().hasLabel('image').valueMap().toList()
    for node in imagenodes:
        newnode = {}
        node.pop('event_id')
        node['label'] = 'image'
        result['nodes'].append(node)

    # tag nodes
    tagnodes = g.V().hasLabel('tag').valueMap().toList()
    for node in tagnodes:
        node['label'] = 'tag'
        result['nodes'].append(node)

    # model nodes
    modelnodes = g.V().hasLabel('model').valueMap().toList()
    for node in modelnodes:
        node['label'] = 'model'
        result['nodes'].append(node)

    # location nodes
    citynodes = g.V().hasLabel('city').valueMap().toList()
    for node in citynodes:
        node['label'] = 'location'
        node['type'] = 'city'
        result['nodes'].append(node)
    statenodes = g.V().hasLabel('state').valueMap().toList()
    for node in statenodes:
        node['label'] = 'location'
        node['type'] = 'state'
        result['nodes'].append(node)
    countrynodes = g.V().hasLabel('country').valueMap().toList()
    for node in countrynodes:
        node['label'] = 'location'
        node['type'] = 'country'
        result['nodes'].append(node)

    # face nodes
    facenodes = g.V().hasLabel('bbox').valueMap().toList()
    facedict = {}
    for node in facenodes:
        newnode = {}
        if node['face_id'][0] not in facedict:
            facedict[node['face_id'][0]] = 1
            newnode['label'] = 'face'
            newnode['face_id'] = node['face_id'][0]
            newnode['id'] = 'face'+str(node['face_id'][0])
            result['nodes'].append(newnode)

    # event nodes
    eventnodes = g.V().hasLabel('image').valueMap().toList()
    eventdict = {}
    for node in eventnodes:
        newnode = {}
        if node['event_id'][0] not in eventdict:
            eventdict[node['event_id'][0]] = 1
            newnode['label'] = 'event'
            newnode['event_id'] = node['event_id'][0]
            newnode['id'] = 'event'+str(node['event_id'][0])
            result['nodes'].append(newnode)

    # realtionship nodes
    images_num = g.V().hasLabel('image').count().toList()[0]
    relationshipdict = {}
    newnode = {}
    for i in range(images_num):
        newnode = {}
        relationships = search_relationship(g, i, dataset)
        if len(relationships) != 0:
            for r in relationships:
                s = r[0]+r[1]+r[2]
                if s not in relationshipdict:
                    relationshipdict[s] = len(relationshipdict)
                    newnode['id'] = 'relationship'+str(relationshipdict[s])
                    newnode['label'] = 'relationship'
                    newnode['subject'] = r[0]
                    newnode['predicate'] = r[1]
                    newnode['object'] = r[2]
                    result['nodes'].append(newnode)

    print result
    return result


def pagerank(g,dataset):
    """get data with pagerank algorithm from the albumgraph.
    Args:
        g - graph from gremlin server
        alpha -
        convergence -
        max_iterations -
        directed -
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        data - 
    """
    print "using pagerank: "
    algorithm='{\
                 "algorithmName":"pagerank",\
                 "parameters":{\
                        "alpha":0.85,\
                        "convergence":0.00001,\
                        "max_iterations":1000,\
                        "directed":true\
                 }\
                }'

    job_id=algorithm_action(g,algorithm,dataset)
    data=check_job(g,job_id,dataset,0,2)
    print data
    return data


def realtime_recommendation(g,arg,dataset):
    """get data with pagerank algorithm from the albumgraph.
    Args:
        g - graph from gremlin server
        
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        data - 
    """
    print "realtime_recommendation: "
    algorithm = "{{'algorithmName':'realtime_recommendation','parameters':{{'sources':'{}','alpha':0.85,'N':10000,'nv':5,'np':1000,'label':'image','directed':false }} }}".format('tag'+arg[0])
    recommendation_album={}
    if int(arg[1])==0:return recommendation_album
    job_id=algorithm_action(g,algorithm,dataset)
    jobdata=check_job(g,job_id,dataset,0,int(arg[1]))
    
    if 'errorCode' in jobdata: return recommendation_album
    data=jobdata['data']['outputs']['score']
    print "jobdata",data
    vertices=[]
    for i in data: #{image_id:score}
        for ID in i:#image_id
            vertices.append(ID)

    data=vertices_action(g,vertices)
    if 'vertices' not in data: return recommendation_album
    for image in data['vertices']:
        image_id=image['properties']['image_id'][0]
        image_path=image['properties']['image_path'][0]
        if image_id not in recommendation_album: 
            recommendation_album[image_id]=image_path
            print image_id,image_path
    return recommendation_album


def personalrank(g,dataset):
    """get data with pagerank algorithm from the albumgraph.
    Args:
        g - graph from gremlin server
        alpha -
        convergence -
        max_iterations -
        directed -
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        data - 
    """
    print "using personalrank: "
    algorithm='{\
                 "algorithmName":"personalrank",\
                 "parameters":{\
                        "source":"tagTree",\
                        "alpha":0.85,\
                        "convergence":0.00001,\
                        "max_iterations":1000,\
                        "directed":false\
                 }\
                }'

    job_id=algorithm_action(g,algorithm,dataset)
    data=check_job(g,job_id,dataset,0,10)
    print data
    return data


def pagerank(g,dataset):
    """get data with pagerank algorithm from the albumgraph.
    Args:
        g - graph from gremlin server
        alpha -
        convergence -
        max_iterations -
        directed -
        dataset- 'l' for large dataset, 's' for small dataset
    Returns:
        data - 
    """
    print "using pagerank: "
    algorithm='{\
                 "algorithmName":"pagerank",\
                 "parameters":{\
                        "alpha":0.85,\
                        "convergence":0.00001,\
                        "max_iterations":1000,\
                        "directed":true\
                 }\
                }'

    job_id=algorithm_action(g,algorithm,dataset)
    data=check_job(g,job_id,dataset,0,2)
    print data
    return data


def get_result(need, arg, dataset):
    print ('creating g ...')
    g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))
    print ('creating g done')
    if need == 'img':
        if arg[0] == 'tag':
            return search_tag(g, arg[1], dataset)
        if arg[0] == 'model':
            return search_model(g, arg[1], dataset)
        if arg[0] == 'bbox':
            return search_bbox(g, arg[1], dataset)
        if arg[0] == 'datetime':
            return search_datetime(g, arg[1], dataset)
        if arg[0] == 'gps':
            return search_gps(g, arg[1], dataset)
        if arg[0] == 'relationships':
            return search_relationship(g, arg[1], dataset)
        if arg[0] == 'allimginfo':
            return search_allimginfo(g, arg[1], dataset)
    if need == 'tag':
        return search_tagalbum(g, arg, dataset)
    if need == 'model':
        return search_modelalbum(g, arg, dataset)
    if need == 'date':
        return search_timealbum(g, arg, dataset)
    if need == 'country':
        return search_countryalbum(g, arg, dataset)
    if need == 'state':
        return search_statealbum(g, arg, dataset)
    if need == 'city':
        return search_cityalbum(g, arg, dataset)
    if need == 'cluster':
        return search_facealbum(g, arg, dataset)
    if need == 'num_events':
        return set_events_num(g, arg, dataset)
    if need == 'event':
        return search_eventalbum(g, arg, dataset)
    if need == 'semantic':
        return search_semanticalbum(g, arg, dataset)
    if need == 'recommendation':
        return realtime_recommendation(g, arg, dataset)
    if need == 'gpsrange':
        return search_gpsalbum(g, [[arg[0][0], arg[0][1]], [arg[1][0], arg[1][1]]], dataset)
    if need == 'allmodels':
        return search_allmodels(g, dataset)
    if need == 'allrelationships':
        return search_allrelationships(g, dataset)
    if need == 'alltags':
        return search_alltags(g, dataset)
    if need == 'allcities':
        return search_allcities(g, dataset)
    if need == 'allstates':
        return search_allstates(g, dataset)
    if need == 'allcountries':
        return search_allcountries(g, dataset)
    if need == 'allsemanticwords':
        return search_allsemanticwords(g, dataset)
    if need == 'entities':
        return entities_timeline(g, arg, dataset)
    if need == 'albumgraph':
        return albumgraph(g, dataset)
    print 'get result'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset', default='s', help='choose dataset: s(200 images),l(4366images)')
    parser.add_argument('--img', help='input image_id')
    parser.add_argument('--tag', help='input tag_id :"Person","Tree",....')
    args = parser.parse_args()
    dataset = args.dataset
    # get graph from gremlin graph
    g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))
    print g.V().count().toList()
    # search_tagalbum(g,'Tree',dataset)
    #search_modelalbum(g,'iPhone 6s Plus',dataset)
    #search_countryalbum(g,'United States of America',dataset)
    # search_statealbum(g,'Washington',dataset)
    # search_cityalbum(g,'Seattle',dataset)
    search_facealbum(g, 1, dataset)
    # search_eventalbum(g,'1',dataset)
    # search_allmodels(g,dataset)
    # search_allsemanticwords(g,dataset)
    # search_allrelationships(g,dataset)
    # search_tag(g,'1',dataset)
    # search_bbox(g,'21',dataset)
    # search_city(g,'1',dataset)
    # search_state(g,'1',dataset)
    # search_country(g,'1',dataset)
    # search_datetime(g,'1',dataset)
    # search_gps(g,'1',dataset)
    # search_allimginfo(g,'145',dataset)
    # search_gpsalbum(g,[[46,47],[-123,-120]],dataset)
    #search_timealbum(g,['2015/01/01 00:00:00','2019/06/01 00:00:00'],dataset)
    # search_semanticalbum(g,['Sky','above','Grass'],dataset)
    # entities_timeline(g,['2010/01/01','2019/06/01'],dataset)
    # albumgraph(g,dataset)

    # search_facealbum(g,1,dataset)
    # vertices_action(g,vertices)
    # set_events_num(g,5,dataset)
    # search_allmodels(g,dataset)
    #search_modelalbum(g,'iPhone 6s Plus',dataset)
    # search_timealbum(g,'2017:03',dataset)
    # search_timealbum(g,'2017:03:31',dataset)
    # pagerank(g,dataset)
    # realtime_recommendation(g,'Person',dataset)
    # personalrank(g,dataset)
    # search_gpsalbum(g,[[45,47],[-123,-122]],dataset)
    # search_datetime(g,45,dataset)
    # search_gps(g,45,dataset)

    # get_similar_face(g,188,dataset)
    #print search_relationship(g,121,dataset)
    #print search_allsemanticwords(g,dataset)
