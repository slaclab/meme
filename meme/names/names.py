from p4p.client.thread import Context
from p4p.nt import NTTable, NTURI

ctx = Context('pva')
NameQueryURI = NTURI([('name', 's'), ('to', 's'), ('pv', 's')])

def directory_service_get(timeout=None, **kws):
  timeout = 5.0 if timeout is None
  NameQueryURI = NTURI([(key, 's') for key in kws])
	request = NameQueryURI.wrap("ds", scheme="pva", kws=kws)
	response = ctx.rpc("ds", request, timeout=timeout)
	return response

def list(pattern, tag=None, sort_by=None, element_type=None, show=None):
	"""Gets a list of PVs, device names, or element names from the directory service.
	
	Args:
		pattern (str): A pattern to search for.  The pattern can use an Oracle-style
			wildcard syntax, like this: "BPMS:BSY:%:X", where % is the wildcard symbol,
			or a regular expression, like this: "(XCOR|BPMS):.*".
		tag (str, optional): A tag to filter the results by.  Tags come from the
			model system, and are used to group a region of devices.  Some commonly-used
			tags: L1, L2, L3, BSY, LTU, UND, DUMPLINE.
		sort_by (str, optional): A property to sort the reults by. sort_by="z" is
			very commonly used.
		element_type (str, optional): An element type to filter the results by.  For
			example, you can show only instruments by passing element_type="INST".
		show (str, optional): The type of name to return.  When 'show' is not
			specified, a list of PVs (something like "BPMS:LI24:801:X") will be
			returned. When 'show' is 'dname', a list of device names (something like
		 	"BPMS:LI24:801") will be returned .  When 'show' is 'ename', a list of
			element names (something like "BPM24801") will be returned.
	Returns:
		list of str: A list of names matching the parameters sent.
	"""
	response = directory_service_get(name=pattern, tag=tag, sort=sort_by, etype=element_type, show=show)
  return [row['name'] for row in NTTable.unwrap(response)]

def list_pvs(pattern, tag=None, sort_by=None, element_type=None):
	"""Gets a list of PVs from the directory service.
	
	Equivalent to calling :meth:`list` without specifying the show parameter.
	
	Args:
		pattern (str): A pattern to search for.  The pattern can use an Oracle-style
			wildcard syntax, like this: "BPMS:BSY:%:X", where % is the wildcard symbol,
			or a regular expression, like this: "(XCOR|BPMS):.*".
		tag (str, optional): A tag to filter the results by.  Tags come from the
			model system, and are used to group a region of devices.  Some commonly-used
			tags: L1, L2, L3, BSY, LTU, UND, DUMPLINE.
		sort_by (str, optional): A property to sort the reults by. sort_by="z" is
			very commonly used.
		element_type (str, optional): An element type to filter the results by.  For
			example, you can show only instruments by passing element_type="INST".
	Returns:
		list of str: A list of PVs matching the parameters sent.
	"""
	return list(pattern, tag, sort_by, element_type)

def list_devices(pattern, tag=None, sort_by=None, element_type=None):
	"""Gets a list of PVs from the directory service.  
	
	Equivalent to calling :meth:`list` with show='dname'.
	
	Args:
		pattern (str): A pattern to search for.  The pattern can use an Oracle-style
			wildcard syntax, like this: "BPMS:BSY:%:X", where % is the wildcard symbol,
			or a regular expression, like this: "(XCOR|BPMS):.*".
		tag (str, optional): A tag to filter the results by.  Tags come from the
			model system, and are used to group a region of devices.  Some commonly-used
			tags: L1, L2, L3, BSY, LTU, UND, DUMPLINE.
		sort_by (str, optional): A property to sort the reults by. sort_by="z" is
			very commonly used.
		element_type (str, optional): An element type to filter the results by.  For
			example, you can show only instruments by passing element_type="INST".
	Returns:
		list of str: A list of device names matching the parameters sent.
	"""
	return list(pattern, tag, sort_by, element_type, show="dname")

def list_elements(pattern, tag=None, sort_by=None, element_type=None):
	"""Gets a list of PVs from the directory service.
	
	Equivalent to calling :meth:`list` with show="ename".
	
	Args:
		pattern (str): A pattern to search for.  The pattern can use an Oracle-style
			wildcard syntax, like this: "BPMS:BSY:%:X", where % is the wildcard symbol,
			or a regular expression, like this: "(XCOR|BPMS):.*".
		tag (str, optional): A tag to filter the results by.  Tags come from the
			model system, and are used to group a region of devices.  Some commonly-used
			tags: L1, L2, L3, BSY, LTU, UND, DUMPLINE.
		sort_by (str, optional): A property to sort the reults by. sort_by="z" is
			very commonly used.
		element_type (str, optional): An element type to filter the results by.  For
			example, you can show only instruments by passing element_type="INST".
	Returns:
		list of str: A list of element names matching the parameters sent.
	"""
	return list(pattern, tag, sort_by, element_type, show="ename")
	

