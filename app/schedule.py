def func(self):
    import requests
    import json
    import utils
    tests = self.datastore.filter("schedule", "yes")
    results = []
    for test in tests:
        failure_count_before = test.data['runs'][-1]['total']['failures'] + test.data['runs'][-1]['total']['errors']

        r = requests.post("https://codeanywhere.sahli.net/fastapp/api/username/admin/base/httptest/apy/entrypoint/execute/?json=&from_store&testid=%s" % test.data['testid'])
        result = json.loads(r.json()['returned']['content'])
        results.append(result)
        result_counters = result['message'][1]

        failure_count_after = result_counters['failures'] + result_counters['errors']

        send_alarm=False
        send_recover=False

        print "Diff %s to %s" % (failure_count_before, failure_count_after)
        if failure_count_before < failure_count_after:
            send_alarm=True
            subject = "HTTPTest - Test '%s' failed on %s" % (test.data['name'], test.data['datetime'])
            msg = "Test %s failed" % (test.data['name'])
        elif failure_count_after == 0 and failure_count_before is not failure_count_after:
            send_recover=True
            subject = "HTTPTest - Test '%s' recovered on %s" % (test.data['name'], test.data['datetime'])
            msg = "Test %s recovered" % (test.data['name'])

        if send_alarm or send_recover:
           utils.sendmail(self, test.data['email'], subject, msg)

    return results
