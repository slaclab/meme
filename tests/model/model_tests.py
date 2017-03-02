import unittest
from meme.model import Model
import numpy as np
import subprocess
import sys

class ModelTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.server_process = subprocess.Popen([sys.executable, '-m', 'tests.model.test_model_server'])
    
  def test_get_rmat_single_element(self):
    m = Model()
    self.assertEqual(m.get_rmat("BPMS:IN20:221").shape, (6,6))
    
  def test_get_rmat_one_list(self):
    m = Model()
    dev_list = ["BPMS:IN20:221", "BPMS:LI24:801", "BPMS:LTU1:250"]
    rs = m.get_rmat(dev_list)
    self.assertEqual(rs.shape, (len(dev_list),6,6))
  
  def test_get_rmat_from_a_to_list(self):
    m = Model()
    dev_list = ["BPMS:IN20:731", "BPMS:LI24:801", "BPMS:LTU1:250"]
    rs = m.get_rmat("BPMS:IN20:221", dev_list)
    self.assertEqual(rs.shape, (len(dev_list),6,6))
  
  def test_get_rmat_from_list_to_b(self):
    m = Model()
    dev_list = ["BPMS:IN20:731", "BPMS:LI24:801", "BPMS:LTU1:250"]
    rs = m.get_rmat(dev_list, "BPMS:LTU1:450")
    self.assertEqual(rs.shape, (len(dev_list),6,6))
  
  def test_get_rmat_from_list_to_list(self):
    m = Model()
    a_list = ["BPMS:IN20:731", "BPMS:LI24:801", "BPMS:LTU1:250"]
    b_list = ["BPMS:LI22:201", "BPMS:LI26:201", "BPMS:LTU1:450"]
    rs = m.get_rmat(a_list, b_list)
    self.assertEqual(rs.shape, (len(a_list),6,6))
  
  def test_get_zpos_single_element(self):
    m = Model()
    self.assertTrue(isinstance(m.get_zpos("BPMS:IN20:221"), float))
  
  def test_get_zpos_list(self):
    m = Model()
    dev_list = ["BPMS:IN20:221", "BPMS:LI24:801", "BPMS:LTU1:250"]
    zs = m.get_zpos(dev_list)
    self.assertEqual(len(dev_list), len(zs))
  
  def test_get_twiss_single_element(self):
    m = Model()
    t = m.get_twiss("BPMS:IN20:221")
    self.assert_has_twiss_fields(t)
  
  def test_get_twiss_list(self):
    m = Model()
    dev_list = ["BPMS:IN20:221", "BPMS:LI24:801", "BPMS:LTU1:250"]
    ts = m.get_twiss(dev_list)
    self.assertEqual(len(dev_list), len(ts))
  
  def assert_has_twiss_fields(self, t):
    names = t.dtype.names
    self.assertTrue('leff' in names)
    self.assertTrue('total_energy' in names)
    self.assertTrue('psi_x' in names)
    self.assertTrue('beta_x' in names)
    self.assertTrue('alpha_x' in names)
    self.assertTrue('eta_x' in names)
    self.assertTrue('etap_x' in names)
    self.assertTrue('psi_y' in names)
    self.assertTrue('beta_y' in names)
    self.assertTrue('alpha_y' in names)
    self.assertTrue('eta_y' in names)
    self.assertTrue('etap_y' in names)
  
  @classmethod
  def tearDownClass(cls):
    cls.server_process.terminate()
    cls.server_process.wait()