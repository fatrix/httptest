def func(self):
	import json
	r={'request': {'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'User-Agent': 'python-requests/2.9.1'}, 'response': {'Content-Encoding': 'gzip', 'Set-Cookie': 'session_id=5d4e427a139bed2d9783aed06ab872d73d5a0777; Expires=Tue, 19-Jul-2016 07:18:33 GMT; Max-Age=7776000; Path=/', 'Server': 'Cherokee', 'Connection': 'close', 'Date': 'Wed, 20 Apr 2016 07:18:33 GMT', 'Content-Type': 'text/html; charset=utf-8'}}
	self.datastore.write_dict(r)
	self.info(self.rid, "stored")
	return self.responses.JSONResponse(json.dumps(r))