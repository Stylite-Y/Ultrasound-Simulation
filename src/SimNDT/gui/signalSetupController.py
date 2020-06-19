__author__ = 'Miguel Molero'

import numpy as np

from PySide.QtCore import *
from PySide.QtGui import *

from SimNDT.gui.ui_signalsetup import Ui_SignalSetupWidget
from SimNDT.gui.Warnings import WarningParms

import SimNDT.core.constants as c
from SimNDT.graphics.mplWidget import MplCanvas
from SimNDT.core.signal import Signals, RaisedCosinePulse, PulseUTsin


class SignalSetupWidget(QWidget, Ui_SignalSetupWidget):
    def __init__(self, parent=None):
        super(SignalSetupWidget, self).__init__(parent)
        self.setupUi(self)


class SignalSetup(QDialog):
    def __init__(self, Signal=None, parent=None):
        super(SignalSetup, self).__init__(parent)

        self.widget = SignalSetupWidget()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)

        self.widget.previewPushButton.pressed.connect(self.preview)
        self.widget.typeComboBox.currentIndexChanged.connect(self.handleTypeSignal)
        self.widget.cyclesLabel.setVisible(False)
        self.widget.cyclesDoubleSpinBox.setVisible(False)

        self.mpl = MplCanvas(width=2, height=2, dpi=100)
        self.mpl.ax.axis("off")

        w = QWidget(self)
        h = QVBoxLayout()
        h.addWidget(self.mpl)
        w.setLayout(h)

        hBox = QHBoxLayout()
        hBox.addWidget(w)
        hBox.addWidget(self.widget)

        vBox = QVBoxLayout()
        vBox.addLayout(hBox)
        vBox.addWidget(self.buttonBox)

        self.setLayout(vBox)
        # On Top
        self.setWindowFlags((self.windowFlags() | Qt.WindowStaysOnTopHint) & ~(Qt.WindowContextHelpButtonHint))
        self.setWindowTitle(self.tr("Signal Parameters Setup"))
        self.setWindowIcon(QIcon(":/signal.png"))

        self.setFixedSize(600, 300)

        self.Signal = None

        if Signal is not None:

            self.widget.amplitudeLineEdit.setText(str(Signal.Amplitude))
            self.widget.frequencyLineEdit.setText(str(Signal.Frequency * 1e-6))
            self.widget.timeLineEdit.setText(str(Signal.time * 1e6))
            print(" real time ", Signal.time)
            # print(Signal.Amplitude)
            print(" real freq ", Signal.Frequency)
            # print(type(Signal.Frequency))

            if Signal.Name == "RaisedCosine":
                self.widget.typeComboBox.setCurrentIndex(c.SignalType.RaisedCosinePulse)
            elif Signal.Name == "GaussianSine":
                self.widget.typeComboBox.setCurrentIndex(c.SignalType.GaussianSinePulse)
                self.widget.cyclesLabel.setVisible(True)
                self.widget.cyclesDoubleSpinBox.setVisible(True)
                self.widget.cyclesDoubleSpinBox.setValue(Signal.N_Cycles)

            t = self.generate(Signal.time)
            # print(t)
            sig = Signal.generate(t)
            self.mpl.ax.plot(sig)
            self.mpl.ax.axis("off")
            self.mpl.ax.hold(False)
            self.mpl.draw()

    def generate(self, time):
        TMin = 1e-6 / 60.0
        Number = time / TMin
        #print(time)
        #print(type(time))
        t = np.linspace(0.0, time, Number)
        print("the number of t ",t.shape)
        return t

    def preview(self):

        type = self.widget.typeComboBox.currentIndex()

        if self.getValues(type):
            self.mpl.ax.plot(np.zeros((10, 1)))
            self.mpl.ax.axis("off")
            self.mpl.ax.hold(False)
            self.mpl.draw()

            return

        t = self.generate(self.Signal.time)
        #print("preview time ", self.Signal.time)
        #print("preview t ", t.shape)
        sig = self.Signal.generate(t)

        self.mpl.ax.plot(sig)
        self.mpl.ax.axis("off")
        self.mpl.draw()

    def accept(self):

        type = self.widget.typeComboBox.currentIndex()

        try:
            if self.getValues(type):
                return
        except:
            return

        QDialog.accept(self)

    def handleTypeSignal(self, index):

        if index == c.SignalType.GaussianSinePulse:
            self.widget.cyclesLabel.setVisible(True)
            self.widget.cyclesDoubleSpinBox.setVisible(True)
        else:
            self.widget.cyclesLabel.setVisible(False)
            self.widget.cyclesDoubleSpinBox.setVisible(False)

    def getValues(self, type):

        try:
            amplitude = float(self.widget.amplitudeLineEdit.text())
            #print("ori amp is ", amplitude)
        except:
            msgBox = WarningParms("Give correctly the Amplitude")
            if msgBox.exec_():
                return True

        try:
            time = float(self.widget.timeLineEdit.text()) * 1e-6
            #print("ori time is ", time)
        except:
            msgBox = WarningParms("Give correctly the time")
            if msgBox.exec_():
                return True

        try:
            frequency = float(self.widget.frequencyLineEdit.text()) * 1e6
            #print("ori freq is ", frequency)
            #print("ori freq is ", frequency)
            if frequency > 1e9:
                msgBox = WarningParms("Give correctly the Frequency (MHz)")
                if msgBox.exec_():
                    return True


        except:
            msgBox = WarningParms("Give correctly the Frequency (MHz)")
            if msgBox.exec_():
                return True

        if type == c.SignalType.RaisedCosinePulse:
            self.Signal = Signals("RaisedCosine", time, amplitude, frequency)
            cycles = 1


        elif type == c.SignalType.GaussianSinePulse:
            try:
                cycles = float(self.widget.cyclesDoubleSpinBox.value())
                if cycles == 0:
                    msgBox = WarningParms("Give correctly the # Cycles")
                    if msgBox.exec_():
                        return True

            except:
                msgBox = WarningParms("Give correctly the # Cycles")
                self.widget.cyclesDoubleSpinBox.setValue(0)
                if msgBox.exec_():
                    return True

            try:
                self.Signal = Signals("GaussianSine", time, amplitude, frequency, cycles)
                t = self.generate(self.Signal.time)
                sig = self.Signal.generate(t)

            except:
                msgBox = WarningParms("Give lower # Cycles")
                self.widget.cyclesDoubleSpinBox.setValue(0)
                if msgBox.exec_():
                    return True
