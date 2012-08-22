import ROOT,sys,random,os
from PyQt4 import QtGui, QtCore
libpath = os.path.abspath('common')
sys.path.append(libpath)
from Pixelater import Pixelater

def gui():
  ROOT.gSystem.Load("libEXOROOT")
  app = QtGui.QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec_())

def cmdline():
  #ROOT.gSystem.Load("libEXOROOT")
  app = QtGui.QApplication(sys.argv)
  sys.exit(app.exec_())

class Digitization(QtCore.QThread):

  eventProcessed = QtCore.pyqtSignal(int)
  neventsChanged = QtCore.pyqtSignal(int)
  nsignalsChanged = QtCore.pyqtSignal(int)
    
  def __init__(self):
    super(Digitization,self).__init__()

    self.nevents = 100
    self.nsignals = 1
    self.abort = False
    self.noiseFilename = ""
    self.useRealNoise = False

    self.pixel = Pixelater()

    self.digimodule = ROOT.EXODigitizeModule()
    self.digimodule.SetAPDNoise(2000.0)
    self.digimodule.SetWireNoise(800.0)
    self.digimodule.SetUnixTimeOfEvent(1333749913)
    self.digimodule.SetDigitizationTime(2048)

    self.toutmodule = ROOT.EXOTreeOutputModule()
    self.toutmodule.SetWriteSignals(True)
    self.toutmodule.SetOutputFilename("digitized.root")
    self.toutmodule.SetWriteMCCharge(True)
    self.toutmodule.SetMaxFileSize(50)

  def abortRun(self):
    self.abort = True

  def setNevents(self,nevents):
    self.nevents = nevents
    self.neventsChanged.emit(nevents)

  def setNsignals(self,nsignals):
    self.nsignals = nsignals
    self.nsignalsChanged.emit(nsignals)

  def setFilename(self,filename):
    self.toutmodule.SetOutputFilename(str(filename))

  def setNoiseFilename(self,filename):
    self.noiseFilename = filename

  def setUseRealNoise(self, value):
    self.useRealNoise = value
    if value:
      self.digimodule.SetWireNoise(0)
    else:
      self.digimodule.SetWireNoise(800.)

  def run(self):
    self.digimodule.Initialize()
    self.toutmodule.Initialize()

    min_energy,max_energy = 0.,4000.
    meantime = 1024*1000
    maxtimediff = 200*1000
    min_z,max_z = -160., 160.
    max_r = 160.

    traceFile = ROOT.TFile()
    traceTree = ROOT.TTree()
    ntraces = 0
    waveforms = []
    if(self.useRealNoise):
      traceFile = ROOT.TFile(str(self.noiseFilename))
      traceFile.ls()
      traceTree = traceFile.Get("TraceTree")
      ntraces = traceTree.GetEntries()
      for i in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE):
        waveforms.append(ROOT.EXODoubleWaveform())
        traceTree.SetBranchAddress("ch"+str(i),waveforms[i])

    for i in range(self.nevents):
      if(self.useRealNoise):
        traceTree.GetEntry(i%ntraces)
      self.eventProcessed.emit(i+1)
      for j in range(self.nsignals):
        energy = random.uniform(min_energy,max_energy)
        time = meantime + random.uniform(-maxtimediff,maxtimediff)
        x = max_r
        y = max_r
        while x**2 + y**2 > max_r**2:
          x = random.uniform(0.,max_r)
          y = random.uniform(0.,max_r)
        z = random.uniform(min_z,max_z)
        for gang in range(2*ROOT.NUMBER_APD_CHANNELS_PER_PLANE):
          self.pixel.AddAPDHit(gang,time,energy)
        self.pixel.AddPCD(x,y,z,time,energy)

      ED = self.pixel.GetEventData()
      if i==0:
        self.digimodule.BeginOfRun(ED)
        self.toutmodule.BeginOfRun(ED)
      self.digimodule.ProcessEvent(ED)
      wfd = ED.GetWaveformData()
      wfd.Decompress()
      if self.useRealNoise:
        for j in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE):
          wf = wfd.GetWaveformWithChannel(j).Convert()
          #wf -= wf[0] #subtract baseline
          wf += waveforms[j]
          intwaveform = wf.Convert()
          wf = wfd.GetWaveformWithChannelToEdit(j)
          wf.Zero()
          wf += intwaveform
      self.toutmodule.ProcessEvent(ED)
      if i==self.nevents-1 or self.abort:
        self.digimodule.EndOfRun(ED)
        self.toutmodule.EndOfRun(ED)
        self.digimodule.ShutDown()
        self.toutmodule.ShutDown()
        break

class MainWindow(QtGui.QWidget):
  def __init__(self):
    super(MainWindow,self).__init__()
    self.runButton = QtGui.QPushButton('start run',self)
    self.runButton.clicked.connect(self.doAction)
    self.fileWidget = FileWidget("Output file:",self)
    self.fileWidget.move(0,100)
    self.neventsWidget = NumberWidget("# events",self)
    self.neventsWidget.move(0,30)
    self.nsignalsWidget = NumberWidget("# signals",self)
    self.nsignalsWidget.setNumber(1)
    self.nsignalsWidget.move(120,30)
    self.noiseCheckbox = QtGui.QCheckBox("use real noise",self)
    self.noiseCheckbox.move(240,50)
    self.noiseFileWidget = FileWidget("Noise trace file:",self)
    self.noiseFileWidget.move(0,150)
    self.dig = Digitization()
    self.progress = ProgressWidget(self)
    self.progress.setGeometry(0,250,400,25)

    self.dig.neventsChanged.connect(self.progress.bar.setMaximum)
    self.dig.eventProcessed.connect(self.progress.bar.setValue)
    self.dig.finished.connect(self.progress.disable)
    self.dig.setNevents(self.neventsWidget.getNumber())
    self.dig.setNsignals(self.nsignalsWidget.getNumber())
    self.dig.setFilename(self.fileWidget.getFilename())

    self.progress.bar.setMinimum(0)
    self.progress.bar.setMaximum(self.dig.nevents)
    self.progress.button.clicked.connect(self.dig.abortRun)

    self.fileWidget.fileChanged.connect(self.dig.setFilename)
    self.noiseFileWidget.fileChanged.connect(self.dig.setNoiseFilename)
    self.neventsWidget.numberChanged.connect(self.dig.setNevents)
    self.nsignalsWidget.numberChanged.connect(self.dig.setNsignals)
    self.noiseCheckbox.stateChanged.connect(self.dig.setUseRealNoise)

    self.setGeometry(400,400,400,300)
    self.show()
    self.progress.hide()

  def doAction(self):
    self.progress.show()
    self.dig.start()

class ProgressWidget(QtGui.QWidget):
  def __init__(self,parent):
    super(ProgressWidget,self).__init__(parent)
    self.setGeometry(0,0,400,25)
    self.bar = QtGui.QProgressBar(self)
    self.button = QtGui.QPushButton('abort',self)
    self.bar.setGeometry(0,0,350,25)
    self.button.setGeometry(355,0,40,25)

  def disable(self):
    self.setDisabled(True)

class FileWidget(QtGui.QWidget):

  fileChanged = QtCore.pyqtSignal(str)
  
  def __init__(self,label,parent):
    super(FileWidget,self).__init__(parent)
    self.setGeometry(0,0,400,50)
    self.label = QtGui.QLabel(label,self)
    self.label.setMaximumHeight(25)
    self.fileEdit = QtGui.QLineEdit(self)
    self.fileEdit.setGeometry(0,25,350,25)
    self.fileEdit.editingFinished.connect(self.editingFinished)

    self.dialogButton = QtGui.QPushButton('open',self)
    self.dialogButton.setGeometry(355,25,40,25)
    self.dialogButton.clicked.connect(self.showDialog)

  def showDialog(self):
    fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',"digitized.root")
    self.fileEdit.setText(fname)
    self.fileChanged.emit(fname)

  def editingFinished(self):
    fname = self.fileEdit.text()
    self.fileChanged.emit(fname)

  def getFilename(self):
    return self.fileEdit.text()

class NumberWidget(QtGui.QWidget):

  numberChanged = QtCore.pyqtSignal(int)

  def __init__(self,label,parent):
    super(NumberWidget,self).__init__(parent)
    self.numberEdit = QtGui.QSpinBox(self)
    self.numberEdit.setMaximum(10000000)
    self.numberEdit.setValue(1000)
    self.numberEdit.setGeometry(0,0,80,25)
    self.numberEdit.valueChanged.connect(self.valueChanged)
    self.numberEdit.move(0,25)

    self.label = QtGui.QLabel(label,self)
    self.label.setGeometry(0,0,80,25)

  def valueChanged(self,number):
    self.numberChanged.emit(number)

  def getNumber(self):
    return self.numberEdit.value()

  def setNumber(self,number):
    self.numberEdit.setValue(number)

if __name__ == "__main__":
  gui()
