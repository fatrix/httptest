def func(self):
	import sys, os
	import py_compile
	if  os.environ['EXECUTOR'] != "docker":
		sys.path.append("/home/philipsahli/workspace/httptest/app")
		py_compile.compile("/home/philipsahli/workspace/httptest/app/cleanup_tests.py", doraise=True)
		import cleanup_tests
		import utils
		reload(cleanup_tests)
		reload(utils)
	else:
		from app import cleanup_tests
	return cleanup_tests.func(self)