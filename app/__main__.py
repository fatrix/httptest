from httptest import func
import sys
import yaml

data_s = sys.stdin.read()
data = yaml.load(data_s)

self = func
self.info = lambda x, y: x
self.error = lambda x, y: x
self.warn = lambda x, y: x
self.debug = lambda x, y: x
self.rid = 1234

#data = {'tests': [{'name': 'test_skip', 'skip': True, 'asserts': {'assert_status_code_is': 200}, 'uri': '/'}, {'name': 'test_home', 'asserts': {'assert_status_code_is': 200}, 'uri': '/'}, {'name': 'test_fails', 'asserts': {'assert_status_code_is': 500}, 'uri': '/'}], 'environments': [{'name': 'sahli', 'base_url': 'https://sahli.net'}, {'name': 'httptest', 'base_url': 'https://www.example.com/'}]}
#import json
#print json.dumps(data)
version = 2
results, ssl_info, total_counter, success =  func(self, data, version, True)#
