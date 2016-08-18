# pd_scopes

pd_scopes displays live waveforms in puredata.
Up to 4 scopes can display 4 different waveforms at the same time.

The scopes are calculated on the gpu (Thanks to the team of vispy!) and are running in an external thread, so fluidly working with pd is still possible.

- Y-values can be adjusted automatically.
- Waveforms might be zoomed and dragged in x and y direction.
- Drag- and zoom-state can be transferred to other scopes.
- A marker can be set and transferred to other scopes.
- The length of the recorded wavefile can be adjusted (44100 = 1 sec, 2205000 = 50 sec). 

Usage:
* LMB + drag: drag x
* RMB + drag: zoom y
* Wheel: zoom x
* LMB + RMB + drag: drag y
* press Wheel: set marker

Download the files pd_scopes.py, pd_scopes.pd and Scopes.pd and put them into the same folder.
Copy a soundfile to that folder.
Open pd_scopes.pd with pd and change the name of the soundfile in the messagebox for [readsf~] or use some other input for the scopes.

Click on [Scopes] for further options.


Prerequisites are:
- python installation 
- numpy, PyQt and vispy installed for python
- py/pyext for puredata

Tested setups:
win7 / win10, python 2.7.4 / 2.7.11, PyQt4, vispy0.5.0dev0



