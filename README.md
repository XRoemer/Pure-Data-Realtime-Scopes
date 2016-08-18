# pd_scopes

pd_scopes displays live waveforms in puredata.

The scopes are calculated on the gpu (Thanks to the team of vispy!) and are running in an external thread, so fluidly working with pd is still possible.

Prerequisites are:
- python installation 
- numpy, PyQt and vispy installed for python
- py/pyext for puredata

Tested setups:
win7 / win10, python 2.7.4 / 2.7.11, PyQt4, vispy0.5.0dev0
