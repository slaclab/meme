import unittest
import meme.archive
from datetime import datetime, timedelta

class ArchiveGetTest(unittest.TestCase):
  def test_single_pv_as_string(self):
    r = meme.archive.get("MC00:ASTS:OUTSIDET")
    self.assertTrue(isinstance(r, dict))
    self.assert_single_pv_response_has_correct_fields(r)
  
  def test_single_pv_as_list(self):
    r = meme.archive.get(["MC00:ASTS:OUTSIDET"])
    self.assertTrue(isinstance(r, dict))
    self.assert_single_pv_response_has_correct_fields(r)
    
  def test_multiple_pvs(self):
    r = meme.archive.get(["MC00:ASTS:OUTSIDET", "QUAD:IN20:425:BDES"])
    self.assertTrue(isinstance(r, list))
    self.assert_multi_pv_response_has_correct_fields(r)
  
  def test_date_args_as_strings(self):
    from_time_str = "1 hour ago"
    to_time_str = "30 minutes ago"
    #Because we calculate our "now" before we send the request, which may
    #be a little different than when the archiver recieves the request,
    #this might fail.
    now = datetime.now()
    from_time = now - timedelta(hours=1)
    to_time = now - timedelta(minutes=30)
    r = meme.archive.get("MC00:ASTS:OUTSIDET", from_time=from_time_str, to_time=to_time_str)
    self.assert_times_within_range(r['secondsPastEpoch'], parsed_from_time, parsed_to_time)
  
  def test_date_args_as_datetimes(self):
    to_time = datetime.now()
    from_time = to_time - timedelta(hours=1)
    r = meme.archive.get("MC00:ASTS:OUTSIDET", from_time=from_time, to_time=to_time)
    self.assert_times_within_range(r['secondsPastEpoch'], from_time, to_time)
  
  def assert_times_within_range(self, times, begin_time, end_time):
    from_time_stamp = (begin_time - datetime(1970,1,1)).total_seconds()
    to_time_stamp = (end_time - datetime(1970,1,1)).total_seconds()
    self.assertTrue(min(times) >= begin_timestamp)
    self.assertTrue(max(times) <= end_timestamp)
    
  def assert_single_pv_response_has_correct_fields(self, response):
    self.assertTrue('status' in response)
    self.assertTrue('secondsPastEpoch' in response)
    self.assertTrue('values' in response)
    self.assertTrue('nanoseconds' in response)
    self.assertTrue('severity' in response)

  def assert_multi_pv_response_has_correct_fields(self, response):
    self.assertTrue('pvName' in response)
    self.assertTrue('value' in response)
    self.assert_single_pv_response_has_correct_fields(response['value'])