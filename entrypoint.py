def func(self):
	import sys, os
	import py_compile
	if  os.environ['EXECUTOR'] != "docker":
		sys.path.append("/home/philipsahli/workspace/httptest/app")
		py_compile.compile("/home/philipsahli/workspace/httptest/app/httptest.py", doraise=True)
		import entrypoint, httptest
		reload(entrypoint)
		reload(httptest)
	else:
		from app import entrypoint
		from app import httptest
		print httptest
	return entrypoint.func(self)