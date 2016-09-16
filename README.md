# Pure Data Scopes

pd_scopes displays waveforms and spectrograms in realtime.
Up to 5 scopes can display 5 different waveforms or spectrograms.

![alt tag](https://github.com/XRoemer/Pure-Data-Realtime-Scopes/blob/master/images/scopes_pd.png)

The scopes are calculated on the gpu (Thanks to the team of vispy!) and are running in an external thread, so fluidly working with pd is still possible.

The spectrograms are still highly cpu intensive.

- Y-values can be adjusted automatically.
- Waveforms might be zoomed and dragged in x and y direction.
- Drag- and zoom-state can be transferred to other scopes.
- A marker can be set and transferred to other scopes.
- The length of the recorded wavefile can be adjusted (44100 = 1 sec, 2205000 = 50 sec). 
- Playback of recorded sounds

Usage:
* LMB + drag:    drag x
* RMB + drag:    zoom y
* Wheel: zoom x
* LMB + RMB + drag: drag y
* press Wheel: set marker
* press Wheel + Control: set all markers to the same window position (not sample position!)
* Wheel + Control + Shift: resize scope
* press Wheel + Alt: when playback was activated, plays file between clicked position and blue markline

Buttons: 
* adjust y: set all windows to the y-range of data 
* m: set markers of other scopes to position of the marker of the clicked scope
* tr: transfer zoom and position on x-axis to other scopes 
* playback: stop recording and start the ability for a playback

Slider: 
* left: boost color 
* middle: adjust point size 
* right: cut display of frequencies (slider goes from 0 - 100% of the highest value)



Download the zip file and extract.
Copy a soundfile to the samples folder.
Open pd_scopes_example.pd with pd and change the name of the soundfile in the messagebox or use some other input for the scopes.
Turn up volume, start the loop player, open scopes and start dsp.


For using pd_scopes outside of the example, one needs to copy pd_scopes.pd and the folder python with pd_scopes3.py 
The spectrogram has a delay of half of the fft window size. Therefore one might use tools/pd_sig_delay.pd and python/effects.py, which create a sample based delay.



Prerequisites are:
- python installation and py/pyext for puredata
- numpy, PyQt and vispy installed for the python installation, py/pyext recognizes
 

Tested setups:

win7 / win10, 

python 2.7.4 / 2.7.11, 

PyQt4, 

vispy0.5.0dev0



![alt tag](https://github.com/XRoemer/Pure-Data-Realtime-Scopes/blob/master/images/scope_and_spectogram2.png)


