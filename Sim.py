import typing
from PyQt5 import QtCore
import matplotlib
matplotlib.use('QTAgg')
import numpy as np


from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QDoubleSpinBox, QTabWidget, QWidget, QGridLayout, QSlider, QLCDNumber, QGroupBox, QLabel, QPushButton,QHBoxLayout, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys

class HTMLDialog(QDialog):
    def __init__(self, parent = None) :
        super().__init__(parent)
        self.files = []
        self.htmlAsString()

        layout = QVBoxLayout()
        

        self.html = QWebEngineView()
        
        layout.addWidget(self.html)

        self.setLayout(layout)
        self.setWindowTitle("Snell's Law")
        self.setFixedSize(700,850)

    def htmlAsString(self):
        
        with open('SnellLaw.html') as file:
            self.text = file.read()
            self.files.append(self.text)

        with open('ReflectionLaw.html') as file:
            self.text = file.read()
            self.files.append(self.text)

    def changeText(self, lawType):
        self.html.setHtml(self.files[lawType])

class MplCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 4, height = 5, dpi = 100, xlim = [1,2], ylim = [1,2]):
        fig = Figure(figsize= (width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlim(xlim[0], xlim[1])
        self.axes.set_ylim(ylim[0], ylim[1])
        self.axes.tick_params(left = False, right = False , labelleft = False , 
                labelbottom = False, bottom = False) 
        self.axes.set_facecolor("#A2A9B0")
        fig.set_facecolor("#A2A9B0")
        super(MplCanvas, self).__init__(fig)

class MirrorTab(QWidget):

    def __init__(self, dialog):
        super().__init__()
        #self.setStyleSheet("background-color:#1E286B;")
        
        self.dialog = dialog
        self.objectPosition = 0
        self.diameter = 60
        self.radius = 180

        layout = QGridLayout()

        controlPanel = QGroupBox()
        controlPanelLayout =  QGridLayout()

        ######################################################################
        incidentAngleLabel = QLabel("Object Position:")
        incidentAngleLabel.setFont(QFont("Helvetica", 13))
        incidentAngleLabel.setStyleSheet("color : black; border: none;")
        incidentAngleLabel.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.incidentAngleSlider = QSlider(Qt.Orientation.Horizontal)
        self.incidentAngleSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.incidentAngleSlider.setRange(0,25)
        self.incidentAngleSlider.setValue(0)
        self.incidentAngleSlider.setSingleStep(1)
        self.incidentAngleSlider.valueChanged.connect(self.updateObjectPos)
        self.incidentAngleSlider.setStyleSheet("background-color: white;")

        self.incidentAngleLCD = QLCDNumber()
        self.incidentAngleLCD.setStyleSheet("background-color: white;")
    
        ######################################################################

        diameterLabel = QLabel("Diameter: ")
        diameterLabel.setStyleSheet("color : black; border: none;")
        diameterLabel.setFont(QFont("Helvetica", 13))

        self.diameterSlider = QSlider(Qt.Orientation.Horizontal)
        self.diameterSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.diameterSlider.setStyleSheet("background-color: white;")
        self.diameterSlider.setRange(60,120)
        self.diameterSlider.setSingleStep(1)
        self.diameterSlider.setValue(60)
        self.diameterSlider.valueChanged.connect(self.updateDiameter)
    
        ######################################################################
        
        controlPanelLayout.addWidget(incidentAngleLabel, 0,0)
        controlPanelLayout.addWidget(self.incidentAngleLCD, 1,0)
        controlPanelLayout.addWidget(self.incidentAngleSlider, 1,1)
        controlPanelLayout.addWidget(diameterLabel, 2,0)
        controlPanelLayout.addWidget(self.diameterSlider, 2,1)
        """
        controlPanelLayout.addWidget(LearnMoreLabel,6,0)
        controlPanelLayout.addWidget(snellsLawInfo, 7,0)
        controlPanelLayout.addWidget(reflectionLawInfo, 7,1)
        """
        controlPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controlPanelLayout.setVerticalSpacing(15)
        controlPanel.setLayout(controlPanelLayout)
        controlPanel.setTitle("Control Panel")
        controlPanel.setStyleSheet("background-color: #C7C7C7; border: 3px solid; border-color:#000000; font-weight:bold; subcontrol-origin: margin;subcontrol-position: top left;padding: 0 3px;")
         
       ######################################################################


        plotPanel = QGroupBox()
        plotPanelLayout= QGridLayout()
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100, xlim= [-1,60], ylim= [-10,10])
        self.canvas.axes.set_facecolor("white")
        plotPanelLayout.addWidget(self.canvas, 0,0)
        plotPanel.setLayout(plotPanelLayout)
        plotPanel.setTitle("Plot")
        plotPanel.setStyleSheet("background-color:#A2A9B0; border: 3px solid; border-color:#000000; font-weight:bold; subcontrol-origin: margin;subcontrol-position: top left;padding: 0 3px;")
        #plotPanel.setFixedHeight(500)
        
        self.startUpPlot()
        ######################################################################
        layout.addWidget(plotPanel,0,0 )
        layout.addWidget(controlPanel,0,1)
        self.setLayout(layout)

    def startUpPlot(self):
        self.updatePlot()

    def updateObjectPos(self, val):
        self.objectPosition = val
        self.updatePlot()
        self.incidentAngleLCD.display(val)
        
    def updateDiameter(self, val):
        self.diameter = val
        self.updatePlot()

    def updateRefIndex(self, val):
        self.refractedIndex = val
        self.updatePlot()

    def updatePlot(self):
        # Drop off the first y element, append a new one.
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.set_xlim(-10, 80)
        self.canvas.axes.set_ylim(-10, 10)
       
        self.canvas.axes.plot([35,35],[self.diameter/20, self.diameter/-20], "k-", linewidth =2, label = "Mirror")
        
        self.canvas.axes.plot([self.objectPosition, 35],[7, self.diameter/20], "b-")
        self.canvas.axes.plot([self.objectPosition, 35],[7, 0], "b-")
        self.canvas.axes.plot([self.objectPosition, 35],[7, self.diameter/-20], "b-")

        self.canvas.axes.plot([35, self.objectPosition],[self.diameter/20, (self.diameter/20) -(7-self.diameter/20) ], "b-")
        self.canvas.axes.plot([35, self.objectPosition],[0, -7],"b-")
        self.canvas.axes.plot([35, self.objectPosition],[self.diameter/-20, (self.diameter/-20) -(7-self.diameter/-20) ],"b-")
        
        
        self.canvas.axes.plot([35, 35+(35-self.objectPosition)],[self.diameter/20, 7], "r--")
        self.canvas.axes.plot([35, 35 +(35-self.objectPosition)],[0,7], "r--")
        self.canvas.axes.plot([35, 35 +(35-self.objectPosition)],[self.diameter/-20, 7], "r--")
        self.canvas.axes.plot(self.objectPosition, 7, 'ob', label = "Object")

        self.canvas.axes.plot(35 +(35-self.objectPosition), 7, 'or', label ="Image")
        self.canvas.axes.legend()
        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    def showSnellsLaw(self):
        self.dialog.changeText(0)
        self.dialog.exec_()

class RRTab(QWidget):

    def __init__(self, dialog):
        super().__init__()
        
        self.dialog = dialog
        self.incidentAngle = 45
        self.incidentIndex = 1
        self.refractedIndex = 1.5
        self.refractedAngle = 0

        layout = QGridLayout()

        controlPanel = QGroupBox()
        controlPanelLayout =  QGridLayout()

        ######################################################################
        incidentAngleLabel = QLabel("Incident Angle:")
        incidentAngleLabel.setFont(QFont("Helvetica", 13))
        incidentAngleLabel.setStyleSheet("color : black; border: none;")
        incidentAngleLabel.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.incidentAngleSlider = QSlider(Qt.Orientation.Horizontal)
        self.incidentAngleSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.incidentAngleSlider.setRange(0,90)
        self.incidentAngleSlider.setValue(45)
        self.incidentAngleSlider.setSingleStep(1)
        self.incidentAngleSlider.valueChanged.connect(self.updateIncAngle)
        self.incidentAngleSlider.setStyleSheet("background-color: white;")

        

        self.incidentAngleLCD = QLCDNumber()
        self.incidentAngleLCD.setStyleSheet("background-color: white;")
    
        ######################################################################
        incidentIndexLabel = QLabel("Incident Index: ")
        incidentIndexLabel.setFont(QFont("Helvetica", 13))
        incidentIndexLabel.setStyleSheet("color : black; border: none;")


        self.incidentIndexSlider = QDoubleSpinBox()
        self.incidentIndexSlider.setRange(1,1.5)
        self.incidentIndexSlider.setSingleStep(.1)
        self.incidentIndexSlider.setValue(1)
        self.incidentIndexSlider.valueChanged.connect(self.updateIncIndex)


        ######################################################################
        refractedIndexLabel = QLabel("Refracted Index: ")
        refractedIndexLabel.setStyleSheet("color : black; border: none;")
        refractedIndexLabel.setFont(QFont("Helvetica", 13))

        self.refractedIndexSlider = QDoubleSpinBox()
        self.refractedIndexSlider.setRange(1.6,3)
        self.refractedIndexSlider.setSingleStep(.1)
        self.refractedIndexSlider.setValue(1.5)
        self.refractedIndexSlider.valueChanged.connect(self.updateRefIndex)
    
        ######################################################################
        refractedAngleLabel = QLabel("Refracted Angle: ")
        refractedAngleLabel.setStyleSheet("color : black; border: none;")
        refractedAngleLabel.setFont(QFont("Helvetica", 13))

        reflectedAngleLabel = QLabel("Reflected Angle: ")
        reflectedAngleLabel.setStyleSheet("color : black; border: none;")
        reflectedAngleLabel.setFont(QFont("Helvetica", 13))
        
        self.refractedAngleLCD = QLCDNumber()
        self.refractedAngleLCD.setFixedHeight(50)
        self.refractedAngleLCD.setFixedWidth(155)
        self.reflectedAngleLCD = QLCDNumber()
        self.reflectedAngleLCD.setFixedHeight(50)
        
        self.refractedAngleLCD.setStyleSheet("background-color: white;")
        self.reflectedAngleLCD.setStyleSheet("background-color: white;")
        
        ######################################################################
        LearnMoreLabel = QLabel("Learn More:")
        LearnMoreLabel.setFont(QFont("Helvetica", 13))
        LearnMoreLabel.setStyleSheet("color : black; border: none;")
        LearnMoreLabel.setAlignment(Qt.AlignmentFlag.AlignBottom)

        snellsLawInfo = QPushButton(text= "Snell's Law")
        snellsLawInfo.setFixedHeight(50)
        snellsLawInfo.setStyleSheet("QPushButton {background-color: white; border: 2px solid;} QPushButton:hover {background-color: #DBD9D9;}")
        snellsLawInfo.pressed.connect(self.showSnellsLaw)
        
        reflectionLawInfo = QPushButton(text= "Law of Reflection")
        reflectionLawInfo.setFixedHeight(50)
        reflectionLawInfo.setStyleSheet("QPushButton {background-color: white; border: 2px solid;} QPushButton:hover {background-color: #DBD9D9;}")
        reflectionLawInfo.pressed.connect(self.showReflectionLaw)

        ######################################################################
        
        controlPanelLayout.addWidget(incidentAngleLabel, 0,0)
        controlPanelLayout.addWidget(self.incidentAngleLCD, 1,0)
        controlPanelLayout.addWidget(self.incidentAngleSlider, 1,1)
        controlPanelLayout.addWidget(incidentIndexLabel, 2,0)
        controlPanelLayout.addWidget(self.incidentIndexSlider, 2,1)
        controlPanelLayout.addWidget(refractedIndexLabel, 3,0)
        controlPanelLayout.addWidget(self.refractedIndexSlider, 3,1)
        controlPanelLayout.addWidget(refractedAngleLabel, 4,0)
        controlPanelLayout.addWidget(self.refractedAngleLCD, 4,1)
        controlPanelLayout.addWidget(reflectedAngleLabel, 5,0)
        controlPanelLayout.addWidget(self.reflectedAngleLCD, 5,1)
        controlPanelLayout.addWidget(LearnMoreLabel,6,0)
        controlPanelLayout.addWidget(snellsLawInfo, 7,0)
        controlPanelLayout.addWidget(reflectionLawInfo, 7,1)

        controlPanelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controlPanelLayout.setVerticalSpacing(15)
        controlPanel.setLayout(controlPanelLayout)
        controlPanel.setTitle("Control Panel")
        controlPanel.setStyleSheet("background-color: #C7C7C7; border: 3px solid; border-color:#000000; font-weight:bold; subcontrol-origin: margin;subcontrol-position: top left;padding: 0 3px;")
         
       ######################################################################

        plotPanel = QGroupBox()
        plotPanelLayout= QGridLayout()
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100, xlim= [-1,2], ylim= [-1,1])
        plotPanelLayout.addWidget(self.canvas, 0,0)
        plotPanel.setLayout(plotPanelLayout)
        plotPanel.setTitle("Plot")
        plotPanel.setStyleSheet("background-color:#A2A9B0; border: 3px solid; border-color:#000000; font-weight:bold; subcontrol-origin: margin;subcontrol-position: top left;padding: 0 3px;")
        
        self.startUpPlot()
        ######################################################################

        layout.addWidget(plotPanel,0,0 )
        layout.addWidget(controlPanel,0,1)
        self.setLayout(layout)

    def startUpPlot(self):
        self.updateIncAngle(self.incidentAngle)

    def updateIncAngle(self, val):
        self.incidentAngle = val
        self.calcRefractionAngle()
        self.updatePlot()
        self.incidentAngleLCD.display(val)
        self.reflectedAngleLCD.display(val)
        
    def updateIncIndex(self, val):
        self.incidentIndex = val
        self.calcRefractionAngle()
        self.updatePlot()

    def updateRefIndex(self, val):
        self.refractedIndex = val
        self.calcRefractionAngle()
        self.updatePlot()

    def updatePlot(self):
        # Drop off the first y element, append a new one.
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.set_xlim(-1, 1)
        self.canvas.axes.set_ylim(-1, 1)
        
       
        self.canvas.axes.plot([0, -1 * np.cos(np.radians(self.incidentAngle))],
            [0, np.sin(np.radians(self.incidentAngle))],
            'r-', label='Incident Ray'
        )
        self.canvas.axes.plot([0, np.cos(np.radians(self.incidentAngle))],
            [0, np.sin(np.radians(self.incidentAngle))],
            'b-', label='Reflected Ray'
        )
        self.canvas.axes.plot([0, np.cos(np.radians(self.refractedAngle))],
            [0, -1 * np.sin(np.radians(self.refractedAngle))],
            'g-', label='Refracted Ray'
        )
        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    def calcRefractionAngle(self):
        theta1 = np.radians(self.incidentAngle)
        theta2 = np.arcsin(self.incidentIndex / self.refractedIndex * np.sin(theta1))
        self.refractedAngle = 90 - np.degrees(theta2)

        self.refractedAngleLCD.display(self.refractedAngle)

    def showSnellsLaw(self):
        self.dialog.changeText(0)
        self.dialog.exec_()

    def showReflectionLaw(self):
        self.dialog.changeText(1)
        self.dialog.exec_()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optics Sim")
        #self.setFixedSize(800,500)
        tabs = QTabWidget()
        dialog = HTMLDialog(self)
        rrTab = RRTab(dialog)
        mirrorTab = MirrorTab(dialog)
        tabs.addTab(rrTab, "Law of Reflection/Refraction")
        tabs.addTab(mirrorTab, "Mirror Sim")

        self.setCentralWidget(tabs)
        

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    


main()