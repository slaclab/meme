import pvaccess
from collections import OrderedDict

class NTURI(pvaccess.PvObject):
	def __init__(self, scheme, path, authority=None, query=None):
		structure_dict = OrderedDict()
		structure_dict['scheme'] = pvaccess.STRING
		if authority is not None:
			structure_dict['authority'] = pvaccess.STRING
		structure_dict['path'] = pvaccess.STRING
		if query is not None:
			q = {key: pvaccess.STRING for key in query if query[key] is not None}
			structure_dict['query'] = q
		
		value_dict = OrderedDict()
		value_dict['scheme'] = scheme
		if authority is not None:
			value_dict['authority'] = authority
		value_dict['path'] = path
		if query is not None:
			value_dict['query'] = query	
		super(NTURI, self).__init__(structure_dict, value_dict, 'epics:nt/NTURI:1.0')