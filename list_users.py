def func(self):
		self.info(self.rid, "get store")
		users = []
		for row in self.datastore.all():
			email = row.data.get('email', None)
			if not email:
				continue
			if not row.data['email'] in users:
				users.append(email)
        
		return users