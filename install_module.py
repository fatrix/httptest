def func(self, r=""):
	import os, sys
	module = "-e " + self.settings.GIT_URL
	pip = os.path.join(os.path.dirname(sys.executable), "pip")
	r=os.popen("%s install %s" % (pip, module)).read()
	return r