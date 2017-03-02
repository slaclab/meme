import pvaccess
import os
import pickle
from collections import OrderedDict

rmat_data = None
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rmat_data.pkl')) as f:
	rmat_data = pickle.load(f)

twiss_data = None
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'twiss_data.pkl')) as f:
  twiss_data = pickle.load(f)

if rmat_data is None or twiss_data is None:
  raise Exception("Could not load saved rmat or twiss data.")

def generate_rmat_table():
  cols = OrderedDict([('ORDINAL', pvaccess.DOUBLE), ('ELEMENT_NAME', pvaccess.STRING), ('EPICS_CHANNEL_ACCESS_NAME', pvaccess.STRING), ('POSITION_INDEX', pvaccess.STRING), ('Z_POSITION', pvaccess.DOUBLE), ('R11', pvaccess.DOUBLE), ('R12', pvaccess.DOUBLE), ('R13', pvaccess.DOUBLE), ('R14', pvaccess.DOUBLE), ('R15', pvaccess.DOUBLE), ('R16', pvaccess.DOUBLE), ('R21', pvaccess.DOUBLE), ('R22', pvaccess.DOUBLE), ('R23', pvaccess.DOUBLE), ('R24', pvaccess.DOUBLE), ('R25', pvaccess.DOUBLE), ('R26', pvaccess.DOUBLE), ('R31', pvaccess.DOUBLE), ('R32', pvaccess.DOUBLE), ('R33', pvaccess.DOUBLE), ('R34', pvaccess.DOUBLE), ('R35', pvaccess.DOUBLE), ('R36', pvaccess.DOUBLE), ('R41', pvaccess.DOUBLE), ('R42', pvaccess.DOUBLE), ('R43', pvaccess.DOUBLE), ('R44', pvaccess.DOUBLE), ('R45', pvaccess.DOUBLE), ('R46', pvaccess.DOUBLE), ('R51', pvaccess.DOUBLE), ('R52', pvaccess.DOUBLE), ('R53', pvaccess.DOUBLE), ('R54', pvaccess.DOUBLE), ('R55', pvaccess.DOUBLE), ('R56', pvaccess.DOUBLE), ('R61', pvaccess.DOUBLE), ('R62', pvaccess.DOUBLE), ('R63', pvaccess.DOUBLE), ('R64', pvaccess.DOUBLE), ('R65', pvaccess.DOUBLE), ('R66', pvaccess.DOUBLE)])
  
  pvObject = pvaccess.PvObject({'labels' : [pvaccess.STRING], 'value' : {key: [val] for key, val in cols.items()}})
  pvObject.setScalarArray('labels', cols.keys())
  pvObject.setStructure('value', {key: rmat_data['value'][key] for key in cols.keys()})

  table = pvaccess.NtTable(pvObject)
  return table

def generate_twiss_table():
  cols = OrderedDict([('ORDINAL', pvaccess.DOUBLE), ('ELEMENT_NAME', pvaccess.STRING), ('EPICS_CHANNEL_ACCESS_NAME', pvaccess.STRING), ('POSITION_INDEX', pvaccess.STRING), ('LEFF', pvaccess.DOUBLE), ('TOTAL_ENERGY', pvaccess.DOUBLE), ('PSI_X', pvaccess.DOUBLE), ('BETA_X', pvaccess.DOUBLE), ('ALPHA_X', pvaccess.DOUBLE), ('ETA_X', pvaccess.DOUBLE), ('ETAP_X', pvaccess.DOUBLE), ('PSI_Y', pvaccess.DOUBLE), ('BETA_Y', pvaccess.DOUBLE), ('ALPHA_Y', pvaccess.DOUBLE), ('ETA_Y', pvaccess.DOUBLE), ('ETAP_Y', pvaccess.DOUBLE)])
  
  pvObject = pvaccess.PvObject({'labels' : [pvaccess.STRING], 'value' : {key: [val] for key, val in cols.items()}})
  pvObject.setScalarArray('labels', cols.keys())
  pvObject.setStructure('value', {key: twiss_data['value'][key] for key in cols.keys()})

  table = pvaccess.NtTable(pvObject)
  return table

rmat_table = generate_rmat_table()
twiss_table = generate_twiss_table()

def handle_twiss_request(request):
	return twiss_table

def handle_rmat_request(request):
  return rmat_table

srv = pvaccess.RpcServer()
srv.registerService('MODEL:TWISS:EXTANT:FULLMACHINE', handle_twiss_request)
srv.registerService('MODEL:TWISS:DESIGN:FULLMACHINE', handle_twiss_request)
srv.registerService('MODEL:RMATS:EXTANT:FULLMACHINE', handle_rmat_request)
srv.registerService('MODEL:RMATS:DESIGN:FULLMACHINE', handle_rmat_request)
srv.listen()