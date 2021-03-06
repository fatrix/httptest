def func(self):
    import json
    import random, string
    import requests

    import httptest
    import utils

    from utils import TableStructure

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
            self.info(self.rid, "Row for %s locked with lock=True")
        except LockException, e:
            self.error(self.rid, "Row for %s was locked with lock=True")
            self.error(self.rid, str(e))
            raise Exception("Test already running")
        if not data:
            raise Exception("Not found")

    # redirect to static url
    if self.method == "GET" and self.GET.get("JSON"):
        return self.responses.JSONResponse(json.dumps(data))
    elif self.method == "GET" and not id:
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
        data.data['table'] = ""
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
        if not self.GET.has_key("from_store"):
            name = self.POST.get("name", None)
            config_data = self.POST.get("config_data", None)
            save_data = self.POST.get("save_data", "no")
            schedule = self.POST.get("schedule", "no")
            config_url = self.POST.get("config_url", None)
            email_list = [ addr.strip() for addr in self.POST["email"].split(',') ]
        else:
            name = data.data['name']
            config_data = data.data['config_data']
            save_data = data.data['save_data']
            schedule = data.data['schedule']
            config_url = data.data["config_url"]

            # convert comma-separated list to list
            email_list = [ addr.strip() for addr in data.data["email"]]

        if config_url:
            r = requests.get(config_url, allow_redirects=True)
            body = r.text
        else:
            body = config_data

        data.data['config_url'] = config_url
        data.data['name'] = name
        data.data['email'] = email_list
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

        results, ssl_info, total_counter, success =  httptest.func(self, config, version, True)
        mydatetime = utils.get_datetime()
        runs = {
              'result': results,
              'ssl_info': ssl_info,
              'total': total_counter,
              'datetime': str(mydatetime)
        }
        data.data['last'] = {
                'success': success,
                'datetime': str(mydatetime)
                }
        if data.data.has_key("runs"):
            data.data['runs'].append(runs)
            if len(data.data['runs']) > 30:
                to_cleanup = len(data.data['runs'])-20
                for num in range(0, to_cleanup):
                    data.data['runs'].pop(0)
        else:
            data.data['runs'] = [runs]

        try:
            # create table structure
            table = TableStructure()

            ngtable = TableStructure()
            #for test_name, v in runs['result'].items():
            #    raise Exception(v)
            #    ngtable.add_row(test_name)
            #    ngtable.add_row(test_name+"@"+v)
            #placeholder='<span class="glyphicon glyphicon-ban-circle" aria-hidden="true"></span>'
            placeholder=None
            for run in data.data['runs']:
                #from utils import debug; debug()
                datetime = run['datetime']
                for test_name, result in run['result'].items():
                    from utils import debug
                    #debug()
                    for r in result['failures']:
                        ngtable.add_column(r['env_name'])
                    for r in result.get('successes', []):
                        ngtable.add_column(r['env_name'])
                    for r in result['errors']:
                        ngtable.add_column(r['env_name'])

                for test_name, result in run['result'].items():
                    cells = []
                    row_name = "%s" % (test_name)
                    # <span class="inlinesparkline">1,4,4,7,5,9,10</span>
                    for result_type in ['errors', 'failures', 'successes']:
                        for idx, r in enumerate(result[result_type], start=1):
                            row_name = "%s@%s[%s]" % (test_name, r.get('assert_key', "None"), str(r.get('assert_value', ""))[:12])
                            if ngtable.cell_contains(row_name, r['env_name'], '<span'):
                                if "success" in result_type:
                                    cell = ngtable.add_cell(row_name, r['env_name'], ',+1')
                                else:
                                    cell = ngtable.add_cell(row_name, r['env_name'], ',-1')
                            else:
                                if "success" in result_type:
                                    cell = ngtable.add_cell(row_name, r['env_name'], '<span class="inlinesparkline">+1')
                                else:
                                    cell = ngtable.add_cell(row_name, r['env_name'], '<span class="inlinesparkline">-1')
                            cells.append(cell)
                    #for cell in cells:
                    #    if isinstance(cell, str):
                    #        cell += "</span>"
                    #    else:
                    #        cell.append("</span>")
                    #    print cell

                    #for r in result['errors']:
                    #    row_name = "%s@%s[%s]" % (test_name, r.get('assert_key', "None"), str(r.get('assert_value', ""))[:12])
                    #    ngtable.add_cell(row_name, r['env_name'], '<span class="glyphicon glyphicon-fire" title="%s (%sms)" aria-hidden="true"></span>' % (run['datetime'], r.get('duration', "?")), placeholder=placeholder)
                    #for r in result.get('successes', []):
                    #    row_name = "%s@%s[%s]" % (test_name, r.get('assert_key', "None"), str(r.get('assert_value', ""))[:12])
                    #    ngtable.add_cell(row_name, r['env_name'], '<span class="glyphicon glyphicon-ok text-success" title="%s (%sms)" aria-hidden="true"></span>' % (run['datetime'], r.get('duration', "?")), placeholder=placeholder)
            data.data['table'] = ngtable.html()
        except Exception, e:
            print utils.full_stack()
            raise e

        self.datastore.update(data)
        self.datastore.session.commit()

        # send report
        #utils.send_report(self, id, email_list, data.data['name'], run=mydatetime)
        return self.responses.JSONResponse(json.dumps({"message": (results, total_counter, str(mydatetime), ssl_info), 'runs_count': len(data.data['runs'])}))
