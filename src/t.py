import sys, json

from LoadBalancerRequest import *
import jsonpickle
import requests

import json


test = LoadBalancerRequest(name='foobar')

lbprops = LoadBalancerProperties()

#test.name = lbprops


# rv = json.dumps(test, sort_keys=True, indent=4, separators=(',', ';'))

rv = jsonpickle.encode(test, make_refs=False)

rv2 = test.to_JSON()

childstuff =  { 'achildstuff' : 'achild', 'anothermore': {'foo':'bar', 'fooa': 'bara'} }

test2 = { 
    'name' : 'foobar',
    'achild' : childstuff,
    'anotherc' : { 'deep1': 'thisisdeep', 'morechild' : childstuff }
    }


resp = requests.post('http://localhost:3000/echo', json=test2).json()

print unicode(resp)
#print 'rv2'
#print rv2

#print 'rv'
#print rv





