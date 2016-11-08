def func(self):
    import requests
    import json
    import utils
    import copy
    import time

    tests = self.datastore.filter("schedule", "yes")

    results = []
    alarms = []

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
            self.GET['testid'] = test.data['testid']
            self.GET['json'] = True
            self.GET['from_store'] = True
            self.method = "POST"
            r = self.siblings.entrypoint(self)
            result = json.loads(r.content)
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
                send_alarm = True
                subject = "HTTPTest - Test '%s' failed" % test.data['name']
                msg = "Test %s failed" % (test.data['name'])
            elif failure_count_after == 0 and failure_count_before is not failure_count_after:
                send_recover = True
                subject = "HTTPTest - Test '%s' recovered" % test.data['name']
                msg = "Test %s recovered" % (test.data['name'])

            self.info(self.rid, "Alarm: %s %s" % (str(send_alarm), str(send_recover)))
            if send_alarm or send_recover:
                self.info(self.rid, "Send Mail to %s" % test.data['email'])
                try:
                    utils.send_report(self, test.data['testid'], test.data['email'], test.data['name'], run=mydatetime, subject=subject)
                except Exception, e:
                    self.error(self.rid, "Exception from utils.send_report")

            # SSL
            try:
                ssl_alarm = copy.deepcopy(test.data['ssl_alarm'])
            except:
                self.info(self.rid, "Create empty dict test.data['ssl_alarm']")
                ssl_alarm = {}

            for env, info in ssl_info.items():
                if not type(info) is dict:
                    self.warn(self.rid, "Not a dict (%s)" % str(info))
                    continue
                self.info(self.rid, env+" ssl_info: "+str(info))
                self.info(self.rid, "Checking for resulted serialNumber "+info['serialNumber'])
                self.info(self.rid, "ssl_alarm from store at begin: %s" % str(test.data['ssl_alarm']))

                if not ssl_alarm.get(env, None):
                    ssl_alarm[env] = {}

                if not ssl_alarm[env].get('%s' % info['serialNumber'], None):
                    self.info(self.rid, "Cleanup test.data['ssl_alarm'] and create empty dict for serialNumber")
                    ssl_alarm[env].clear()
                    ssl_alarm[env]['%s' % info['serialNumber']] = {}
                self.info(self.rid, "ssl_alarm3: %s" % str(ssl_alarm[env]))

                for left in [2,  5,  10, 30]:
                    is_alarmed = ssl_alarm[env]['%s' % info['serialNumber']].get(str(left), False)
                    self.info(self.rid, "Left: %s: %s" % (left, is_alarmed))
                    if info['daysLeft'] == left and not is_alarmed:
                        self.info(self.rid, "must alert for ssl expiration, %s | %s | %s | %s " % (left, is_alarmed, ssl_alarm[env], info['commonName']))
                        ssl_alarm[env]['%s' % info['serialNumber']][str(left)] = True
                        self.info(self.rid, "must alert for ssl expiration, %s | %s | %s | %s | is_alarmed: %s" % (left, is_alarmed, ssl_alarm[env], info['commonName'], ssl_alarm[env]['%s' % info['serialNumber']][str(left)]))
                        self.info(self.rid, "ssl_alarm after: %s" % ssl_alarm[env])

                        subject = "HTTPTest - Test '%s': The SSL certificate on environment '%s' will expire in %s days!" % (test.data['name'], env, info['daysLeft'])
                        utils.send_report(self, test.data['testid'], test.data['email'], test.data['name'], run=mydatetime, subject=subject)

                        #self.datastore.update(test)
                        #self.datastore.session.commit()

        except Exception, e:
            import sys, os
            import inspect
            lineno = inspect.currentframe().f_back.f_lineno
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            s = str((exc_type, fname, exc_tb.tb_lineno))

            self.error(self.rid, str(e)+" (%s)" % s)
            self.datastore.session.rollback()

        finally:
            self.info(self.rid, "Finally: %s" % test.data['testid'])
            test.data['ssl_alarm'] = ssl_alarm
            self.info(self.rid, "ssl_alarm after2: %s" % test.data['ssl_alarm'])

            alarms.append(ssl_alarm)
            try:
                #self.info(self.rid, "Lasts: %s" % test.data['last'].datetime)
                self.info(self.rid, "Alarm: %s" % str(test.data['ssl_alarm']))
            except Exception, e:
                print e
                self.error(self.rid, e.message)
            self.datastore.update(test)
            self.datastore.session.commit()


    for test in tests:
        handle(test)

    self.info(self.rid, "Ended for %s tests" % len(tests))

    return results, alarms
