def func(self):
	import sys, os
	import py_compile
	if  os.environ['EXECUTOR'] != "docker":
		sys.path.append("/home/philipsahli/workspace/httptest/app")
		py_compile.compile("/home/philipsahli/workspace/httptest/app/schedule.py", doraise=True)
		import schedule
		import utils
		reload(schedule)
		reload(utils)
	else:
		from app import schedule
	return schedule.func(self)