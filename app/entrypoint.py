def func(self):
    import json
    import random, string
    import requests
    import sys

    from datetime import datetime

    import httptest

    id = self.GET.get("testid", None)

    DEFAULT_VERSION = 1

    version = self.GET.get("version", None)
    # default version
    if not version or "None" in version:
        version = DEFAULT_VERSION


    if id:
        data = self.datastore.get("testid", id)
        if not data:
            raise Exception("Not found")
    else:
        # create new test
        new_id=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
        json_data = {}
        json_data.update({"testid": new_id})
        json_data.update({"version": version})
        json_data.update({"runs": []})
        self.datastore.write_dict(json_data)
        return self.responses.RedirectResponse("/fastapp/api/username/%s/base/httptest/apy/entrypoint/execute/?testid=%s&version=%s" % (self.settings.RUNTIME_USER, new_id, version))


    if self.method == "GET" and self.GET.has_key("sendmail"):
        try:
            email = data.data['email']
            test_list = self.datastore.filter("email", data.data['email'])
            msg = ""
            for test in test_list:
                testurl = "%s/fastapp/httptest/static/index.html?testid=%s&version=%s" % (self.settings.BASE_URL, test.data['testid'], test.data.get('version', DEFAULT_VERSION))
                msg+="%s: %s\n" % (test.data.get('name', "No name"), testurl)

            from boto.ses import connect_to_region

            conn = connect_to_region('us-east-1', aws_access_key_id=self.settings.AWS_KEY, aws_secret_access_key=self.settings.AWS_SECRET)
            conn.send_email(
                    self.settings.EMAIL_SENDER, 
                    "Subject", 
                    msg, 
                    [email]
                )
            return self.responses.JSONResponse(json.dumps({"message": "sent"}))
        except Exception, e:
            self.error(self.rid, e.message)
            return self.responses.JSONResponse(json.dumps({"message": "error", "details": e.message}))
        
    elif self.method == "GET":
        return self.responses.RedirectResponse("/fastapp/httptest/static/index.html?testid=%s&version=%s" % (id, version))

    elif self.method == "POST" and self.GET.get('action') == "reset":
        data.data['runs'] = []
        self.datastore.update(data)
        return self.responses.JSONResponse({'message': "reset"})
    elif self.method == "POST" and self.GET.get('action') == "delete":
        self.datastore.delete(data)
        return self.responses.JSONResponse({'message': "delete"})
    elif self.method == "POST":
        # update name
        name = self.POST.get("name", None)
        email = self.POST.get("email", None)
        config_url = self.POST.get("config_url", None)
        config_data = self.POST.get("config_data", None)
        save_data = self.POST.get("save_data", "no")
        if config_url:
            r = requests.get(config_url, allow_redirects=True)
            body = r.text
        else:
            body = config_data
        data.data['config_url'] = config_url
        data.data['name'] = name
        data.data['email'] = email
        if "yes" in save_data:
            data.data['config_data'] = config_data
            data.data['save_data'] = save_data
        else:
            data.data['config_data'] = ""
        ALPHA = string.ascii_letters
        if body.startswith('"') and body.endswith('"'):
            body= body[1:-1]
        if body.startswith("{"):
            # JSON
            config = json.loads(body)
        elif body.startswith(tuple(ALPHA)):
            import yaml
            config = yaml.load(body)
        else:
            raise Exception("Missing data, body was: "+body )

        results, total_counter =  httptest.func(self, config, True)
        runs = {
              'result': results,
              'total': total_counter,
              'datetime': str(datetime.now())
        }
        if data.data.has_key("runs"):
            data.data['runs'].append(runs)
            if len(data.data['runs']) > 5:
                to_cleanup = len(data.data['runs'])-5
                for num in range(0, to_cleanup):
                    data.data['runs'].pop(0)
        else:
            data.data['runs'] = [runs]
        self.datastore.update(data)
        return self.responses.JSONResponse(json.dumps({"message": "runs", 'runs_count': len(data.data['runs'])}))
