def func(self):
    from core.responses import JSONResponse
    import json
    return JSONResponse(json.dumps(self.identity))