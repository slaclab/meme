import pvaccess
import numpy as np
from ..utils.nturi import NTURI

def full_machine_rmats(use_design=False):
	"""Gets the full machine model from the MEME optics service.
	
	Args:
		use_design (bool, optional): Whether or not to use the design model, rather
			than the extant model.  Defaults to False.
	Returns:
		numpy.ndarray: A numpy structured array containing the model data.  The array
			has the following fields:
				* `ordinal` (int): The ordinal index for the element.  An element with a
					low ordinal number always comes before a high ordinal number.
				* `element_name` (str): The element name for the element.
				* `epics_channel_access_name` (str): The device name for the element.
				* `position_index` (str): For elements which are split into multiple
					sub-elements, this is the sub-element position. Either "BEGIN", "MIDDLE",
		 			or "END".
				* `z_position` (float): The Z position for the element.  Note that Z
					position of 0 refers to the start of the entire SLAC linac, NOT the start
					of LCLS.
				* `r_mat` (6x6 np.ndarray of floats): The 6x6 transport matrix for this element.
	"""
	model_type = "EXTANT"
	if use_design:
		model_type = "DESIGN"
	path = "MODEL:RMATS:{}:FULLMACHINE".format(model_type)
	rpc = pvaccess.RpcClient(path)
	request = NTURI(scheme='pva', path=path)
	response = rpc.invoke(request).getStructure()
	m = np.zeros(len(response['ELEMENT_NAME']), dtype=[('ordinal', 'i16'),('element_name', 'a60'), ('epics_channel_access_name', 'a60'), ('position_index', 'a6'), ('z_position', 'float32'), ('r_mat', 'float32', (6,6))])
	m['ordinal'] = response['ORDINAL']
	m['element_name'] = response['ELEMENT_NAME']
	m['epics_channel_access_name'] = response['EPICS_CHANNEL_ACCESS_NAME']
	m['position_index'] = response['POSITION_INDEX']
	m['z_position'] = response['Z_POSITION']
	m['r_mat'] = np.reshape(np.array([response['R11'], response['R12'], response['R13'], response['R14'], response['R15'], response['R16'], response['R21'], response['R22'], response['R23'], response['R24'], response['R25'], response['R26'], response['R31'], response['R32'], response['R33'], response['R34'], response['R35'], response['R36'], response['R41'], response['R42'], response['R43'], response['R44'], response['R45'], response['R46'], response['R51'], response['R52'], response['R53'], response['R54'], response['R55'], response['R56'], response['R61'], response['R62'], response['R63'], response['R64'], response['R65'], response['R66']]).T, (-1,6,6))
	return m
	
def full_machine_twiss(use_design=False):
	"""Gets twiss parameters for the full machine from the MEME optics service.
	
	Args:
		use_design (bool, optional): Whether or not to use the design model, rather
			than the extant model.  Defaults to False.
	Returns:
		numpy.ndarray: A numpy structured array containing the model data.  The array
			has the following fields for each element:
				* `ordinal` (int): The ordinal index for the element.  An element with a
					low ordinal number always comes before a high ordinal number.
				* `element_name` (str): The element name for the element.
				* `epics_channel_access_name` (str): The device name for the element.
				* `position_index` (str): For elements which are split into multiple
					sub-elements, this is the sub-element position. Either "BEGIN", "MIDDLE",
		 			or "END".
				* `leff` (float): The effective length of the element.
				* `total_energy`: The total energy of the beam at the element.
				* `psi_x` (float): The horizontal betatron phase advance at the element.
				* `beta_x` (float): The horizontal beta function value at the element.
				* `alpha_x` (float): The horizontal alpha function value at the element.
				* `eta_x` (float): The horizontal dispersion at the element.
				* `etap_x` (float): The horizontal second-order dispersion at the element.
				* `psi_y` (float): The vertical betatron phase advance at the element.
				* `beta_y` (float): The vertical beta function value at the element.
				* `alpha_y` (float): The vertical alpha function value at the element.
				* `eta_y` (float): The vertical dispersion at the element.
				* `etap_y` (float): The vertical second-order dispersion at the element.
	"""
	model_type = "EXTANT"
	if use_design:
		model_type = "DESIGN"
	path = "MODEL:TWISS:{}:FULLMACHINE".format(model_type)
	rpc = pvaccess.RpcClient(path)
	request = NTURI(scheme='pva', path=path)
	response = rpc.invoke(request).getStructure()
	m = np.zeros(len(response['ELEMENT_NAME']), dtype=[('ordinal', 'i16'),('element_name', 'a60'), ('epics_channel_access_name', 'a60'), ('position_index', 'a6'), ('leff', 'float32'), ('total_energy', 'float32'), ('psi_x', 'float32'), ('beta_x', 'float32'), ('alpha_x', 'float32'), ('eta_x', 'float32'), ('etap_x', 'float32'), ('psi_y', 'float32'), ('beta_y', 'float32'), ('alpha_y', 'float32'), ('eta_y', 'float32'), ('etap_y', 'float32')])
	m['ordinal'] = response['ORDINAL']
	m['element_name'] = response['ELEMENT_NAME']
	m['epics_channel_access_name'] = response['EPICS_CHANNEL_ACCESS_NAME']
	m['position_index'] = response['POSITION_INDEX']
	m['leff'] = response['LEFF']
	m['total_energy'] = response['TOTAL_ENERGY']
	m['psi_x'] = response['PSI_X']
	m['beta_x'] = response['BETA_X']
	m['alpha_x'] = response['ALPHA_X']
	m['eta_x'] = response['ETA_X']
	m['etap_x'] = response['ETAP_X']
	m['psi_y'] = response['PSI_Y']
	m['beta_y'] = response['BETA_Y']
	m['alpha_y'] = response['ALPHA_Y']
	m['eta_y'] = response['ETA_Y']
	m['etap_y'] = response['ETAP_Y']
	return m