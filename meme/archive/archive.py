from p4p.client.thread import Context
from p4p.nt import NTTable, NTURI
import pandas as pd
import dateutil.parser
import pytz
from datetime import datetime

local_time_zone = pytz.timezone('US/Pacific')
ctx = Context('pva')
ArchiveQueryURI = NTURI([('from', 's'), ('to', 's'), ('pv', 's')])

def hist_service_get(timeout=None, **kws):
  if timeout is None:
    timeout = 5.0
  query_dict = {key.lstrip("_"): val for key, val in kws.items()}
  request = ArchiveQueryURI.wrap("hist", scheme="pva", kws=query_dict)
  return ctx.rpc("hist", request, timeout=timeout)

def convert_datetime_to_UTC(naive_datetime):
  local_datetime = local_time_zone.localize(naive_datetime, is_dst=None)
  utc_datetime = local_datetime.astimezone(pytz.utc)
  utc_datetime = utc_datetime.replace(tzinfo=None)
  return utc_datetime

def iso8601_string_from_datetime(dt):
  return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

def get(pv, from_time=None, to_time=None, timeout=None):
  """Gets history data from the archive service.
  
  Args:
    pv (str or list of str): A PV (or list of PVs) to get history data for.
      The archive engine can perform processing on the data before returning it
      to you.  To process data, you can ask for a PV wrapped in a processing
      function.  For example, to bin the data into 3600 second-wide bins, and
      take the mean of each bin, ask for "mean_3600(YOUR:PV:NAME:HERE)".  For
      full documentation of all the processing operators, see the
      `EPICS Archiver Appliance User Guide <https://slacmshankar.github.io/epicsarchiver_docs/userguide.html>`_.
    from_time (str or datetime, optional): The start time for the data.  Can be a
      string, like "1 hour ago" or "now", or a python datetime object.  If you
      use a datetime object, and do not specify UTC or GMT for the timezone, 
      a timezone of 'US/Pacific' is implied.
    to_time (str or datetime, optional): The end time for the data.  The same
      rules as `from_time` apply.
  Returns:
    dict or list of dicts: A data structure with the following fields:

    * `secondsPastEpoch` (list of ints): The UNIX timestamp for each history point.
    * `values` (list of float): The values for each history point.
    * `nanoseconds` (list of ints): The number of nanoseconds past the timestamp for each history point.
    * `severity` (list of int): The severity value for the PV at each history point.
    * `status` (list of int): The status value for the PV at each history point.
    
    If more than one PV was requested, a list of dicts will be returned.
    Each item in the list has the following fields:
  
    * `pvName` (str): The PV that this structure represents.
    * `value` (dict): A dict with the data for the PV.  Has the following fields:
  
      * `value` (dict): Holds the data for the PV.  Same fields as the single-PV
        case, documented above.
      * `labels` (list of str): The names of the fields in the value structure.
  
  """
  multiple_pvs = False
  if isinstance(pv, str):
    pvlist = pv
  else:
    pvlist = ",".join(pv)
    if len(pv) > 1:
      multiple_pvs = True
  if isinstance(from_time, datetime):
    if from_time.tzinfo is None or from_time.tzinfo.tzname(from_time) not in ("UTC", "GMT"):
      from_time = convert_datetime_to_UTC(from_time)
    from_time = iso8601_string_from_datetime(from_time)
  if isinstance(to_time, datetime):
    if to_time.tzinfo is None or to_time.tzinfo.tzname(to_time) not in ("UTC", "GMT"):
      to_time = convert_datetime_to_UTC(to_time)
    to_time = iso8601_string_from_datetime(to_time)
  response = hist_service_get(pv=pvlist, _from=from_time, _to=to_time, timeout=timeout)
  if multiple_pvs:
    return [item.todict() for item in response.value]
  else:
    return response.value.todict()

def convert_to_dataframe(archive_data):
    """Convert archive data returned by :func:`meme.archive.get` to a pandas dataframe. 
  
    Args:
      archive_data (dict or list of dicts): A dictionary, or list of dictionaries of archive data, in the format returned by
      :func:`meme.archive.get`.
    Returns:
      pandas.DataFrame: A pandas DataFrame object with a column for the values of each PV.
      
      The DataFrame is indexed on timestamp, with nanosecond level precision.  All data is
      is joined on the timestamps, and filled when there are gaps, so every column has data
      for every timestamp.
    """
    import pandas as pd
    flattened_data = {}
    if isinstance(archive_data, dict):
        # If this was a single PV, wrangle into the format for multiple PVs.
        archive_data = {"pvName": "value", "value": {"value": archive_data}}
        archive_data = [archive_data]
        
    for pv_data in archive_data:
        pv_name = pv_data['pvName']
        flattened_data[pv_name] = {"secondsPastEpoch": pv_data['value']['value']["secondsPastEpoch"],
                                             "nanoseconds": pv_data['value']['value']['nanoseconds'],
                                             "values": pv_data['value']['value']['values']}
    # Now we make data frames for each PV, then join them all together.
    dfs = []
    for pv_name in flattened_data:
        df = pd.DataFrame.from_dict(flattened_data[pv_name])
        df['datetime'] = pd.to_datetime(df["secondsPastEpoch"]*1.0e9 + df["nanoseconds"])
        df.set_index('datetime', inplace=True)
        del(df['nanoseconds'])
        del(df['secondsPastEpoch'])
        df.rename(columns={'values': pv_name}, inplace=True)
        dfs.append(df)
    # Now join all the individual data frames together, and fill gaps in timestamps
    all_data = dfs[0].join(dfs[1:], how='outer')
    all_data.fillna(method="ffill", inplace=True)
    all_data.fillna(method="bfill", inplace=True)
    return all_data