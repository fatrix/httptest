def func(self):
	for row in self.datastore.all():
		self.datastore.delete(row)