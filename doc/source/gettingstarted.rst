Getting Started
===============


Archive
-------
Getting history data via MEME is very straightforward.  There is only one
method: :func:`meme.archive.get`.

>>> import meme.archive
>>> meme.archive.get(["MC00:ASTS:OUTSIDET", "PWR:MCC0:1:SITE"], from_time="1 day ago", to_time="now")
<Results snipped>

You can supply a list of PVs, or just a single PV. The from_time and to_time 
parameters can take strings of the form "1 day ago", python datetime objects,
or a mix:

>>> from datetime import datetime
>>> import meme.archive
>>> downtime_2016 = datetime(2016, 12, 20)
>>> meme.archive.get("GDET:FEE1:241:ENRC", from_time="1 year ago", to_time=downtime_2016)
<Results snipped>

The :doc:`Archive Module Documentation <meme/archive/archive>` provides details
about the format that history data is returned as, and other useful tidbits.

Model
-----
Interacting with the model takes an object oriented approach.  To get model
data, first make an instance of the :class:`meme.model.Model` class, then call its methods to
get the data you are interested in:

>>> from meme.model import Model
>>> m = Model()
>>> m.get_rmat('BPMS:LI24:801')
<6x6 np.ndarray>

The model module works this way to keep things fast: usually, its faster to
get the full machine model once, then refer to it repeatedly, than it is to
repeatedly ask the model service for small bits of information.  Whenever you
make a new instance of Model, you'll get the latest data from the service.  If
you'd like to refresh the data for an existing instance, you can do that by
calling :meth:`meme.model.Model.refresh_all`:

>>> from meme.model import Model
>>> m = Model()
>>> twiss = m.get_twiss('QUAD:LTU1:440')
>>> m.refresh_all() #The beam energy has changed and you want a new model.
>>> new_twiss = m.get_twiss('QUAD:LTU1:440')

The various `get` methods in the Model class are pretty flexible.  You can
input a list of names, a single name, etc.  See the :doc:`Model documentation <meme/model/model>` for all the
details.

Names
-----
Getting lists of PV names is easy.  If you know how to use aidalist, you know
how to use :func:`meme.names.list_pvs`:

>>> import meme.names
>>> all_bpm_tmit_pvs = meme.names.list_pvs("BPMS:%:%:TMIT")
<list of BPM TMIT PVs>

The directory service is very powerful, and lets you do fancy queries with
sorting and filtering.  You can specify a tag to search for, like an LCLS
region:

>>> import meme.names
>>> L2_xcor_bacts = meme.names.list_pvs("XCOR:%:BACT", tag="L2", sort_by="z")
<list of XCOR BACT values for L2>

You can also get device names, or element names (aka MAD names), using the
:func:`meme.names.list_devices` and :func:`meme.names.list_elements` functions.
They take the same arguments as `list_pvs()`.  To get a list of all BPM devices
in the 'BSYLTU' line:

>>> import meme.names
>>> bsy_ltu_bpms = meme.names.list_devices("BPMS:%", tag="BSYLTU", sort_by="z") 
['BPMS:BSYH:445', 'BPMS:BSYH:465', ...]

For more information about the syntax for searching, and other parameters you
can pass to the various list functions, see the 
:doc:`Names documentation <meme/names/names>`.