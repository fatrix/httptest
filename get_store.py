def func(self):
        self.info(self.rid, "get store")
        l=[row.data for row in self.datastore.all()]
        #self.info(self.rid, str(l))
        return l, len(self.datastore.all())