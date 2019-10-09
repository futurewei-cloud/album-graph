import json
	
class Message:
    def __init__(self, code='', msg='', results=[]):
	self.code = code
	self.msg = msg
	self.res = results

    def to_json(self):
	return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))

class Result:
    def __init__(self, box=[], name='', score=0, features=[], sources=[], visual_rels=[]):
	self.box = box
	self.name = name
	self.score = score
	self.features = features
	self.visual_rels = visual_rels
	self.sources = sources

    def to_json(self):
	return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))

class Feature:
    def __init__(self, type='', value=[]):
	self.type = type
	self.value = value
    
    def to_json(self):
	return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))

if __name__=='__main__':
    f1 = Feature('face', [.1, .2, .3, .5, .0, .9, .4])
    f2 = Feature('scene', [1,2,3,4,5,6,5,4,3,2,1,0])
    res1 = Result([.1, .2, .5, .8], 'face', .9, [f1,f2], ['oic-object-detection'], [('shirt3-on-person0', 1.2381408)])
    res2 = Result([], 'Tie', .8, [], ['huawei-image-tagging'], [('shirt3-on-person0', 1.2381408)])
    message = Message('200', 'OK', [res1, res2])
    json_data = message.to_json()
    print(type(json_data))
    print(json_data)
    print(type(message.__dict__))
    print(message.__dict__)
