# -*- encoding: utf-8 -*-

#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
#  ***** GPL LICENSE BLOCK *****


import sys
sys.dont_write_bytecode = True


import pyext


from math import exp as math_exp
from traceback import format_exc as tb
from threading import Thread 
import numpy as np
from math import e as euler


platform = sys.platform
import platform as platf

def pydevBrk():      
    # adjust your path 
    platf1 = platf.platform()
    
    if platform == 'linux':
        # Ubuntu
        sys.path.append('/home/xgr/.eclipse/org.eclipse.platform_4.4.1_1473617060_linux_gtk_x86_64/plugins/org.python.pydev_4.0.0.201504132356/pysrc') 
        # Fedora
        #sys.path.append('/root/.p2/pool/plugins/org.python.pydev_4.4.0.201510052309/pysrc')     
    else:
        if 'Windows-10' in platf1:
            sys.path.append(r'C:/Users/xgr/.p2/pool/plugins/org.python.pydev_4.5.4.201601292234/pysrc') 
        else:
            sys.path.append(r'C:/Users/Homer/.p2/pool/plugins/org.python.pydev_4.4.0.201510052309/pysrc')
        # win10
        
    from pydevd import settrace
    settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True) 
         
pd = pydevBrk



        

 
class Signal_Delay(pyext._class):
    
    
    def __init__(self,*args):
        print('args:', args)
                 
        self.delay = np.fromiter([0 for x in range(4410 + 64)], np.float32)
            

    def _anything_(self,n,*args):
        #print("Message into inlet",n,":",args)
                
        str_arg = str(args[0])

        if str_arg.startswith('delay'):
            self.delay = np.fromiter([0 for x in range(abs(int(args[1])) + 64)], np.float32)
    
    def _signal(self):
        
        self.delay = np.append(self.delay[64:], self._invec(0) )            
        self._outvec(0)[:] = self.delay[:64]
        
import time        
class Msg_Delay(pyext._class):
    # doesn't work properly
    
    _inlets = 1
    _outlets = 1
    
    def __init__(self,*args):
        print('args:', args)
                 
        self.sleep_time = 1 / 1000. /44.1 * 64
            

    def _anything_(self,n,*args):
        #print("Message into inlet",args)
        print("Message into inlet",n,":",args)
        
        
        self._outlet(1,'hi') 
        
        str_arg = str(args[0])

        if str_arg.startswith('delay'):
            self.delay = np.fromiter([0 for x in range(abs(int(args[1])) + 64)], np.float32)
    
            
    def _signal(self,*args):
        print('sig')
        self.delay = np.append(self.delay[64:], self._invec(0) )            
        self._outvec(0)[:] = self.delay[:64]
        

        
    def bang_1(self,*args):
        """Do some scripting - PD only!"""
        print('#',args,'*')
        
        t = Thread(target=send_msg,args=(self,self.sleep_time))
        t.start()
        
    def float_1(self,*arg):
        """This is a class-local receive function, which has access to class members."""
        print(arg)
        self.sleep_time = 1 / 1000. /44.1 * int(arg[0])
        
    def float_0(self,*arg):
        """This is a class-local receive function, which has access to class members."""
        print(arg)
        
    def symbol_1(self,*arg):
        """This is a class-local receive function, which has access to class members."""
        print(arg)
        
    def pointer_1(self,*arg):
        """This is a class-local receive function, which has access to class members."""
        print(arg)
        

     
def send_msg(obj, t):
    time.sleep(t)
    obj._send("msg1","bang")
    
            
class Signal(pyext._class):
    
        
    def __init__(self,*args):
        print('args:', args)
                 
        self.delay = np.fromiter([0 for x in range(44100)], np.float32)
        self.running = False
            

    def _anything_(self,n,*args):
        print("Message into inlet",n,":",args)
        
        str_arg = str(args[0])
        
        if str_arg.startswith('start'):
            self.running = True
            return
        elif str_arg.startswith('stop'):
            self.running = False
            return
        
        delay = int(str(args[1]))

        if str_arg.startswith('signal_distance'):
            array = [ int( (x % delay) == 0) for x in range(44100)]
            
            self.delay = np.fromiter(array, np.float32)
            

    def _signal(self):
        
        if not self.running:
            return
 
        self._outvec(0)[:] = self.delay[:64]
        self.delay = np.append(self.delay[64:], self.delay[:64] )  


class FFT(pyext._class):
    
        
    def __init__(self,*args):
        print('args:', args)
        
        self.fft_window_size = 8184
        self.freq = 2000
        
        
        self.running = True
        
        self.out_vec = np.zeros((64,), dtype=np.float32)
        
        self.set_values()
            
    
    def set_values(self):
        try:
            self.window = self.gauss_window(self.fft_window_size)
            self.fft_window_size_cut = int(self.freq / 22500. * self.fft_window_size)
            self.ysl = np.zeros((self.fft_window_size,), dtype=np.float32) 
        except Exception as e:
            print(tb())
    
    def gauss_window(self, n):
    
        values = []
        N = n - 1
        
        alpha = euler 
        
        v = lambda k: np.exp( -1/2 * ( alpha * (k - N/2) / (N/2) )**2 )
        
        zero_dif = v(0)
        
        for x in range(N):
            values.append ( v(x) - zero_dif)
            
        values.append(values[0])
                
        return values
    
    
    def _anything_(self,n,*args):
        print("Message into inlet",n,":",args)
        
        str_arg = str(args[0])
        
        if str_arg.startswith('start'):
            self.running = True
            return
        elif str_arg.startswith('stop'):
            self.running = False
            return
        
        if str_arg.startswith('fft_window_size'):
            self.fft_window_size = int(str(args[1]))
            self.set_values()
        if str_arg.startswith('cut_freq'):
            self.freq = int(str(args[1]))
            self.set_values()
            
            
            

    def _signal(self):
        
        if not self.running:
            return
 
        try:
            invec = self._invec(0)
            self.ysl = np.append(self.ysl[64 :], self._invec(0) )
            fft = np.fft.rfft(self.ysl)# * self.window )
             
            # cut: don't show upper frequencies
            fft = fft[ : self.fft_window_size_cut ]
              
            fft_real = fft.real
            ysl1 = np.abs(fft_real)
            
            fft_imag = fft.imag
            ysl2 = np.abs(fft_imag)
            
            fft_calc = (np.sqrt( ysl1 + ysl2) / self.fft_window_size).astype(np.float32)[:-1]
            
            wert = np.max(fft_calc).astype(np.float32) *1000
            
            out = np.empty(64).astype(np.float32)
            out.fill(wert)
            #print(wert)
            self._outvec(0)[:] = out
            #pd()
        except Exception as e:
            print(tb())
            #pd()

class Test(pyext._class):
    
        
    def __init__(self,*args):
        print('args:', args)
            
        self.running = False   
        self.aufnahme = np.fromiter([], np.float32)
        

    def _anything_(self,n,*args):
        print("Message into inlet",n,":",args)
        
        print(self._arraysupport())
        self._tocanvas("editmode",1)
        print('#')
        
        str_arg = str(args[0])

        if str_arg.startswith('delay'):
            self.delay = np.fromiter([0 for x in range(int(args[1]) + 64)], np.float32)
            print(len(self.delay))
        elif str_arg.startswith('start'):
            self.running = True
        elif str_arg.startswith('stop'):
            self.running = False
            

            
    def _signal(self):

#         self.delay = np.append(self.delay[64:], self._invec(0) )            
#         self._outvec(0)[:] = self.delay[:64]
        
        try:
            
            if self.running:
                
                print(np.amax(self._invec(0)))
                
                
                
#                 welle = self._invec(0)
#                 w = welle * welle
                
                #self.aufnahme = np.append(self.aufnahme, w )
                #print('run')
#             else:
#                 if len(self.aufnahme) > 64:
#                     self._outvec(0)[:] = self.aufnahme[:64]
#                     self.aufnahme = self.aufnahme[64:]
                    #print(len(self.aufnahme))
                #print('stop')
        except:
            print(tb())
        
    def _array(self,*args):    
        print(args)
        
    def _s(self,*args):    
        print(args)
        
    def _s_bang(self,*args):    
        print(args)
        
    def _list(self,*args):    
        print(args)
        
    def _s_symbol(self,*args):    
        print(args)
        


def pr(locs,*args):
    print('')
    for a in args:
        print('{0}: {1}'.format(a,locs[a]))



        

class Max(pyext._class):
    
    
    def __init__(self,*args):
        print('args:', args)
                 

            

    def _anything_(self,n,*args):
        #print("Message into inlet",n,":",args)
                
        str_arg = str(args[0])

        if str_arg.startswith('delay'):
            self.delay = np.fromiter([0 for x in range(abs(int(args[1])) + 64)], np.float32)
    
    def _signal(self):
        
        invec = self._invec(0)

        wert = np.max(invec).astype(np.float32) 
        
        out = np.empty(len(invec)).astype(np.float32)
        out.fill(wert)
        #print(wert)
        self._outvec(0)[:] = out
            
            
            
class DX(pyext._class):
    
    
    def __init__(self,*args):
        print('args:', args)
                 
        self.sig = np.fromiter([0 for x in range(512)], np.float32)
        self.old = 0
        self.out = np.empty(64).astype(np.float32)
            

    def _anything_(self,n,*args):
        #print("Message into inlet",n,":",args)
                
        str_arg = str(args[0])

        if str_arg.startswith('dx'):
            length = abs(int(args[1]))
            self.sig = np.fromiter([0 for x in range(length)], np.float32)
            
    
    def _signal(self):
        
        self.sig = np.append(self.sig[64:], self._invec(0) )  
        new = np.sum(self.sig)
        dx = new - self.old
        self.old = new        
        self.out.fill(dx)
        self._outvec(0)[:] = self.out      




