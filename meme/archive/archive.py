import pvaccess
from ..utils.nturi import NTURI
from datetime import datetime
import dateutil.parser
import pytz
local_time_zone = pytz.timezone('US/Pacific')

def hist_service_get(**kws):
  query_dict = {key.lstrip("_"): val for key, val in kws.items()}
  query_struct = {}
  for key in query_dict:
    query_struct[key] = pvaccess.STRING
  path = "hist"
  request = NTURI(scheme="pva", path=path, query=query_dict)
  rpc = pvaccess.RpcClient(path)
  return rpc.invoke(request)

def convert_datetime_to_UTC(naive_datetime):
  loacl_datetime = local_time_zone.localize(naive_datetime, is_dst=None)
  utc_datetime = local_datetime.astimezone(pytz.utc)
  utc_datetime = utc_datetime.replace(tzinfo=None)
  return utc_datetime

def iso8601_string_from_datetime(dt):
  return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get(pv, from_time=None, to_time=None):
  """Gets history data from the archive service.
  
  Args:
    pv (str or list of str): A PV (or list of PVs) to get history data for.
    from_time (str or datetime, optional): The start time for the data.  Can be a
      string, like "1 hour ago" or "now", or a python datetime object.  If you
      use a datetime object, and do not specify UTC or GMT for the timezone, 
      a timezone of 'US/Pacific' is implied.
    to_time (str or datetime, optional): The end time for the data.  The same
      rules as `from_time` apply.
  Returns:
    dict: A data structure with the following fields:
    * value (structure): Holds the history data.  It has the following fields
      * secondsPastEpoch (list of ints): The UNIX timestamp for each history 
      point.
      * values (list of float): The values for each history point.
      * nanoseconds (list of ints): The number of nanoseconds past the
      timestamp for each history point.
      * severity (list of int): The severity value for the PV at each history
      point
      * status (list of int): The status value for the PV at each history
      point
    * labels (list of str): The names of the fields in the value structure.
  
    If more than one PV was requested, a list of dicts will be returned.
    Each item in the list has the following fields:
    * pvName (str): The PV that this structure represents.
    * value (dict): A data structure with the fields described above.
  """
  if isinstance(pv, str):
    pvlist = pv
    multiple_pvs = False
  else:
    pvlist = ",".join(pv)
    multiple_pvs = True
  if isinstance(from_time, datetime):
    if from_time.tzinfo is None or from_time.tzinfo.tzname(from_time) not in ("UTC", "GMT"):
      from_time = convert_datetime_to_UTC(from_time)
    from_time = iso8601_string_from_datetime(from_time)
  if isinstance(to_time, datetime):
    if to_time.tzinfo is None or to_time.tzinfo.tzname(to_time) not in ("UTC", "GMT"):
      to_time = convert_datetime_to_UTC(to_time)
    to_time = iso8601_string_from_datetime(from_time)
  response = hist_service_get(pv=pvlist, _from=from_time, _to=to_time)
  if multiple_pvs:
    return [item.getStructure() for item in response.getUnionArray()]
  else:
    return response.getStructure()
  
