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
        self.info(self.rid, "To deleted: %s %s" % (test, test.data['testid']))
        self.datastore.delete(test)
        self.info(self.rid, "Deleted: %s %s" % (test, test.data['testid']))

    for test in tests:
        if "name" not in test.data and len(test.data['runs']) == 0 :
            try:
                test_locked = self.datastore.get("testid", test.data['testid'], lock=True, nowait=True)
                handle(test_locked)
            except Exception, e:
                self.error(self.rid, e.message)
                self.datastore.session.rollback()
            finally:
                self.info(self.rid, "Test deleted")
                self.datastore.session.commit()
        else:
            self.info(self.rid, "let it be")

    self.info(self.rid, "Ended for %s tests" % len(tests))

    return "Done"
