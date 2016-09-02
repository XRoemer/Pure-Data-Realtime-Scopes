# Pure Data Scopes

pd_scopes displays waveforms and spectograms in realtime.
Up to 4 scopes can display 4 different waveforms or spectograms.

The scopes are calculated on the gpu (Thanks to the team of vispy!) and are running in an external thread, so fluidly working with pd is still possible.

- Y-values can be adjusted automatically.
- Waveforms might be zoomed and dragged in x and y direction.
- Drag- and zoom-state can be transferred to other scopes.
- A marker can be set and transferred to other scopes.
- The length of the recorded wavefile can be adjusted (44100 = 1 sec, 2205000 = 50 sec). 

Usage:
* LMB + drag:    drag x
* RMB + drag:    zoom y
* Wheel: zoom x
* LMB + RMB + drag: drag y
* press Wheel: set marker
* press Wheel + Control: set all markers
* Wheel + Control + Shift: resize scope

Buttons: 
* adjust y: set all windows to the y-range of data button 
* m: set all markers to selected button 
* tr: transfer zoom and pos x to others 

Slider: 
* left: boost color 
* middle: adjust point size 
* right: cut display of frequencies (slider goes from 0 - 100% of the highest value)



Download the zip file and extract.
Copy a soundfile to that folder.
Open pd_scopes_example.pd with pd and change the name of the soundfile in the messagebox or use some other input for the scopes.
Turn up volume, press start, press open and start dsp.


Prerequisites are:
- python installation and py/pyext for puredata
- numpy, PyQt and vispy installed for the python installation, py/pyext recognizes
 

Tested setups:

win7 / win10, 

python 2.7.4 / 2.7.11, 

PyQt4, 

vispy0.5.0dev0



![alt tag](https://github.com/XRoemer/Pure-Data-Realtime-Scopes/blob/master/images/scope_and_spectogram2.png)


