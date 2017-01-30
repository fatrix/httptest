import os

def func(self, data, version, response_obj=None):
    """
    >>> self = func
    >>> self.info = lambda x, y: x
    >>> self.error = lambda x, y: x
    >>> self.warn = lambda x, y: x
    >>> self.debug = lambda x, y: x
    >>> self.rid = 1234
    >>> data = {'tests': [{'name': 'test_home', 'asserts': {'assert_status_code_is': 200}, 'uri': '/'}, {'name': 'test_fails', 'asserts': {'assert_status_code_is': 500}, 'uri': '/'}], 'environments': [{'name': 'sahli', 'base_url': 'https://sahli.net'}, {'name': 'httptest', 'base_url': 'https://www.example.com/'}]}
    >>> version = 2
    >>> results, ssl_info, total_counter, success =  func(self, data, version, True)
    >>> results.keys()
    ['test_fails', 'test_home']
    >>> results['test_fails'].keys()
    ['errors', 'success', 'successes', 'result_counters', 'skipped', 'result', 'failures']
    >>> results['test_fails']['success']
    False
    >>> len(results['test_fails']['failures'])
    2
    >>> results['test_fails']['failures'][0]['env_name']
    'sahli'
    >>> results['test_fails']['failures'][1]['env_name']
    'httptest'
    >>> len(results['test_fails']['errors'])
    0
    >>> len(results['test_fails']['successes'])
    0
    >>> len(results['test_home']['successes'])
    2
    >>> results['test_home']['successes'][0]['env_name']
    'sahli'
    >>> total_counter['run']
    4
    >>> success
    True
    """
    import unittest
    import requests
    import json
    import re
    import string
    import random
    from multiprocessing.pool import ThreadPool
    import utils

    info = self.info
    error = self.error
    warn = self.warn
    rid = self.rid

    environments = data['environments']
    requests_data = data.get('requests', data['tests'])


    class HTTPTest(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super(HTTPTest, self).__init__()
            self.response = None
            self.kwargs = kwargs
            self.url = kwargs['url']
            self.env_name = kwargs['env_name']
            self.status_code = kwargs.get('status_code', "200")
            self.method = kwargs.get('method', "GET")
            self.data = kwargs.get('data', None)
            self.auth = None
            if kwargs.get('username', None):
                    self.auth = (kwargs['username'], kwargs['password'])
            self.pattern = kwargs.get('response_pattern', None)

            self.json = kwargs.get('response_json', None)

            self.type = kwargs.get('type', None)

        def _send_request(self):
            headers = self.kwargs.get("headers", {})

            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=2)
            prepared_req = None
            if not self.method:
                self.method = "GET"
            #if self.data and self.data.startswith("http"):
            #    prepared_req = requests.Request("GET", self.data, adapter)
            if self.data and self.data.startswith("<"):
                headers['Content-Type'] = 'application/xml'
                r = requests.Request(self.method, self.url, data=self.data, auth=self.auth, headers=headers)
            elif self.data:
                self.data = json.loads(self.data)
                r = requests.Request(self.method, self.url, json=self.data, auth=self.auth, headers=headers)
            else:
                r = requests.Request(self.method, self.url, auth=self.auth, headers=headers)
            if r:
                prepared_req = r.prepare()
                session.mount("https://", adapter)
                r = session.send(prepared_req, verify=self.verify, timeout=10, allow_redirects=False)

            # save data
            self.response = r
            self.headers = {}
            self.headers['request'] = self._format_headers(r.request.headers)
            self.headers['response'] = self._format_headers(r.headers)

        def _format_headers(self, headers):
            for key, value in headers.iteritems():
                if "authorization" in key.lower():
                    headers[key] = "**************"
            return dict(headers)

        def runTest(self):
            if self.kwargs.get('disabled', False):
                raise unittest.SkipTest("test by env disabled (%s)" % self.url)
            if not self.kwargs.get('enable', True):
                raise unittest.SkipTest("test by request disabled (%s)" % self.url)
            self.verify = self.kwargs.get('ssl_verify', True)
            try:

                self._send_request()
                assert int(self.status_code) == self.response.status_code, "%s is expected, but was %s" % (self.status_code, self.response.status_code)
                if self.type:
                    response_type = eval(self.type.replace("<", "").replace(">", ""))
                    #info(rid, str(response_type))
                    assert response_type == type(self.response.json()), "Wrong response type"
                if self.pattern:
                    assert self.pattern in self.response.text, self.pattern + " not found in response body" % self.pattern
            except AssertionError, e:
                #warn(rid, "%s: %s (%s)" % (self.url, str(e.message), self.response.text[:60]))
                self.error = e.message
                raise AssertionError("%s: %s" % (self.url, str(e.message)))
            except requests.ConnectionError, e:
                #error(rid, "%s: ConnectionError: %s " % (self.url, str(e.message)))
                self.error = e.message
                raise requests.ConnectionError("%s: %s" % (self.url, str(e.message)))
            except Exception, e:
                #error(rid, "%s: Exception: %s" % (self.url, str(e.message)))
                self.error = repr(e)
                raise Exception("%s: %s" % (self.url, repr(e)))

            #info(rid, "OK "+self.url)

    class HTTPTestV2(HTTPTest):
        def __init__(self, outer_self, id, test_name, test_assert, **kwargs):
            super(HTTPTest, self).__init__()
            self.outer_self = outer_self
            self.assert_key, self.assert_value = test_assert
            self.response = None
            self.kwargs = kwargs
            self.url = kwargs['url']
            self.env_name = kwargs['env_name']
            self.test_name = test_name
            self.method = kwargs.get('method', "GET")
            self.data = kwargs.get('data', None)
            self.auth = None
            self.id = id
            if kwargs.get('username', None):
                    self.auth = (kwargs['username'], kwargs['password'])

            self.ssl_info = None

        def runTest(self):
            """ 
            timeout
            skip
            ssl_verify
            headers

            - assert_status_code_is
            - assert_status_code_is_not
            - assert_header_is_set
            - assert_header_is_not_set
            - assert_header_value_contains
            - assert_body_contains
            - assert_is_json
            - assert_is_not_json
            """
            if self.kwargs.get('skip', None):
                raise unittest.SkipTest("test marked as skip (%s)" % self.url)
            self.verify = self.kwargs.get('ssl_verify', True)
            try:
                from urlparse import urlparse
                url_parsed = urlparse(self.url)
                if url_parsed.scheme == "https":
                    host_port = url_parsed.netloc.split(":")
                    host = host_port[0]
                    if url_parsed.port:
                        port = url_parsed.port
                    else:
                        port = 443
                    self.ssl_info = utils.get_ssl_info(self.outer_self, host, port)
                else:
                    self.ssl_info = None
            except Exception, e:
                self.outer_self.error(self.outer_self.rid, str(e))
                if "handshake failure" in str(e):
                    self.ssl_info = str(e)
                else:
                    self.ssl_info = "Unexpected SSL Error (%s)" % str(e)
            try:
                self.starttime = utils.get_datetime()
                self._send_request()
                self.endtime = utils.get_datetime()
                delta = self.endtime - self.starttime
                self.duration = int(delta.total_seconds() * 1000)

                self.response_text = self.response.text
                if self.assert_key == "assert_status_code_is":
                    assert int(self.assert_value) == self.response.status_code, "%s is expected, but was %s" % (self.assert_value, self.response.status_code)
                if self.assert_key == "assert_status_code_is_not":
                    assert int(self.assert_value) != self.response.status_code, "%s is not expected, but was %s" % (self.assert_value, self.response.status_code)
                if self.assert_key == "assert_body_contains":
                    assert self.assert_value in self.response.text, "assert_body_contains failed, string %s not found in response body" % (self.assert_value)

                if self.assert_key == "assert_is_json":
                    try:
                        try:
                            self.response.json()
                        except AttributeError, e:
                            # accept null as valid JSON
                            if self.response_text == "null":
                                pass
                            else:
                                raise e
                    except:
                        raise AssertionError("assert_is_json evaluated to false, should be true")

                if self.assert_key == "assert_is_not_json":
                    try:
                        self.response.json()
                        raise AssertionError("assert_is_json evaluated to true, should be false")
                    except:
                        pass

                if self.assert_key == "assert_header_is_set":
                    header = self.assert_value
                    assert header in self.response.headers.keys(), "assert_header_is_set failed, header '%s' is missing" % header

                if self.assert_key == "assert_header_is_not_set":
                    header = self.assert_value
                    assert header not in self.response.headers.keys(), "assert_header_is_not_set failed, header '%s' is set" % header

                if self.assert_key == "assert_header_value_contains":
                    headers = self.assert_value
                    try:
                        for k, v in headers.iteritems():
                            if self.response.headers.get(k, None):
                                assert v in self.response.headers.get(k), "assert_header_value_contains failed, header '%s' is: %s" % (k, self.response.headers.get(k))
                            else:
                                raise AssertionError("Header '%s' is not set" % k)
                    except AttributeError, e:
                        warn(rid, "Headers isis: "+str(headers))
                        warn(rid, "Headers type is: "+str(type(headers)))

            except AssertionError, e:
                #warn(rid, "%s: %s (%s)" % (self.url, str(e.message), self.response.text[:60]))
                self.error = e.message
                raise AssertionError("%s: %s" % (self.url, str(e.message)))
            except requests.ConnectionError, e:
                #error(rid, "%s: ConnectionError: %s " % (self.url, str(e.message)))
                self.error = e.message
                raise requests.ConnectionError("%s: %s" % (self.url, str(e.message)))
            except Exception, e:
                self.error = repr(e)
                import time
                import traceback
                traceback.print_exc()

                time.sleep(5)
                raise Exception("%s: %s" % (self.url, repr(e)))


    def suite(request, environments, version=1):
        suite = unittest.TestSuite()
        tests = []
        import copy
        for env in environments:
            # needs to deepcopy the arg because we enrich the dict with stuff from environment
            request_orig = copy.deepcopy(request)
            request_orig.update(env)
            request_orig['url'] = env['base_url']+request_orig['uri']
            variables = env.get('variables', {})
            for var_k, var_v in variables.iteritems():
                request_orig['url'] = request_orig['url'].replace("{{%s}}" % var_k, var_v)
            request_orig['env_name'] = env['name']
            if version == 1:
                tests.append(HTTPTest(**request_orig))
            elif version == 2:
                for test_assert in request_orig['asserts'].iteritems():
                    test_assert_new = list(copy.deepcopy(test_assert))
                    for var_k, var_v in variables.iteritems():
                        test_assert_new[1] = str(test_assert_new[1]).replace("{{%s}}" % var_k, var_v)
                        try:
                            test_assert_new[1] = int(test_assert_new[1])
                        except:
                            pass
                    N = 5
                    id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
                    tests.append(HTTPTestV2(self, id, request['name'], test_assert_new, **request_orig))
            else:
                raise Exception("Unknown version %s" % version)
        suite.addTests(tests)
        return suite

    result_list = {}
    env_pool = ThreadPool(processes=10)

    class MyTestRunner(unittest.TextTestRunner):

        def _makeResult(self):
            return MyTextTestResult(self.stream, self.descriptions, self.verbosity)

    class MyTextTestResult(unittest.TextTestResult):

        def __init__(self, stream=None, descriptions=None, verbosity=None):
            self.successes = []
            super(MyTextTestResult, self).__init__(stream, descriptions, verbosity)

        def addSkip(self, test, reason):

            super(MyTextTestResult, self).addSkip(test, reason)
            if hasattr(self, "ssl_info"):
                self.ssl_info['None'] = None
            else:
                self.ssl_info = {}
                self.ssl_info["None"] = None

        def addSuccess(self, test):
            super(MyTextTestResult, self).addSuccess(test)
            self.successes.append((test, "a"))
            if hasattr(self, "ssl_info"):
                self.ssl_info[test.env_name] = test.ssl_info
            else:
                self.ssl_info = {}
                self.ssl_info[test.env_name] = test.ssl_info
        def addFailure(self, test, err):
            super(MyTextTestResult, self).addFailure(test, err)
            if hasattr(self, "ssl_info"):
                self.ssl_info[test.env_name] = test.ssl_info
            else:
                self.ssl_info = {}
                self.ssl_info[test.env_name] = test.ssl_info
        def addError(self, test, err):
            super(MyTextTestResult, self).addError(test, err)
            if hasattr(self, "ssl_info"):
                self.ssl_info[test.env_name] = test.ssl_info
            else:
                self.ssl_info = {}
                self.ssl_info[test.env_name] = test.ssl_info


    def run_test(*args):
        request = args[0]
        environments= args[1]
        return MyTestRunner().run(suite(request, environments, int(version)))

    # main
    result_pool = {}
    for request in requests_data:
        result_pool[request['name']] = env_pool.apply_async(run_test, args=[request, environments, int(version)])
    env_pool.close()
    env_pool.join()

    # for env
    total_counters = {
            "run": 0,
            "errors": 0,
            "failures": 0,
            "success": 0,
            "skipped": 0 
        }
    ssl_info = {}
    for test_name, async_result in result_pool.items():

        result = async_result.get()
        success = result.wasSuccessful()
        #self.info(self.rid, str(result.__dict__))
        # .*run=([0-9]*) errors=([0-9]*) failures=([0-9]*)>
        # <unittest.runner.TextTestResult run=2 errors=1 failures=0>
        m = re.match(r".*run=([0-9]*) errors=([0-9]*) failures=([0-9]*)>", str(result))
        run_count = int(m.group(1))
        errors_count = int(m.group(2))
        failures_count = int(m.group(3))
        skipped_count = len(result.skipped)
        success_count = run_count - errors_count - failures_count - skipped_count

        result_counters = {
            "run": run_count,
            "errors": errors_count,
            "failures": failures_count,
            "success": success_count,
            "skipped": skipped_count
        }

        total_counters["run"] += run_count
        total_counters["errors"] += errors_count
        total_counters["failures"] += failures_count
        total_counters["success"] += success_count
        total_counters["skipped"] += skipped_count

        failures_list = []
        errors_list = []
        for a in result.failures:
            failures_list.append({
                'env_name': a[0].env_name,
                'test_name': a[0].test_name,
                'assert_key': a[0].assert_key,
                'duration': getattr(a[0], "duration", None),
                'response_text': getattr(a[0], "response_text", None),
                'url': a[0].url,
                'id': a[0].id,
                'message': str(a[0].error),
                'headers': a[0].__dict__.get("headers", {})
            })
        for a in result.errors:
            errors_list.append({
                'env_name': a[0].env_name, 
                'test_name': a[0].test_name,
                'assert_key': a[0].assert_key,
                'duration': getattr(a[0], "duration", None),
                'response_text': getattr(a[0], "response_text", None), 
                'url': a[0].url, 
                'id': a[0].id, 
                'message': str(a[0].error), 
                'headers': a[0].__dict__.get("headers", {})
            })
        for r in result.failures + result.errors + result.skipped:
            self.info(self.rid, "Result DEBUG: " + str(r[0].test_name) +" " +str(r[0].env_name) +" "+r[0]._testMethodName+" "+ r[0].url)

        success_list = []
        for r in result.successes:
            #raise Exception(r[0].assert_key)
            self.info(self.rid, "Result DEBUG: " + str(r[0].test_name) +" " +str(r[0].env_name) +" "+r[0]._testMethodName+" "+ r[0].url)
            success_list.append({
                'env_name': r[0].env_name,
                'test_name': r[0].test_name,
                'assert_key': r[0].assert_key,
                'duration': getattr(a[0], "duration", None),
                'response_text': getattr(r[0], "response_text", None),
                'url': r[0].url,
                'id': r[0].id,
                'message': None,
                'headers': r[0].__dict__.get("headers", {})
            })


        for env, info in result.ssl_info.items():
            ssl_info[env] = info

        result_list[test_name] = {
                "success": success,
                "result_counters": result_counters,
                "result": str(result),
                "failures": failures_list,
                "successes": success_list,
                "errors": errors_list,
                "skipped": [a[0].url for a in result.skipped],
        }
    if not response_obj:
        return self.responses.JSONResponse((len(result_pool), result_list))
    else:
        return result_list, ssl_info, total_counters, success

if __name__ == "__main__":
        import doctest
        if os.environ.get("CI", None):
            doctest.testmod(raise_on_error=True)
        else:
            doctest.testmod()
