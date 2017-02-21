import pvaccess
import numpy as np
from ..utils.nturi import NTURI

class Model(object):
	"""Holds the data for the full machine model, with convenient features for retrieving info.

	    The Model class represents model data for the full machine.  This class fetches the full
			machine model from the MEME model service, and caches it.  All class methods then operate
			on the cached data.  If you would like to refresh the cache, you can call the
			`refresh_rmat_data()`, `refresh_twiss_data()`, or `refresh_all()` methods, which will
			re-fetch the information from the model service.  Alternatively, you can use the Model's
			`no_caching` attribute to ensure that the model data is refreshed before any method call.
			Be warned though, this adds a significant delay to every call.
	    Properties created with the ``@property`` decorator should be documented
	    in the property's getter method.
	
			Args:
				initialize (:obj:`bool`, optional): Whether to fetch rmat and twiss data
		 			immediately upon initialization.  Defaults to True.  If initialize is 
					False, the data will be fetched the first time it is used.
				use_design (:obj:`bool`, optional): Use the design model, rather than the
					extant model.  Defaults to True.
				no_caching (:obj:`bool`, optional): If true, model-data will be re-fetched
					every time it is used.  This ensures you stay in-sync with the current
					model, but makes method calls in this class slower.  If you are worried
					about operators running and saving the model in-between uses of this
					class, you might consider setting no_caching to True.
	    """
	def __init__(self, initialize=True, use_design=False, no_caching=False):
		self.use_design = use_design
		self.no_caching = no_caching
		self.rmat_data = None
		self.twiss_data = None
		if initialize:
			self.refresh_all()
		
	def get_rmat(self, from_device, to_device=[], from_pos='MIDDLE', to_pos='MIDDLE', ignore_bad_names=False):
		"""Get 6x6 transfer matrices for one or more devices.
		
		This method operates in a few different modes:
			1. When a single 'from' device and a single 'to' device is specified, a
				single 6x6 transfer matrix will be returned.
			2. When a single 'from' device and a list of 'to' devices is specified, a
				list of matrices will be returned, one for each element in the 'to' list.
			3. When a list of 'from' devices, and a single 'to' device is specified, a
				list of matrices will be returned, one for each element in the 'from' list.
			4. When a list is specified for both 'from' and 'to' devices, a list of
				matrices will be returned, one for each pair in the two lists.  Note that
				in this mode, both device lists must be the same length.
			5. If only one device, or one list of devices is specified, it is assumed
				that a single 'from' device, the first element in the machine, is implied.
		
		Args:
			from_device (str or list of str): The starting device(s) for calculating the
				transfer matrices.
			to_device (str or list of str): The end device(s) for calculating the
				transfer matrices.
			from_pos (str, optional): For elements split into multiple sub-elements,
				this parameter specifies which sub-element to start the calculation from.
				Must be either "BEGIN", "MIDDLE", or "END".  Defaults to "MIDDLE".
			to_pos (str, optional): or elements split into multiple sub-elements,
				this parameter specifies which sub-element to end the calculation at.
				Must be either "BEGIN", "MIDDLE", or "END".  Defaults to "MIDDLE".
			ignore_bad_names (:obj:`bool`, optional): Whether or not to ignore device
				names which aren't present in the model.  If this option is True, and a
				device is not found in the model, a 6x6 matrix filled with np.nan will be 
				inserted for that device.
		
		Returns:
			np.ndarray: An array with shape Nx6x6, where N is the length of from_device
				or to_device
		"""
		if isinstance(from_device, str):
			from_device = [from_device]
		if isinstance(to_device, str):
			to_device = [to_device]
		if len(from_device) > 1 and len(to_device) > 1 and len(from_device) != len(to_device):
			raise Exception("Length of from_device must match length of to_device if both have length > 1.")
		if len(to_device) == 0:
			to_device = list(from_device)
			from_device = ['CATH:IN20:111'] #This probably shouldn't be hard-coded.
		if self.rmat_data is None or self.no_caching:
			self.refresh_rmat_data()
		device_list = zip(from_device, cycle(to_device)) if len(from_device) > len(to_device) else zip(cycle(from_device), to_device)
		rmats = np.zeros((len(device_list),6,6))
		i = 0
		for dev_pair in device_list:
			a, b = dev_pair
			a_index = np.where(self.rmat_data['epics_channel_access_name'] == a)
			if len(a_index[0]) > 1:
				a_index = a_index & (self.rmat_data['position_index'] == from_pos)
			b_index = np.where(self.rmat_data['epics_channel_access_name'] == b)
			if len(b_index[0]) > 1:
				b_index = b_index & (self.rmat_data['position_index'] == to_pos)
			try:
				a_mat = np.mat(self.rmat_data[a_index][0]['r_mat'])
			except IndexError:
				msg = "Device with name {name} not found in the machine model.".format(name=a)
				if ignore_bad_names:
					print(msg)
					a_mat = np.zeros((6,6))
					a_mat.fill(np.nan)
					a_mat = np.asmatrix(a_mat)
				else:
					raise IndexError(msg)
			try:
				b_mat = np.mat(full_model[b_index][0]['r_mat'])
			except IndexError:
				msg = "Device with name {name} not found in the machine model.".format(name=b)
				if ignore_bad_names:
					print(msg)
					b_mat = np.zeros((6,6))
					b_mat.fill(np.nan)
					b_mat = np.asmatrix(b_mat)
				else:
					raise IndexError(msg)
			rmats[i] = b_mat * np.linalg.inv(a_mat)
			i += 1
		if i == 1:
			return rmats[0]
		return rmats
	
	def get_zpos(device_list, pos='MIDDLE', ignore_bad_names=False):
		"""Get Z position for one or more devices.
		
		Args:
			device_list (str or list of str): The device(s) to get Z positions for.
			pos (str, optional): For elements split into multiple sub-elements,
				this parameter specifies which sub-element to get the position for.
				Must be either "BEGIN", "MIDDLE", or "END".  Defaults to "MIDDLE".
			ignore_bad_names (:obj:`bool`, optional): Whether or not to ignore device
				names which aren't present in the model.  If this option is True, and a
				device is not found in the model, np.nan will be inserted for that device.
		
		Returns:
			np.ndarray: A 1xN array of Z positions, where N=len(device_list)
		"""
		if isinstance(device_list, str):
			device_list = [device_list]
		if self.rmat_data is None or self.no_caching:
			self.refresh_rmat_data()
		z_pos = np.zeros((len(device_list)))
		i = 0
		for dev in device_list:
			dev_index = np.where(self.rmat_data['epics_channel_access_name'] == dev)
			if len(dev_index[0]) > 1:
				dev_index = dev_index & (self.rmat_data['position_index'] == pos)
			if len(dev_index[0]) == 1:
				z_pos[i] = self.rmat_data[dev_index][0]['z_position']
			else:
				msg = "Device with name {name} not found in the machine model, could not get Z position.".format(name=dev)
				if ignore_bad_names:
					print(msg)
					z_pos[i] = None
				else:
					raise IndexError(msg)
			i += 1
		if i == 1:
			return z_pos[0]
		return z_pos
	
	def get_twiss(device_list, pos='MIDDLE', ignore_bad_names=False):
		"""Get Z position for one or more devices.
		
		Args:
			device_list (str or list of str): The device(s) to get twiss parameters for.
			pos (str, optional): For elements split into multiple sub-elements,
				this parameter specifies which sub-element to get the twiss for.
				Must be either "BEGIN", "MIDDLE", or "END".  Defaults to "MIDDLE".
			ignore_bad_names (:obj:`bool`, optional): Whether or not to ignore device
				names which aren't present in the model.  If this option is True, and a
				device is not found in the model, np.nan will be inserted for that device.
		
		Returns:
			np.ndarray: A numpy structured array containing the twiss parameters for the
			requested devices.  The array has the following fields:
				* `leff` (float): The effective length of the device.
				* `total_energy` (float): The total energy of the beam at the device.
				* `psi_x` (float): The horizontal betatron phase advance at the device.
				* `beta_x` (float): The horizontal beta function value at the device.
				* `alpha_x` (float): The horizontal alpha function value at the device.
				* `eta_x` (float): The horizontal dispersion at the device.
				* `etap_x` (float): The horizontal second-order dispersion at the device.
				* `psi_y` (float): The vertical betatron phase advance at the device.
				* `beta_y` (float): The vertical beta function value at the device.
				* `alpha_y` (float): The vertical alpha function value at the device.
				* `eta_y` (float): The vertical dispersion at the device.
				* `etap_y` (float): The vertical second-order dispersion at the device.
		"""
		if isinstance(device_list, str):
			device_list = [device_list]
		if self.rmat_data is None or self.no_caching:
			self.refresh_twiss_data()
		twiss = np.zeros(len(device_list), dtype=[('leff', 'float32'), ('total_energy', 'float32'), ('psi_x', 'float32'), ('beta_x', 'float32'), ('alpha_x', 'float32'), ('eta_x', 'float32'), ('etap_x', 'float32'), ('psi_y', 'float32'), ('beta_y', 'float32'), ('alpha_y', 'float32'), ('eta_y', 'float32'), ('etap_y', 'float32')])
		i = 0
		for dev in device_list:
			dev_index = np.where(self.twiss_data['epics_channel_access_name'] == dev)
			if len(dev_index[0]) > 1:
				dev_index = dev_index & (self.twiss_data['position_index'] == pos)
			if len(dev_index[0]) == 1:
				twiss[i]['leff'] = self.twiss_data[dev_index][0]['leff']
				twiss[i]['total_energy'] = self.twiss_data[dev_index][0]['total_energy']
				twiss[i]['psi_x'] = self.twiss_data[dev_index][0]['psi_x']
				twiss[i]['beta_x'] = self.twiss_data[dev_index][0]['beta_x']
				twiss[i]['alpha_x'] = self.twiss_data[dev_index][0]['alpha_x']
				twiss[i]['eta_x'] = self.twiss_data[dev_index][0]['eta_x']
				twiss[i]['etap_x'] = self.twiss_data[dev_index][0]['etap_x']
				twiss[i]['psi_y'] = self.twiss_data[dev_index][0]['psi_y']
				twiss[i]['beta_y'] = self.twiss_data[dev_index][0]['beta_y']
				twiss[i]['alpha_y'] = self.twiss_data[dev_index][0]['alpha_y']
				twiss[i]['eta_y'] = self.twiss_data[dev_index][0]['eta_y']
				twiss[i]['etap_y'] = self.twiss_data[dev_index][0]['etap_y']
			else:
				msg = "Device with name {name} not found in the machine model, could not get twiss information.".format(name=dev)
				if ignore_bad_names:
					print(msg)
					twiss[i][:] = None
				else:
					raise IndexError(msg)
			i += 1
		if i == 1:
			return twiss[0]
		return twiss
	
	def refresh_rmat_data(self):
		self.rmat_data = full_machine_rmats(self.use_design)

	def refresh_twiss_data(self):
		self.twiss_data = full_machine_twiss(self.use_design)
	
	def refresh_all(self):
		self.refresh_rmat_data()
		self.refresh_twiss_data()
	
	

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
				* `total_energy` (float): The total energy of the beam at the element.
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