import pvaccess

srv = pvaccess.RpcServer()
def handle_request(request):
	single_pv_struct = {"labels": [pvaccess.STRING], "value": {"secondsPastEpoch": [pvaccess.LONG], "values": [pvaccess.DOUBLE], "nanoseconds": [pvaccess.INT], "severity": [pvaccess.INT], "status": [pvaccess.INT]}}
	single_pv_value = {"labels": ["secondsPastEpoch", "values", "nanoseconds", "severity", "status"], "value": {"secondsPastEpoch": [1], "values": [123.45], "nanoseconds": [0], "severity": [0], "status": [0]}}
	pv_list = request['query']['pv'].split(",")
	if len(pv_list) == 1:
		single_pv_response = pvaccess.PvObject(single_pv_struct, single_pv_value,'NTComplexTable')
		return single_pv_response
	else:
		final_response_struct = pvaccess.PvObject({"value": [()]})
		result_list = []
		for pv in pv_list:
			pv_data = pvaccess.PvObject({"value": {"pvName": pvaccess.STRING, "value": single_pv_struct}},{"value": {"pvName": pv, "value": single_pv_value}})
			result_list.append(pv_data)
		final_response_struct.setUnionArray(result_list)
		return final_response_struct
	
srv.registerService('hist', handle_request)
srv.listen()