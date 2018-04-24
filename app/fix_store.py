def func(self):
	#return str(dir(self.datastore))
	self.datastore.session.rollback()
	self.datastore._execute("SELECT setval('data_table_id_seq', (SELECT MAX(id) FROM data_table)+1)")
	self.datastore.session.commit()
	return "Fixed"