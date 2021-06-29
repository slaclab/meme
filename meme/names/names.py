import re
from p4p.client.thread import Context
from p4p.nt import NTTable, NTURI

ctx = Context('pva')
NameQueryURI = NTURI([('name', 's'), ('to', 's'), ('pv', 's')])

def directory_service_get(timeout=None, **kws):
  if timeout is None:
    timeout = 5.0
  NameQueryURI = NTURI([(key, 's') for key in kws])
  request = NameQueryURI.wrap("ds", scheme="pva", kws=kws)
  response = ctx.rpc("ds", request, timeout=timeout)
  return response

def _list(pattern, tag=None, sort_by=None, element_type=None, show=None, timeout=None):
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
  response = directory_service_get(timeout=timeout, name=pattern, tag=tag, sort=sort_by, etype=element_type, show=show)
  return [row['name'] for row in NTTable.unwrap(response)]

def list_pvs(pattern, tag=None, sort_by=None, element_type=None, timeout=None):
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
  return _list(pattern, tag=tag, sort_by=sort_by, element_type=element_type, timeout=timeout)

def list_devices(pattern, tag=None, sort_by=None, element_type=None, timeout=None):
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
  return _list(pattern, tag=tag, sort_by=sort_by, element_type=element_type, show="dname", timeout=timeout)

def list_elements(pattern, tag=None, sort_by=None, element_type=None, timeout=None):
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
  return _list(pattern, tag=tag, sort_by=sort_by, element_type=element_type, show="ename", timeout=timeout)
  
def device_to_element(device_name, timeout=None):
  """Given a device name or list of device names, get the corresponding element name(s).
     
    Args:
      device_name (str or list of str): Device name(s) to convert to element name(s).
        You can also specify device name patterns, or a list of device name patterns
        to search for, using Oracle-style wildcard syntax (like "BPMS:BSYH:%") or regex
        patterns (like "BPMS:(BSYH|LTUH|UNDH):.*").
    Returns:
      str or list of str: An element name or list of element names.
  """
  was_single_string = False
  if isinstance(device_name, str):
    if re.search("[.^$*+?{}()[\],\\\/|%]", device_name) == None:
      #This is a plain-old device name, not a pattern.
      was_single_string = True
    device_name = [device_name]
  responses = []
  for devname in device_name:
    response = directory_service_get(timeout=timeout, dname=devname, show="ename")
    responses.extend([row['name'] for row in NTTable.unwrap(response)])
  flattened_responses = []
  for item in responses:
    if isinstance(item, list):
      for name in item:
        flattened_responses.append(name)
    else:
        flattened_responses.append(item)
  if was_single_string:
    return flattened_responses[0]
  return flattened_responses

def element_to_device(element_name, timeout=None):
  """Given an element name or list of element names, get the corresponding device name(s).
     
    Args:
      element_name (str or list of str): Element name(s) to convert to device name(s).
        Note: Unlike :func:`device_to_element()`, the directory service does not support
        wildcards or regex patterns when converting from element names to device names.
    Returns:
      str or list of str: An element name or list of element names.
  """
  was_single_string = False
  if isinstance(element_name, str):
    was_single_string = True
    element_name = [element_name]
  responses = []
  for elename in element_name:
    response = directory_service_get(timeout=timeout, ename=elename, show="dname")
    responses.extend([row['name'] for row in NTTable.unwrap(response)])
  flattened_responses = []
  for item in responses:
    if isinstance(item, list):
      for name in item:
        flattened_responses.append(name)
    else:
        flattened_responses.append(item)
  if was_single_string:
    return flattened_responses[0]
  return flattened_responses
  
