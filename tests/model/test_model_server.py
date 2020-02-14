from p4p import Type, Value
from p4p.nt import NTTable
from p4p.server.thread import SharedPV
from p4p.server import Server
import os
import sys
import pickle
from collections import OrderedDict

rmat_data = None
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rmat_data.pkl'), 'rb') as f:
	rmat_data = pickle.load(f)

twiss_data = None
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'twiss_data.pkl'), 'rb') as f:
  twiss_data = pickle.load(f)

if rmat_data is None or twiss_data is None:
  raise Exception("Could not load saved rmat or twiss data.")

twiss_cols = [('ORDINAL', 'd'), ('ELEMENT_NAME', 's'), ('EPICS_CHANNEL_ACCESS_NAME', 's'), ('POSITION_INDEX', 's'), ('LEFF', 'd'), ('TOTAL_ENERGY', 'd'), ('PSI_X', 'd'), ('BETA_X', 'd'), ('ALPHA_X', 'd'), ('ETA_X', 'd'), ('ETAP_X', 'd'), ('PSI_Y', 'd'), ('BETA_Y', 'd'), ('ALPHA_Y', 'd'), ('ETA_Y', 'd'), ('ETAP_Y', 'd')]
twiss_table = NTTable(twiss_cols)
rows = [{key: twiss_data['value'][key][i] for key, _ in twiss_cols} for i in range(0,len(twiss_data['value']['ELEMENT_NAME']))]
twiss_vals = twiss_table.wrap(rows)
twiss_pv = SharedPV(nt=twiss_table, initial=twiss_vals)

rmat_cols = [('ORDINAL', 'd'), ('ELEMENT_NAME', 's'), ('EPICS_CHANNEL_ACCESS_NAME', 's'), ('POSITION_INDEX', 's'),('Z_POSITION', 'd'),
('R11', 'd'), ('R12', 'd'), ('R13', 'd'), ('R14', 'd'), ('R15', 'd'), ('R16', 'd'),
('R21', 'd'), ('R22', 'd'), ('R23', 'd'), ('R24', 'd'), ('R25', 'd'), ('R26', 'd'),
('R31', 'd'), ('R32', 'd'), ('R33', 'd'), ('R34', 'd'), ('R35', 'd'), ('R36', 'd'),
('R41', 'd'), ('R42', 'd'), ('R43', 'd'), ('R44', 'd'), ('R45', 'd'), ('R46', 'd'),
('R51', 'd'), ('R52', 'd'), ('R53', 'd'), ('R54', 'd'), ('R55', 'd'), ('R56', 'd'),
('R61', 'd'), ('R62', 'd'), ('R63', 'd'), ('R64', 'd'), ('R65', 'd'), ('R66', 'd')]
rmat_table = NTTable(rmat_cols)
rows = [{key: rmat_data['value'][key][i] for key, _ in rmat_cols} for i in range(0,len(rmat_data['value']['ELEMENT_NAME']))]
rmat_vals = rmat_table.wrap(rows)
rmat_pv = SharedPV(nt=rmat_table, initial=rmat_vals)

@twiss_pv.rpc
def twiss_request_handler(pv, op):
  op.done(twiss_vals)

@rmat_pv.rpc
def rmat_request_handler(pv, op):
  op.done(rmat_vals)
print("Starting Model Service Test Server!")
Server.forever(providers=[{
  'MODEL:TWISS:EXTANT:FULLMACHINE': twiss_pv,
  'MODEL:TWISS:DESIGN:FULLMACHINE': twiss_pv,
  'MODEL:RMATS:EXTANT:FULLMACHINE': rmat_pv,
  'MODEL:RMATS:DESIGN:FULLMACHINE': rmat_pv
}])