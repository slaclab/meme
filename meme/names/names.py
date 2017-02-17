import pvaccess
from ..utils.nturi import NTURI
from collections import OrderedDict

def directory_service_get(**kws):
	query_dict = kws
	query_struct = {}
	for key in query_dict:
		query_struct[key] = pvaccess.STRING
	path = "ds"
	request = NTURI(scheme="pva", path=path, query=kws)
	rpc = pvaccess.RpcClient(path)
	response = rpc.invoke(request).getStructure()
	return response