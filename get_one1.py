def func(self):
    import json
    return self.responses.JSONResponse(json.dumps(self.datastore.get("name", "My Test", lock=False, nowait=True).data['runs'][0].keys()))