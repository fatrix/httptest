def func(self):
	import json
	print json
	
	id = self.GET.get("id", None)
	
	if id:
		data = self.datastore.filter("id", id)
		if len(data) <1:
			raise Exception("Not found")
	else:
		import random, string
		new_id=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
		self.datastore.write_dict({'id': new_id, 'testcases': []})
		return self.responses.RedirectResponse("/fastapp/api/base/httptest/apy/old_index/execute/?id=%s" % new_id)