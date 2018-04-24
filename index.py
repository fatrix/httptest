def func(self):
	import sys, os
	import py_compile
	if  os.environ['EXECUTOR'] != "docker":
		sys.path.append("/home/philipsahli/workspace/httptest/app")
		py_compile.compile("/home/philipsahli/workspace/httptest/app/httptest.py", doraise=True)
		import httptest
		reload(httptest)
	else:
		from app import httptest
	#self.datastore.write_dict({'msg': "sync starting"})
	return httptest.func(self)