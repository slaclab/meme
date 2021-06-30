import sys
from p4p.client.thread import Context
from p4p.nt import NTTable, NTURI
import numpy as np
from itertools import cycle

class NumpyNTTable(NTTable):
     # Note: There's a 60 character limit on strings
     # in the numpy.ndarray that we return.  This gives the end user a nostalgic
     # feeling for the era of resource-limited computing.
    p4p_to_numpy_dtype = {
        "a?": "?",
        "as": "U60",
        "ab": "i1",
        "aB": "u1",
        "ah": "i2",
        "aH": "u2",
        "ai": "i4",
        "aI": "u4",
        "al": "i8",
        "aL": "u8",
        "af": "f4",
        "ad": "f8"
    }

    def wrap(self, structured_array):
        """Turn a numpy structured array into a NTTable"""
        if isinstance(values, Value):
            return values
            
        try:
            cols = {label: structured_array[label] for label in self.labels}
            return self.Value(self.type, {
                'labels': self.labels,
                'value': cols
            })
        except:
            _log.error("Failed to encode '%s' with %s", cols, self.labels)
            raise

    @staticmethod
    def unwrap(value):
        col_names = value.value.keys()
        if sys.version_info[0] < 3:
          col_names = [n.encode('utf-8') for n in col_names]
        # We need to get the dtype info for each column.  This lives in the 
        # following location:
        col_types = value.type().items()[1][1].items()
        np_types = [NumpyNTTable.p4p_to_numpy_dtype[t] for _, t in col_types]
        m = np.zeros(len(value.value.items()[0][1]), dtype=list(zip(col_names, np_types)))
        for col, val in value.value.items():
            m[col] = val
        return m
  
    @staticmethod
    def assign(val, obj):
        val.value = obj

# We use a custom subclass of NTTable that wraps/unwraps to a numpy structured array.
ctx = Context('pva', nt={"epics:nt/NTTable:1.0": NumpyNTTable})

class Model(object):
    """Holds the data for the full machine model, with convenient features for retrieving info.
    
    The Model class represents model data for the full machine.  This class fetches the full
    machine model from the MEME model service, and caches it.  All class methods then operate
    on the cached data.  If you would like to refresh the cache, you can call the
    :func:`refresh_rmat_data()`, :func:`refresh_twiss_data()`, or :func:`refresh_all()` methods, which will
    re-fetch the information from the model service.  Alternatively, you can use the Model's
    `no_caching` attribute to ensure that the model data is refreshed before any method call.
    Be warned though, this adds a significant delay to every call.
  
    Args:
      initialize (bool, optional): Whether to fetch rmat and twiss data
        immediately upon initialization.  Defaults to True.  If initialize is 
        False, the data will be fetched the first time it is used.
      use_design (bool, optional): Use the design model, rather than the
        extant model.  Defaults to True.
      no_caching (bool, optional): If true, model-data will be re-fetched
        every time it is used.  This ensures you stay in-sync with the current
        model, but makes method calls in this class slower.  If you are worried
        about operators running and saving the model in-between uses of this
        class, you might consider setting no_caching to True.
    
    Examples:
      >>> from meme.model import Model
      >>> m = Model()
      >>> m.get_rmat('BPMS:LI24:801')
      <np.ndarray>
    """
    def __init__(self, model_name, initialize=True, use_design=False, no_caching=False):
        self.model_name = str(model_name).upper()
        self.use_design = use_design
        self.no_caching = no_caching
        self.rmat_data = None
        self.twiss_data = None
        if initialize:
            self.refresh_all()
    
    def get_rmat(self, from_device, to_device=[], ignore_bad_names=False):
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
          ignore_bad_names (bool, optional): Whether or not to ignore device
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
        device_list = list(zip(from_device, cycle(to_device))) if len(from_device) > len(to_device) else list(zip(cycle(from_device), to_device))
        rmats = np.zeros((len(device_list),6,6))
        i = 0
        for dev_pair in device_list:
            a, b = dev_pair
            a_index = np.where(self.rmat_data['device_name'] == a)
            #if len(a_index[0]) > 1:
                #a_index = a_index & (self.rmat_data['position_index'] == from_pos)
            b_index = np.where(self.rmat_data['device_name'] == b)
            #if len(b_index[0]) > 1:
                #b_index = b_index & (self.rmat_data['position_index'] == to_pos)
            try:
                a_mat = self.rmat_data[a_index][0]['r_mat']
            except IndexError:
                msg = "Device with name {name} not found in the machine model.".format(name=a)
                if ignore_bad_names:
                    print(msg)
                a_mat = np.empty((6,6))
                a_mat.fill(np.nan)
            else:
                raise IndexError(msg)
            try:
                b_mat = self.rmat_data[b_index][0]['r_mat']
            except IndexError:
                msg = "Device with name {name} not found in the machine model.".format(name=b)
                if ignore_bad_names:
                    print(msg)
                    b_mat = np.empty((6,6))
                    b_mat.fill(np.nan)
                else:
                    raise IndexError(msg)
            rmats[i] = np.matmul(b_mat,np.linalg.inv(a_mat))
            i += 1
        if i == 1:
            return rmats[0]
        return rmats
    
    def get_zpos(self, device_list, ignore_bad_names=False):
        """Get Z position for one or more devices.  NOTE: This is actually
        returning the 's' position of the device (so, the integrated distance
        along the beamline).
        
        Args:
            device_list (str or list of str): The device(s) to get Z positions for.
            ignore_bad_names (bool, optional): Whether or not to ignore device
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
            dev_index = np.where(self.rmat_data['device_name'] == dev)
            #if len(dev_index[0]) > 1:
                #dev_index = dev_index & (self.rmat_data['position_index'] == pos)
            if len(dev_index[0]) == 1:
                z_pos[i] = self.rmat_data[dev_index][0]['s']
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
    
    def get_twiss(self, device_list, ignore_bad_names=False):
        """Get Z position for one or more devices.
        
        Args:
            device_list (str or list of str): The device(s) to get twiss parameters for.
            pos (str, optional): For elements split into multiple sub-elements,
                this parameter specifies which sub-element to get the twiss for.
                Must be either "BEGIN", "MIDDLE", or "END".  Defaults to "MIDDLE".
            ignore_bad_names (bool, optional): Whether or not to ignore device
                names which aren't present in the model.  If this option is True, and a
                device is not found in the model, np.nan will be inserted for that device.
        
        Returns:
            np.ndarray: A numpy structured array containing the twiss parameters for the
                requested devices.  The array has the following fields:
                
                * `length` (float): The effective length of the device.
                
                * `p0c` (float): The total energy of the beam at the device.
                
                * `alpha_x` (float): The horizontal alpha function value at the device.
                
                * `beta_x` (float): The horizontal beta function value at the device.
                
                * `eta_x` (float): The horizontal dispersion at the device.
                
                * `etap_x` (float): The horizontal second-order dispersion at the device.
                
                * `psi_x` (float): The horizontal betatron phase advance at the device.
                
                * `alpha_y` (float): The vertical alpha function value at the device.
                
                * `beta_y` (float): The vertical beta function value at the device.
                
                * `eta_y` (float): The vertical dispersion at the device.
                
                * `etap_y` (float): The vertical second-order dispersion at the device.
                
                * `psi_y` (float): The vertical betatron phase advance at the device.
        """
        if isinstance(device_list, str):
            device_list = [device_list]
        if self.rmat_data is None or self.no_caching:
            self.refresh_twiss_data()
        twiss = np.zeros(len(device_list), dtype=[('length', 'float32'), ('p0c', 'float32'), ('alpha_x', 'float32'), ('beta_x', 'float32'), ('eta_x', 'float32'), ('etap_x', 'float32'), ('psi_x', 'float32'), ('alpha_y', 'float32'), ('beta_y', 'float32'), ('eta_y', 'float32'), ('etap_y', 'float32'), ('psi_y', 'float32')])
        i = 0
        for dev in device_list:
            dev_index = np.where(self.twiss_data['device_name'] == dev)
            #if len(dev_index[0]) > 1:
                #dev_index = dev_index & (self.twiss_data['position_index'] == pos)
            if len(dev_index[0]) == 1:
                twiss[i]['length'] = self.twiss_data[dev_index][0]['length']
                twiss[i]['p0c'] = self.twiss_data[dev_index][0]['p0c']
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
        """Refresh the R-Matrix data from the MEME optics service."""
        self.rmat_data = full_machine_rmats(self.model_name, self.use_design)
    
    def refresh_twiss_data(self):
        """Refresh the Twiss data from the MEME optics service."""
        self.twiss_data = full_machine_twiss(self.model_name, self.use_design)
    
    def refresh_all(self):
        """Refresh the R-Matrix and Twiss data from the MEME optics service."""
        self.refresh_rmat_data()
        self.refresh_twiss_data()

def full_machine_rmats(model_name, use_design=False):
    """Gets the full machine model from the MEME optics service.
    
    Args:
        use_design (bool, optional): Whether or not to use the design model, rather
        than the extant model.  Defaults to False.
    Returns:
        numpy.ndarray: A numpy structured array containing the model data.  The array
        has the following fields:
            * `element` (str): The element name for the element.
            * `device_name` (str): The device name for the element.
            * `s` (float): The s position for the element.  Note that s
              position of 0 refers to the start of the entire SLAC linac, NOT the start
              of LCLS.
            * `r_mat` (6x6 np.ndarray of floats): The 6x6 transport matrix for this element.
    """
    model_type = "LIVE"
    if use_design:
        model_type = "DESIGN"
    path = "SIMULACRUM:SYS0:1:{}:{}:RMAT".format(model_name, model_type)
    response = ctx.get(path)
    m = np.zeros(len(response['element']), dtype=[('element', 'U60'), ('device_name', 'U60'), ('s', 'float32'), ('r_mat', 'float32', (6,6))])
    m['element'] = response['element']
    m['device_name'] = response['device_name']
    m['s'] = response['s']
    m['r_mat'] = np.reshape(np.array([response['r11'], response['r12'], response['r13'], response['r14'], response['r15'], response['r16'], response['r21'], response['r22'], response['r23'], response['r24'], response['r25'], response['r26'], response['r31'], response['r32'], response['r33'], response['r34'], response['r35'], response['r36'], response['r41'], response['r42'], response['r43'], response['r44'], response['r45'], response['r46'], response['r51'], response['r52'], response['r53'], response['r54'], response['r55'], response['r56'], response['r61'], response['r62'], response['r63'], response['r64'], response['r65'], response['r66']]).T, (-1,6,6))
    return m

def full_machine_twiss(model_name, use_design=False):
    """Gets twiss parameters for the full machine from the MEME optics service.
    
    Args:
        use_design (bool, optional): Whether or not to use the design model, rather
        than the extant model.  Defaults to False.
    Returns:
        numpy.ndarray: A numpy structured array containing the model data.  The array
        has the following fields for each element:
            * `element` (str): The element name for the element.
            * `device_name` (str): The device name for the element.
            * `length` (float): The effective length of the element.
            * `p0c` (float): The total energy of the beam at the element.
            * `alpha_x` (float): The horizontal alpha function value at the element.
            * `beta_x` (float): The horizontal beta function value at the element.
            * `eta_x` (float): The horizontal dispersion at the element.
            * `etap_x` (float): The horizontal second-order dispersion at the element.
            * `psi_x` (float): The horizontal betatron phase advance at the element.
            * `alpha_y` (float): The vertical alpha function value at the element.
            * `beta_y` (float): The vertical beta function value at the element.
            * `eta_y` (float): The vertical dispersion at the element.
            * `etap_y` (float): The vertical second-order dispersion at the element.
            * `psi_y` (float): The vertical betatron phase advance at the element.
    """
    model_type = "LIVE"
    if use_design:
        model_type = "DESIGN"
    path = "SIMULACRUM:SYS0:1:{}:{}:TWISS".format(model_name, model_type)
    return ctx.get(path)
