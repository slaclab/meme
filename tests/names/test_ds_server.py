import pvaccess

srv = pvaccess.RpcServer()
def handle_request(request):
	response = pvaccess.PvObject({"labels": [pvaccess.STRING], "value": {"name": [pvaccess.STRING]}}, {"labels": ["name"], "value": {"name": ['This', 'is', 'a', 'test']}},'epics:nt/NTTable:1.0')
	return response
	
print("Starting Test Server!")
srv.registerService('ds', handle_request)
srv.listen()