def func(self):
    import json
    import random, string
    import requests
    import sys

    from datetime import datetime

    import httptest
    import utils

    from core.plugins.datastore import LockException

    id = self.GET.get("testid", None)

    DEFAULT_VERSION = 2

    version = self.GET.get("version", None)
    # default version
    if not version or "None" in version:
        version = DEFAULT_VERSION

    if id:
        try:
            data = self.datastore.get("testid", id, lock=True, nowait=True)
        except LockException, e:
            self.error(self.rid, str(e))
            raise Exception("Test already running")
        if not data:
            raise Exception("Not found")
    # sendmail
    if self.method == "GET" and self.GET.has_key("sendmail"):
        try:
            email = self.GET.get('email')
            test_list = self.datastore.filter("email", email)
            msg = ""
            if len(test_list) > 0:
                for test in test_list:
                    testurl = utils.get_test_url(self, test.data['testid'], version, fq=True)
                    msg+="%s: %s\n" % (test.data.get('name', "No name"), testurl)
            else:
                msg = "No test found"

            subject = "HTTPTest - Links for %s" % email

            utils.sendmail(self, email, subject, msg)

            return self.responses.JSONResponse(json.dumps({"message": "sent"}))
        except Exception, e:
            self.error(self.rid, e.message)
            return self.responses.JSONResponse(json.dumps({"message": "error", "details": e.message}))

    # redirect to static url
    elif self.method == "GET":
        # create new test
        id=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
        json_data = {}
        json_data.update({"testid": id})
        json_data.update({"version": version})
        json_data.update({"runs": []})
        json_data.update({"user_id": self.identity['internalid']})
        self.datastore.write_dict(json_data)

        return self.responses.RedirectResponse(utils.get_test_url(self, id, version))

    # reset
    elif self.method == "POST" and self.GET.get('action') == "reset":
        data.data['runs'] = []
        self.datastore.update(data)
        self.datastore.session.commit()
        return self.responses.JSONResponse({'message': "reset"})
    # delete
    elif self.method == "POST" and self.GET.get('action') == "delete":
        self.datastore.delete(data)
        self.datastore.session.commit()
        return self.responses.JSONResponse({'message': "delete"})
    # run
    elif self.method == "POST":
        user_id = self.identity['internalid']
        if not self.GET.has_key("from_store"):
            name = self.POST.get("name", None)
            config_data = self.POST.get("config_data", None)
            save_data = self.POST.get("save_data", "no")
            schedule = self.POST.get("schedule", "no")
            config_url = self.POST.get("config_url", None)
            email = self.POST.get("email", None)
        else:
            name = data.data['name']
            config_data = data.data['config_data']
            save_data = data.data['save_data']
            schedule = data.data['schedule']
            config_url = data.data["config_url"]
            email = data.data["email"]

        if config_url:
            r = requests.get(config_url, allow_redirects=True)
            body = r.text
        else:
            body = config_data

        data.data['config_url'] = config_url
        data.data['name'] = name
        data.data['email'] = email
        data.data['user_id'] = user_id
        if "yes" in save_data:
            data.data['config_data'] = config_data
            data.data['save_data'] = save_data
        else:
            data.data['config_data'] = ""
            data.data['save_data'] = "no"
        if "yes" in schedule:
            data.data['schedule'] = schedule
        else:
            data.data['schedule'] = "no"

        ALPHA = string.ascii_letters
        if body.startswith('"') and body.endswith('"'):
            body= body[1:-1]
        if body.startswith("{"):
            # JSON
            config = json.loads(body)
        elif body.startswith(tuple(ALPHA)):
            # YAML
            import yaml
            config = yaml.load(body)
        else:
            raise Exception("Missing data, body was: "+body )

        # save config_data as dict
        if "yes" in save_data:
            data.data['config_data_dict'] = config

        results, ssl_info, total_counter =  httptest.func(self, config, version, True)
        mydatetime = datetime.now()
        runs = {
              'result': results,
              'ssl_info': ssl_info,
              'total': total_counter,
              'datetime': str(mydatetime)
        }
        if data.data.has_key("runs"):
            data.data['runs'].append(runs)
            if len(data.data['runs']) > 20:
                to_cleanup = len(data.data['runs'])-20
                for num in range(0, to_cleanup):
                    data.data['runs'].pop(0)
        else:
            data.data['runs'] = [runs]
        self.datastore.update(data)
        self.datastore.session.commit()
        # send report
        #utils.send_report(self, id, email, data.data['name'], run=mydatetime)
        return self.responses.JSONResponse(json.dumps({"message": (results, total_counter, str(mydatetime), ssl_info), 'runs_count': len(data.data['runs'])}))
