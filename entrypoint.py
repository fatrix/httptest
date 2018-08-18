def func(self):
	import sys 
	sys.path.append("/home/tumbo/.virtualenvs/tumbo/src/httptest")
	from app import entrypoint
	return entrypoint.func(self)