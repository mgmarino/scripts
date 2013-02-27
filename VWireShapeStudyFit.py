import ROOT,sys
from array import array

class Fitter:
  def __init__(self):
    transfer = ROOT.EXOTransferFunction()
    transfer.AddDiffStageWithTime(10000.0)
    transfer.AddDiffStageWithTime(10000.0)
    transfer.AddDiffStageWithTime(60000.0)
    transfer.AddIntegStageWithTime(3000.0)
    transfer.AddIntegStageWithTime(3000.0)
    builder = ROOT.EXOVWireSignalModelBuilder(transfer,0.00171,2.25*ROOT.CLHEP.mm/ROOT.CLHEP.microsecond,0.0)
    self.channel = 40
    self.model = ROOT.EXOSignalModel()
    builder.InitializeSignalModelIfNeeded(self.model,self.channel)
    self.fitter = ROOT.EXOSignalFitterChiSquare()
    truearray = 80*'a'
    falseWF = ROOT.EXOBoolWaveform()
    falseWF.SetLength(256-40)
    falseWF.SetSamplingFreq(0.001)
    falseWF.SetTOffset(0.0)
    falseWF.Zero()
    trueWF = ROOT.EXOBoolWaveform(truearray,80)
    trueWF.SetSamplingFreq(0.001)
    trueWF.SetTOffset(0.0)
    self.Include = ROOT.EXOBoolWaveform()
    self.Include.SetLength(256-40)
    self.Include.SetSamplingFreq(0.001)
    self.Include.SetTOffset(0.0)
    self.Include.Zero()
    self.Include.Append(trueWF)
    self.Include.Append(falseWF)
    self.t_min = self.Include.GetTimeAtIndex(256-40) - 1
    self.t_max = self.Include.GetTimeAtIndex(256+40)

  def doFit(self,wf):
    self.fitter.Reset()
    doubleWF = wf.Convert()
    exoWF = ROOT.EXOWaveform(wf.GetData(),wf.GetLength())
    exoWF.SetSamplingFreq(0.001)
    exoWF.SetTOffset(0.0)
    exoWF.fChannel = self.channel
    noiseCalc = ROOT.EXOBaselineAndNoiseCalculator()
    map = noiseCalc.ExtractAll(doubleWF)
    noise = map["Noisecounts"]
    baseline = map["Baseline"]
    sig = ROOT.EXOSignal()
    sig.fMagnitude = exoWF[256] - exoWF[0]
    sig.fTime = exoWF.GetTimeAtIndex(256)
    sigs = ROOT.EXOChannelSignals()
    sigs.SetChannel(self.channel)
    sigs.AddSignal(sig)
    sigs.SetWaveform(exoWF)
    self.fitter.AddSignalsWithFitModel(sigs,self.model,ROOT.EXOVWireFitRanges(self.t_min,self.t_max),self.Include,noise,baseline)
    self.fitter.Minimize()
    return self.fitter.GetMinimizer().MinValue(), self.fitter.GetFitChannelSignalsAt(0)

def main(file):
  #ROOT.gROOT.SetBatch(True)
  ROOT.gSystem.Load("libEXOUtilities")
  ROOT.gSystem.Load("libEXOReconstruction")
  fitter = Fitter()
  f = ROOT.TFile(file)
  x = []
  y = []
  c1 = ROOT.TCanvas("c1")
  #c1.Print("Fits.pdf[")
  for i in range(-199,199):
    wf = f.Get("WF_Z_"+str(i))
    chi2,chansig = fitter.doFit(wf)
    plots = ROOT.TList()
    fitter.fitter.GetHistPlotOfResults(plots)
    aplot = plots.At(0)
    aplot.SetTitle("Z = "+str(i))
    #aplot.Draw()
    #c1.Update()
    #c1.Print("Fits.pdf")
    x.append(i)
    y.append(chi2)
  #c1.Print("Fits.pdf]")
  size = len(x)
  x = array('d',x)
  y = array('d',y)
  graph = ROOT.TGraph(size,x,y)
  graph.SetMarkerStyle(20)
  graph.Draw("AP")
  raw_input("hit enter to quit")
  c1.Print("Chi2.pdf")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" file")
    sys.exit(1)
  main(sys.argv[1])
