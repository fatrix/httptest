def func(self):
    import requests
    import json
    import utils
    tests = self.datastore.filter("schedule", "yes")
    results = []
    for test in tests:
        failure_count_before = test.data['runs'][-1]['total']['failures'] + test.data['runs'][-1]['total']['errors']

        r = requests.post("%s?json=&from_store&testid=%s" % (self.settings.SCHEDULE_URL, test.data['testid']))
        self.info(self.rid, r.status_code)
        self.info(self.rid, r.text)
        result = json.loads(r.json()['returned']['content'])
        results.append(result)
        result_counters = result['message'][1]
        #datetime = result['message'][2]
        #datetime = None

        failure_count_after = result_counters['failures'] + result_counters['errors']

        send_alarm=False
        send_recover=False

        self.info(self.rid, "Diff %s to %s" % (failure_count_before, failure_count_after))
        if failure_count_before < failure_count_after:
            send_alarm=True
            #subject = "HTTPTest - Test '%s' failed on %s" % (test.data['name'], datetime)
            subject = "HTTPTest - Test '%s' failed (%s)" % (test.data['name'], result_counters)
            msg = "Test %s failed" % (test.data['name'])
        elif failure_count_after == 0 and failure_count_before is not failure_count_after:
            send_recover=True
            #subject = "HTTPTest - Test '%s' recovered on %s" % (test.data['name'], datetime)
            subject = "HTTPTest - Test '%s' recovered (%s)" % (test.data['name'], result_counters)
            msg = "Test %s recovered" % (test.data['name'])

        self.info(self.rid, "%s %s" % (str(send_alarm), str(send_recover)))
        if send_alarm or send_recover:
            self.info(self.rid, "Send Mail to %s" % test.data['email'])
            utils.sendmail(self, test.data['email'], subject, msg)

    return results
