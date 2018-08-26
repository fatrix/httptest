def func(self):
	r1=self.siblings.install_dependencies(self)
	r2=self.siblings.install_module(self)
	import os, signal
	os.kill(1, signal.SIGHUP)
	return r1, r2