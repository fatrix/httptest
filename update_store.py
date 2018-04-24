def func(self):
	import json
	data = self.POST['body']
	self.info(self.rid, data)
	json_data = json.loads(data)
	return self.responses.JSONResponse(json_data)