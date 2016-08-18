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
#sys.dont_write_bytecode = True

from PyQt4 import QtGui, QtCore

import pyext

from vispy import app, gloo
from vispy import visuals
from vispy.visuals.transforms import STTransform, NullTransform
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.util.transforms import perspective, translate, rotate

from functools import partial
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


win_geometry = QtCore.QRect(200, 200, 840, 580)
       
class Main_Window(QtGui.QMainWindow):
    def __init__(self, caller, open_graph_on_top):
        super(Main_Window, self).__init__()
        
        self.caller = caller

        if open_graph_on_top:
            QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        else:
            QtGui.QMainWindow.__init__(self, None)

        self.setGeometry(win_geometry)  
        self.update()
    
    def closeEvent(self,event):
        self.caller.started = False
        global win_geometry
        win_geometry = self.geometry()
        

 
class Scopes(pyext._class):
    
    def __init__(self,*args):
        print('args:', args)
                 
        self.signal = { i : np.array([], np.float32) for i in range(4) }
        self.amount_scopes = 1
        self.scopes = {}
        
        self.buffer_multi = 30
        self.smpls_all = 44100
        self.amount_samples = 64 * self.buffer_multi    
        self.amount_curves = self.smpls_all / self.amount_samples + 1
        
        self.buffer = 0
        self.buffer_counter = 0
        self.update_pos_line = 30
        
        self.open_graph_on_top = 1
        self.started = False
        
        self.zaehler = 0
        self.texte_args = None, None, None
            
            
    def set_anzahl(self):  
        self.amount_samples = 64 * self.buffer_multi 
        self.amount_curves = self.smpls_all / self.amount_samples + 1

    
    def _anything_(self,n,*args):
        #print("Message into inlet",n,":",args)
        
        str_arg = str(args[0])

        try:
            if str_arg.startswith('scopes'):
                self.amount_scopes = int(args[1])
                
            elif str_arg.startswith('samples'):
                self.smpls_all = int(args[1])
                self.set_anzahl()
                
            elif str_arg.startswith('buffer_multi'):
                self.buffer_multi = int(args[1])
                self.set_anzahl()
                
            elif str_arg.startswith('update_pos_line'):
                self.update_pos_line = int(args[1])
                
            elif str_arg.startswith('open_graph_on_top'):
                self.open_graph_on_top = int(args[1])
                
            elif str_arg.startswith('open_scopes'):
                
                if self.started:
                    return
                else:
                    self.started = True
                
                t = Thread(target=self.start_v,args=())
                t.start()
                                
        except:
            print(tb())

    
    def start_v(self):
        
        try:                
            oApp = app.use_app()
            oApp.native.aboutToQuit.connect(oApp.native.deleteLater)
            
            self.win = Main_Window(self, 1)

            self.gui()
            self.win.setCentralWidget(self.top_widget)
            self.win.show()

            oApp.run()
               
        except Exception as e:
            print(tb())
              
                         
    def adjust_y(self):

        for a in range(self.amount_scopes):
            scope = self.scopes[a]
            data = scope.y[0]
            maxi = max(0, np.amax(data))
            mini = min(0, np.amin(data))
            
            positions, null_pos = berechne_abstaende_y_Achse(maxi, mini)
            
            if maxi - mini == 0:
                adjust = 1
            else:
                adjust = 2 / (maxi - mini)
            
            scope.program['adjust_y'] = adjust
            scope.program['drag_y'] = null_pos
            scope.drag_y = null_pos
            scope.program['zoom_y'] = 1
            scope.zoom_y = 1
            
            # Update der 0-Linie
            model = translate((0, null_pos, 0))
            scope.xAchse['model'] = model
            
            # Update der Skalierungsanzeige
            scope.yAxis.max_y = maxi 
            scope.yAxis.min_y = mini
            
            scope.yAxis.drag_y = 0
            scope.yAxis.zoom_y = 1
            scope.yAxis.positions = positions  
            scope.yAxis.update()
            
            scope.update()
    

    def set_markers_to_selected(self,*ev):
        
        nr = ev[0][0]
        scope = self.scopes[nr]
        pos = scope.pos_markline
        
        for a in range(self.amount_scopes):
            if a != nr:
                scope = self.scopes[a]
                scope.pos_markline = pos
                scope.setze_markierungslinie()

    
    def set_xrange_to_selected(self,*ev):
        
        nr = ev[0][0]
        scope = self.scopes[nr]
        versatz = scope.program['versatz'][0]
        drag_x = scope.program['drag_x'][0]
        zoom_x = scope.program['zoom_x'][0]
        sichtbare = scope.sichtbare
        positions = scope.xAxis.positions
        pos = scope.pos_markline
        
        for a in range(self.amount_scopes):
            if a != nr:
                scope = self.scopes[a]
                scope.program['versatz'] = float(versatz)
                scope.program['drag_x'] = float(drag_x)
                scope.program['zoom_x'] = float(zoom_x)
                scope.drag_x = float(drag_x)
                scope.sichtbare = sichtbare
                
                scope.setze_markierungslinie()
                
                scope.xAxis.positions = positions  
                scope.xAxis.update()
                
                scope.update()
                
                                        
    def gui(self):
        
        ## top-level widget to hold everything
        self.top_widget = QtGui.QWidget()
        self.top_widget.setStyleSheet('QWidget {color: #c9c9c9; background-color: #333333}')

        toplayout = QtGui.QGridLayout()
        self.top_widget.setLayout(toplayout)
        toplayout.setSpacing(0)
        
        btn_y_zoom = QtGui.QPushButton('adjust y')
        btn_y_zoom.setStyleSheet('QPushButton {color: #c9c9c9; background-color: #474747}')
        btn_y_zoom.clicked.connect(self.adjust_y)
        
        ####
        widget_head = QtGui.QWidget()
        layout_head = QtGui.QGridLayout()
        widget_head.setLayout(layout_head)
        layout_head.setSpacing(0)

        #void QGridLayout::addWidget(  fromRow,  fromColumn,  rowSpan,  columnSpan,  alignment = 0)
        toplayout.addWidget(widget_head, 0, 1, 1, 2)
        layout_head.addWidget(btn_y_zoom, 1, 3, 1, 1)
        
#         curvePen = pg.mkPen(color=(50, 50, 255))
        
        for a in range(self.amount_scopes):
         
            xAxis = XAxis()
            yAxis = YAxis()
            self.scopes[a] = Canvas(self.smpls_all, xAxis, yAxis, self.scopes) 
            self.scopes[a].widget = self.top_widget
             
            widget = QtGui.QWidget()
            layout = QtGui.QGridLayout()
            widget.setLayout(layout)
            layout.setSpacing(0)
            layout.setContentsMargins(10, 0, 20, 5)
             
            toplayout.addWidget(widget, 4 + a,1,1,2)
            layout.addWidget(self.scopes[a].native, 0,2,1,1)
              
            btn_marker = QtGui.QPushButton('m')
            btn_marker.setStyleSheet('QPushButton {color: #c9c9c9; background-color: #474747}')
            btn_marker.clicked.connect(partial( self.set_markers_to_selected,(a, 'marker')) )
              
            btn_y_transfer = QtGui.QPushButton('tr')
            btn_y_transfer.setStyleSheet('QPushButton {color: #c9c9c9; background-color: #474747}')
            btn_y_transfer.clicked.connect(partial(self.set_xrange_to_selected, (a, 'transfer')) )
            btn_y_transfer.setObjectName("newGame")
              
            widget_scope_btns = QtGui.QWidget()
            widget_scope_btns.setFixedWidth(40)
            widget_scope_btns.setFixedHeight(25)
  
            layout_scope_btns = QtGui.QGridLayout()
            widget_scope_btns.setLayout(layout_scope_btns)
            layout_scope_btns.setSpacing(2)
            layout_scope_btns.setContentsMargins(0,5,5,0)
              
            layout_scope_btns.addWidget(btn_marker, 0, 0, 1, 1)
            layout_scope_btns.addWidget(btn_y_transfer, 0, 1, 1, 1)
            layout.addWidget(widget_scope_btns, 2,1,1,1)
            
            layout.addWidget(xAxis, 2,2,1,1)
            xAxis.setFixedHeight(25)
            
            layout.addWidget(yAxis, 0,1,1,1) 
            yAxis.setFixedWidth(40)

            
    def _signal(self):
        '''
        Drawing of the Plot Window
        '''
                
        try:
            
            if not self.started:
                return
            
            if self.buffer_counter + 64 >= self.smpls_all:
                noch_zu_schreibende = self.smpls_all -1 - self.buffer_counter
                
                for i in range(self.amount_scopes):
                    ysl1 = self._invec(i)[:noch_zu_schreibende]
                    ysl2 = self._invec(i)[noch_zu_schreibende:]
                    
                    self.scopes[i].y[0][self.buffer_counter: self.buffer_counter + noch_zu_schreibende] = ysl1
                    self.scopes[i].y[0][: 64 - noch_zu_schreibende] = ysl2
                    
                    self.scopes[i].program['position'].set_data(self.scopes[i].y)
                
                
                self.buffer_counter = 64 - noch_zu_schreibende
                self.zaehler = 0
                
                for i in range(self.amount_scopes):
                    
                    pos = -1 + (self.smpls_all / (64 - noch_zu_schreibende)) + self.scopes[i].program['versatz'][0]
                    self.scopes[i].prg_poslinie['model'] = translate((pos, 0, 0))
                    self.scopes[i].pos_line = self.buffer_counter
                    self.scopes[i].update()
            
            else:
                for i in range(self.amount_scopes):
                    ysl = self._invec(i)
                    self.scopes[i].y[0][self.buffer_counter: self.buffer_counter + 64] = ysl
                    self.scopes[i].program['position'].set_data(self.scopes[i].y)
                            
                self.buffer_counter += 64
                self.zaehler += 1
            
                if self.zaehler % 30 == 0:
                    self.zaehler = 0
                    
                    for i in range(self.amount_scopes):
                        
                        zoom = self.scopes[i].program['zoom_x'][0]
                        versatz = self.scopes[i].program['versatz'][0]
                        drag_x = self.scopes[i].program['drag_x'][0]
                        
                        pos = -1 + float(self.buffer_counter)/self.smpls_all * 2
                        pos += drag_x 
                        pos = pos * zoom + self.scopes[i].program['versatz'][0]
                        
                        self.scopes[i].prg_poslinie['model'] = translate((pos, 0, 0))
                        self.scopes[i].pos_line = self.buffer_counter
                        self.scopes[i].update()
                        
        except:
            print(tb())
            
            



VERT_SHADER = """

// y coordinate of the position.
attribute float position;

// time index.
attribute vec3 index;

// Number of samples per signal.
uniform float all_samples;

// Zoom Position X / Y
uniform float zoom_x;
uniform float zoom_y;

attribute float versatz;
attribute float drag_x;
attribute float drag_y;
attribute float adjust_y;

void main() {
    
    float x = -1 + ( 2 * index.z / (all_samples-1) );
    float y =  position;    
                  
    gl_Position =  ( vec4( x * zoom_x , y * zoom_y * adjust_y , 0.0, 1.0) 
                    + vec4(drag_x * zoom_x , drag_y , 0, 0) 
                    + vec4(versatz, 0, 0, 0)
                    );
}
"""

FRAG_SHADER = """

varying vec4 v_color;
//varying vec3 v_index;

void main() {
    gl_FragColor = vec4 (.8, .45, 0.0, 1.0); 
}
"""


vertex_line = """

uniform mat4 model;
attribute vec3 position;

// Color.
attribute vec4 a_color;
varying vec4 v_color;

void main() {
    gl_Position =  model * vec4(position, .1);
    v_color = vec4(a_color);
}
"""

fragment_line = """
varying vec4 v_color;

void main() {
    gl_FragColor = v_color;
}
"""




class Canvas(app.Canvas):
    
    def __init__(self, smpl_all, xAxis, yAxis, scopes):
        app.Canvas.__init__(self, title='Glyphs', keys='interactive')
        
        try:
            self.smpl_all = smpl_all
            self.xAxis= xAxis
            self.yAxis= yAxis
            self.scopes = scopes
            
            self.last_mouse_position = None
            
            self.anzeigewerte = [b * 10**a for a in reversed(range(6)) for b in (4,2,1)]
            self.sichtbare = [0, smpl_all - 1]
            self.pos_line = 0
            self.pos_markline = 0
            
            
             
            # Generate the signals as a (m, n) array.
            #self.y = np.array(np.linspace(-1, 1, smpl_all - 1),ndmin=2).astype(np.float32)
            self.y = np.array(np.linspace(0, 0, smpl_all - 1),ndmin=2).astype(np.float32)
     
            # Signal 2D index of each vertex (row and col) and x-index (sample index
            # within each signal).
            index = np.c_[np.repeat(0, smpl_all -1),
                          np.repeat(0, smpl_all-1),
                          np.arange(smpl_all-1)].astype(np.float32)
     
             
            self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
            self.program['position'] = self.y#.reshape(-1, 1)
            self.program['index'] = index
            
            self.program['all_samples'] = smpl_all
            
            self.program['versatz'] = 0
            self.program['drag_x'] = 0
            self.program['drag_y'] = 0
            
            self.program['zoom_x'] = 1.
            self.program['zoom_y'] = 1.
            
            self.program['adjust_y'] = 1.
            self.drag_x = 0
            self.drag_y = 0
            self.zoom_y = 1
            
            # X-Achse
            self.xAchse, self.indices0 = self.create_line([-.1, 0], [.1, 0], (.3, .3, .3))
            self.prg_poslinie, self.indices = self.create_line([0, -.1], [0, .1], (0, 1., 0.))
            self.prg_marklinie, self.indices2 = self.create_line([0, -.1], [0, .1], (0, 0., 1.))
                         
            self.setze_xAchse()

        except Exception as e:
            print(tb())
             
        
    def on_mouse_press(self, event):
        self.last_mouse_position = event.pos
        
        if event.button == 3:
            pos = float(event.pos[0]) / self.physical_size[0] 
            self.setze_markierungslinie(pos)
                        
                  
    def on_mouse_move(self, event):
        
        try:
            if event.is_dragging and event.buttons == [1]:

                dx =  event.pos[0] - self.last_mouse_position[0]
                relative_dx = float(dx) / self.physical_size[0] * 2 / self.program['zoom_x'][0]
                self.drag_x += relative_dx
                self.program['drag_x'] = self.drag_x
                
                self.setze_xAchse()
                self.setze_positionslinie()  
                self.setze_markierungslinie()
                
                self.update()
                self.last_mouse_position = event.pos
                
            elif event.is_dragging and event.buttons in( [1,2], [2,1] ):
                
                dy =  event.pos[1] - self.last_mouse_position[1]
                relative_dy = -float(dy) / self.physical_size[1] * 2 / self.program['zoom_y'][0]
                self.drag_y += relative_dy
                self.program['drag_y'] = self.drag_y

                model = translate((0, self.drag_y, 0))
                self.xAchse['model'] = model
                
                self.yAxis.drag_y -= relative_dy / self.program['adjust_y'][0]
                self.yAxis.set_scale_y()
                self.yAxis.update()
                
                self.update()
                self.last_mouse_position = event.pos
                
            elif event.is_dragging and event.buttons == [2]:
                
                dy = event.pos[1] - self.last_mouse_position[1]
                self.zoom_y -= dy / 50.
                self.zoom_y = max(.01, self.zoom_y)
                self.program['zoom_y'] = self.zoom_y
                
                self.yAxis.zoom_y = self.zoom_y
                self.yAxis.set_scale_y()
                self.yAxis.update()

                self.update()
                self.last_mouse_position = event.pos
                
            elif event.is_dragging and event.buttons == [3]:
                pos = float(event.pos[0]) / self.physical_size[0] 
                self.setze_markierungslinie(pos)
                
                self.update()
                self.last_mouse_position = event.pos
                
        except:
            print(tb())


    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        
    def create_line(self, pos1, pos2, color):
         
        try:
            x1, y1 = pos1
            x2, y2 = pos2
             
            V = np.zeros(2, [("position", np.float32, 3)])
            V["position"] = [[ x1, y1, 0], [x2, y2, 0]] 
                     
            vertices = VertexBuffer(V)
            indices = IndexBuffer([0, 1])
             
            program = gloo.Program(vertex_line, fragment_line)
            program.bind(vertices)
            model = translate((0, 0, 0))
            program['model'] = model
            r,g,b = color
            program['a_color'] = (r,g,b, 1)
             
            return program, indices
        except:
            print(tb())
       
 
    def on_mouse_wheel(self, event):
        
        try:
            dx = np.sign(event.delta[1]) * .05
            pos_im_fenster = ( event.pos[0] / float(self.physical_size[0]) )

            self.setze_zoom_x(dx, pos_im_fenster)
            self.setze_xAchse() 
            self.setze_positionslinie()   
            self.setze_markierungslinie()        
            
            self.update()             
                         
        except Exception as e:
            print(tb())
             

    def setze_zoom_x(self, dx, pos_im_fenster):
         
        # Position Wave
        zoom_alt = self.program['zoom_x'][0]
        zoom_neu = max(1.0, zoom_alt * math_exp(2.5 * dx))
         
        anzahl_sichtbare = int(self.smpl_all / zoom_neu  ) 
        anzahl_sichtbare_alt = int(self.smpl_all / zoom_alt  )       
        dif_sichtbare = anzahl_sichtbare_alt - anzahl_sichtbare 
        
        nach_links = int(dif_sichtbare * pos_im_fenster) 
        nach_rechts = dif_sichtbare - nach_links        
        
        if zoom_neu == 1.0:
            self.sichtbare[0] = 0
            self.sichtbare[1] = self.smpl_all - 1
            self.drag_x = 0
            self.drag_y = 0
            self.zoom_y = 1
            self.program['drag_x'] = 0
        else:
            self.sichtbare[0] += nach_links 
            self.sichtbare[1] -= nach_rechts 
        
        eigentliche_pos = -1 - ( -1 + 2.0 / self.smpl_all * self.sichtbare[0] )  * zoom_neu 

        self.program['versatz'] = eigentliche_pos 
        self.program['zoom_x'] = zoom_neu 


    def setze_positionslinie(self):
        
        x0, x1 = self.berechne_anfang_und_ende()
        zoom = self.program['zoom_x']
        versatz = self.program['versatz'][0]
        
        anzahl_sichtbare = int(self.smpl_all / zoom )
        
        if x0 <= self.pos_line <= x1:
            pos = self.pos_line - x0 
            pos_line_new = -1 + 2 * pos / float(anzahl_sichtbare)  
        else:
            # Positionslinie ausblenden
            pos_line_new = -2
         
        self.prg_poslinie['model'] = translate((pos_line_new, 0, 0))  
        
    
    def setze_markierungslinie(self, pos = None):
    
        x0, x1 = self.berechne_anfang_und_ende()
    
        if pos != None:
            dif = x1 - x0
            pos_but = runden(dif * pos) + x0
            self.pos_markline = pos_but
        
        zoom = self.program['zoom_x']
        anzahl_sichtbare = int(self.smpl_all / zoom )
         
        if x0 <= self.pos_markline <= x1:
            pos = self.pos_markline - x0
            pos_line_new = -1 + 2 * pos / float(anzahl_sichtbare)  
        else:
            # Positionslinie ausblenden
            pos_line_new = -2
        
        self.prg_marklinie['model'] = translate((pos_line_new, 0, 0))     
        self.update()
        
          
    def berechne_anfang_und_ende(self):
        
        drag_x = self.program['drag_x']
        zoom = self.program['zoom_x']
        eigentliche_pos = self.program['versatz']
                        
        pos0 = -1. * zoom + drag_x * zoom + eigentliche_pos  
        pos1 = 1. * zoom + drag_x * zoom + eigentliche_pos 
        
        pos0 = pos0[0]
        pos1 = pos1[0]

        laenge = pos1 - pos0
        smpl_laenge = laenge / self.smpl_all 
        
        if pos0 <= -1:
            dif_links = abs(pos0 + 1)
            dif_rechts = pos1 - 1
        elif pos0 > -1:
            dif_links = -( pos0 + 1 )
            dif_rechts = pos1 - 1
            
        stelle_m1 = 100 / laenge * dif_links
        stelle_p1 = 100 - (100 / laenge * dif_rechts)
        x0 = runden(self.smpl_all * stelle_m1 / 100)
        x1 = runden(self.smpl_all * stelle_p1 / 100)
        
        return x0, x1
    
         
    def setze_xAchse(self):

        x0, x1 = self.berechne_anfang_und_ende()
                
        zoom_neu = self.program['zoom_x'][0]
        anzahl = int(self.smpl_all / zoom_neu  )
                 
        for w in self.anzeigewerte:
            teiler = anzahl / w
            if teiler > 2:
                break

        anfang = x0 / w + 1
        reihe = list(range(anfang * w, x1, w))
         
        positions = []
         
        for s in reihe:
            pos = s - x0
            positions.append([s,-1 + 2 * pos / float(anzahl) ])
     
        self.xAxis.positions = positions  
        self.xAxis.update()

    
    def on_draw(self, event):
        
        gloo.clear(color='black')
        gloo.set_viewport(0, 0, *self.physical_size)
                
        try:
            vp = (0, 0, self.physical_size[0], self.physical_size[1])
            self.context.set_viewport(*vp)
            
            self.xAchse.draw('lines', self.indices0)
            self.program.draw('line_strip') #'points'
            self.prg_poslinie.draw('lines', self.indices)
            self.prg_marklinie.draw('lines', self.indices2)

        except Exception as e:
            print(tb())


class XAxis(QtGui.QWidget):
    
    def __init__(self):
        super(XAxis, self).__init__()
        
        self.qp = QtGui.QPainter()
        self.metrics = QtGui.QFontMetrics(QtGui.QFont('Decorative', 10))
        self.setContentsMargins(0, 0, 0, 0)
        self.positions = []
           

    def paintEvent(self, event):

        self.qp.begin(self)
        self.qp.setPen(QtGui.QColor(200,200,200))
        self.qp.setFont(QtGui.QFont('Decorative', 10))
        
        r = event.rect()
        rect_x = r.width()
        
        self.qp.drawLine(0,0,rect_x,0)
        
        for txt,pos in self.positions:
            
            txt = str(txt)
            width = self.metrics.width(txt)
            
            x1 = int( (1 + pos) / 2 * rect_x) 
            x = x1 - int(width/2.)
            
            rect = QtCore.QRect(x,8,width,13)
            
            self.qp.drawText(rect, QtCore.Qt.AlignLeft, txt) 
            self.qp.drawLine(x1,0,x1,5) 
            
        self.qp.end()   
                            
            
class YAxis(QtGui.QWidget):
    
    def __init__(self):
        super(YAxis, self).__init__()

        self.positions = []
        
        self.anzahl_y_Werte = 9
        
        self.max_y = 1
        self.min_y = -1
        
        self.drag_y = 0
        self.zoom_y = 1
        
        self.font_size = 10.
        
        self.qp = QtGui.QPainter()
        self.metrics = QtGui.QFontMetrics(QtGui.QFont('Decorative', self.font_size))
        

    def paintEvent(self, event):

        self.qp.begin(self)
        self.qp.setPen(QtGui.QColor(200,200,200))
        self.qp.setFont(QtGui.QFont('Decorative', 10))
        
        r = event.rect()
        width = r.width()
        height = r.height()
        
        self.qp.drawLine(width - 1, 0, width - 1, height)
        
        for txt,pos in self.positions:
            
            txt = str(txt)

            txt_height = self.metrics.height()
            txt_width = self.metrics.width(txt)
             
            y = int( (1 + -pos) / 2 * height) 
            y1 = y - int(txt_height / 2.)
             
            rect = QtCore.QRect(width - txt_width - 7, y1, txt_width, y1)
            
            self.qp.drawText(rect, QtCore.Qt.AlignLeft, txt) 
            self.qp.drawLine(width - 5, y , width, y) 
            
        self.qp.end()   
    
    
    def set_scale_y(self):

        maxi = (self.max_y + self.drag_y) / self.zoom_y
        mini = (self.min_y + self.drag_y) / self.zoom_y
          
        self.positions, null_pos = berechne_abstaende_y_Achse(maxi, mini)    


def runden(x):
    dif = x - int(x)
    if dif >= .5:
        return int(x) + 1
    else:
        return int(x)


def pr(locs,*args):
    print('')
    for a in args:
        print('{0}: {1}'.format(a,locs[a]))


from decimal import Decimal as D  
def berechne_abstaende_y_Achse(maxi, mini):
    
    laenge = float(maxi - mini)
    vor, nach = str(laenge).split('.')
    
    if laenge == 0:
        return  [[1.,1.], [0., 0.], [-1., -1.]], 0.
    
    if int(vor) != 0:
        dezi = 10**( len(vor) -1)
    else:
        d = 0
        while nach[d] == '0':
            d += 1

        dezi = 1. / 10**(d + 1)
    
    
    anzahl = laenge / dezi
    if anzahl > 9:
        dezi *= 2
        anzahl = laenge / dezi
    
    if anzahl < 2:
        dezi /= 2.
        anzahl = laenge / dezi
    
    groesser0 = []
    kleiner0 = []
    positionen = []
    
    x = 1
    while dezi * x < maxi:
        v = D(str(dezi)) * D(str(x))
        groesser0.append(v)
        x += 1
    
    x = 1
    while dezi * -x > mini:
        v = D(str(dezi)) * D(str(-x))
        kleiner0.append(v)
        x += 1
    
    reihe = list(reversed(groesser0)) + [0] + kleiner0
    
    for r in reihe:
        rel_pos = - 1 + 2. / laenge * (float(r) - mini)
        positionen.append([r, rel_pos])
        if r == 0:
            null_pos = rel_pos 
      
    return positionen, null_pos
        



