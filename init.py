def func(self):
	if "yes" in self.settings.INIT:
		r1=self.siblings.install_dependencies(self)
		r2=self.siblings.install_module(self)
	return r1, r2