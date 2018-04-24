def func(self):
	import sys, os
	import py_compile
	if  os.environ['EXECUTOR'] != "docker":
		sys.path.append("/home/philipsahli/workspace/httptest/app")
		py_compile.compile("/home/philipsahli/workspace/httptest/app/run_all.py", doraise=True)
		import run_all
		import utils
		reload(run_all)
		reload(utils)
	else:
		from app import run_all
	return run_all.func(self)