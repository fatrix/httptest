def func(self):
    import requests
    import json
    import utils

    import time
    from core.plugins.datastore import LockException
    time.sleep(0.2)

    tests = self.datastore.all(lock=False, nowait=True)

    self.info(self.rid, "Starting for %s tests" % len(tests))

    def handle(test):
        # name
        delete = False
        try:
            #self.info(self.rid, test.data['runs'])
            if "name" not in test.data and len(test.data['runs']) == 0 :
                delete = True
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
            if delete:
                self.info(self.rid, "To deleted: %s %s" % (test, test.data['testid']))
                self.datastore.delete(test)
                self.info(self.rid, "Deleted: %s %s" % (test, test.data['testid']))

    for test in tests:
        try:
            test_locked = self.datastore.get("testid", test.data['testid'], lock=True, nowait=True)
            handle(test_locked)
        except Exception, e:
            self.error(self.rid, e.message)
            self.datastore.session.rollback()
        finally:
            self.datastore.session.commit()

    self.info(self.rid, "Ended for %s tests" % len(tests))

    return "Done"
