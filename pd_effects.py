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



        

 
class Delay(pyext._class):
    
        
    def __init__(self,*args):
        print('args:', args)
                 
        self.delay = np.fromiter([0 for x in range(4410 + 64)], np.float32)
            

    def _anything_(self,n,*args):
        print("Message into inlet",n,":",args)
        
        str_arg = str(args[0])

        if str_arg.startswith('delay'):
            self.delay = np.fromiter([0 for x in range(int(args[1]) + 64)], np.float32)
            print(len(self.delay))

            
    def _signal(self):

        self.delay = np.append(self.delay[64:], self._invec(0) )            
        self._outvec(0)[:] = self.delay[:64]

            




def pr(locs,*args):
    print('')
    for a in args:
        print('{0}: {1}'.format(a,locs[a]))



        



