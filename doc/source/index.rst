.. MEME Tools for Python documentation master file, created by
   sphinx-quickstart on Tue Feb 21 14:41:46 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MEME Tools for Python
=====================
MEME Tools for Python, known as 'meme', is a python wrapper for the MEME
(MAD EPICS MATLAB Environment) services at SLAC.  The meme 
wrapper aims to hide away EPICS v4 boilerplate code where possible, and provide
a simple, easy to learn API for interacting with the various MEME services.

meme is split up into sub-modules, one for each MEME service. So far, the
services implemented in python are:

* **archive**: Use the MEME archive service to get history data for one or more PVs.
* **model**: Use the MEME model service get machine model data (R-matrices, Twiss parameters, Z-Positions) for beamline elements.
* **names**: Use the MEME directory service to list PVs, element names, or device names.

Note that MEME has more services than the meme wrapper implements.  The goal is
to implement all MEME services over time.

Contents:

.. toctree::
   :maxdepth: 2
   
   gettingstarted
   meme/model/model
   meme/names/names
   meme/archive/archive

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

