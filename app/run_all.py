def func(self):
    import requests
    import json
    import utils

    import time
    from core.plugins.datastore import LockException
    time.sleep(0.2)

    tests = self.datastore.all(lock=False, nowait=False)

    results = []

    self.info(self.rid, "Starting for %s tests" % len(tests))

    def handle(test):
        try:
            self.info(self.rid, "start %s" % test.data.get("name", "No Name"))
            try:
                failure_count_before = test.data['runs'][-1]['total']['failures'] + test.data['runs'][-1]['total']['errors']
            except Exception, e:
                failure_count_before = 0

            url = "%s?json=&from_store&testid=%s" % (self.settings.SCHEDULE_URL, test.data['testid'])
            self.debug(self.rid, url)
            #r = requests.post("%s?json=&from_store&testid=%s" % (self.settings.SCHEDULE_URL, test.data['testid']))
            #self.info(self.rid, "status_code on call for run is: %s" % r.status_code)
            #self.info(self.rid, r.text)
            #if r.status_code is not 200:
            #    self.error(self.rid, "Could not invoke test (%s)" % r.status_code)
            #    raise Exception("Could not invoke test (%s)" % r.status_code)
            self.GET['testid'] = test.data['testid']
            self.GET['json'] = True
            self.GET['from_store'] = True
            self.method = "POST"
            #from utils import debug
            #debug()
            r = self.siblings.entrypoint(self)
            result = json.loads(r.json()['returned']['content'])
            results.append(result)
            result_counters = result['message'][1]
            mydatetime = result['message'][2]

            ssl_info = result['message'][3]

            failure_count_after = result_counters['failures'] + result_counters['errors']

            send_alarm=False
            send_recover=False

            self.debug(self.rid, "Diff %s to %s" % (failure_count_before, failure_count_after))

            # TEST
            if failure_count_before < failure_count_after:
                send_alarm=True
                subject = "HTTPTest - Test '%s' failed" % test.data['name']
                msg = "Test %s failed" % (test.data['name'])
            elif failure_count_after == 0 and failure_count_before is not failure_count_after:
                send_recover=True
                subject = "HTTPTest - Test '%s' recovered" % test.data['name']
                msg = "Test %s recovered" % (test.data['name'])

            self.info(self.rid, "%s %s" % (str(send_alarm), str(send_recover)))
            if send_alarm or send_recover:
                self.info(self.rid, "Send Mail to %s" % test.data['email'])
                utils.send_report(self, test.data['testid'], test.data['email'], test.data['name'], run=mydatetime, subject=subject)

            # SSL
            for env, info in ssl_info.items():
                #from remote_pdb import RemotePdb
                #RemotePdb('127.0.0.1', 4444).set_trace()
                if not type(info) is dict:
                    self.warn(self.rid, "Not a dict (%s)" % str(info))
                    continue
                if not test.data.get('ssl_alarmed', None):
                    test.data['ssl_alarmed'] = {}
                for left in [2,  5,  10, 30]:
                    leftAlarmed = test.data['ssl_alarmed'].get(str(left), False)
                    if info['daysLeft'] == left and not leftAlarmed:
                        test.data['ssl_alarmed'][left] = True

                        subject = "HTTPTest - Test '%s': The SSL certificate on environment '%s' will expire in %s days!" % (test.data['name'], env, info['daysLeft'])
                        utils.send_report(self, test.data['testid'], test.data['email'], test.data['name'], run=mydatetime, subject=subject)

        except Exception, e:
            import inspect
            lineno = inspect.currentframe().f_back.f_lineno
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            s = str((exc_type, fname, exc_tb.tb_lineno))
            self.error(self.rid, str(e)+" (%s)" % s)
            self.datastore.session.rollback()

        finally:
            self.info(self.rid, "Finally: %s" % test)
            try:
                self.info(self.rid, "Lasts: %s" % test.data['last'].datetime)
            except:
                pass
            self.datastore.update(test)
            self.datastore.session.commit()


    for test in tests:
        handle(test)

    self.info(self.rid, "Ended for %s tests" % len(tests))

    return results
