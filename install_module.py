def func(self, r=""):
	import os, sys,signal
	module = "-e " + self.settings.GIT_URL
	pip = os.path.join(os.path.dirname(sys.executable), "pip")
	r=os.popen("%s install %s" % (pip, module)).read()
	os.kill(1, signal.SIGHUP)
	return r