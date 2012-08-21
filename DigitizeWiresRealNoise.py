import ROOT,sys,random,math
from array import array

def main(filename):
  ROOT.gSystem.Load("libEXOROOT")
  nevents = 20000
  maxmagnitude = 15000
  traceFile = ROOT.TFile(filename)
  traceTree = traceFile.Get("TraceTree")
  ntraces = traceTree.GetEntries()
  waveforms = []
  for i in range(ROOT.NCHANNELS_PER_WIREPLANE*ROOT.NWIREPLANES):
    waveforms.append(ROOT.EXODoubleWaveform())
    traceTree.SetBranchAddress("ch"+str(i),waveforms[i])

  pixel = Pixelater()

  digimodule = ROOT.EXODigitizeModule()
  digimodule.SetAPDNoise(0.0)
  digimodule.SetWireNoise(0.0)
  digimodule.SetUnixTimeOfEvent(1333749913)
  digimodule.SetDigitizationTime(2048)

  toutmodule = ROOT.EXOTreeOutputModule()
  toutmodule.SetWriteSignals(True)
  toutmodule.SetOutputFilename("digitizedWires-realnoise.root")
  toutmodule.SetWriteMCCharge(True)
  toutmodule.SetMaxFileSize(50)

  digimodule.Initialize()
  toutmodule.Initialize()

  highBandwidthWF = ROOT.EXODoubleWaveform()
  highBandwidthWF.SetLength(2048*ROOT.BANDWIDTH_FACTOR)
  highBandwidthWF.SetSamplingPeriod(ROOT.SAMPLE_TIME_HIGH_BANDWIDTH)
  highBandwidthWF.Zero()
  for i in range(1024*ROOT.BANDWIDTH_FACTOR,2048*ROOT.BANDWIDTH_FACTOR):
    highBandwidthWF[i] = 1.0

  northenergyhist = ROOT.TH1D("northenergyhist","northenergyhist",100,0,20000)
  southenergyhist = ROOT.TH1D("southenergyhist","southenergyhist",100,0,20000)


  for i in range(nevents):
    if not i%(nevents/100):
      print("Processing event "+str(i)+" ("+str(float(i)/nevents*100)+"%)")
    if realnoise:
      traceTree.GetEntry(i%ntraces)
    magnitude = random.uniform(0,maxmagnitude)
    energy[0] = magnitude
    workingWF = ROOT.EXODoubleWaveform(highBandwidthWF)
    workingWF *= magnitude
    transfer.Transform(workingWF)
    workingWF /= transfer.GetGain()
    doubleWFnorth = ROOT.EXODoubleWaveform()
    doubleWFnorth.SetLength(2048)
    doubleWFnorth.SetSamplingPeriod(ROOT.SAMPLE_TIME_HIGH_BANDWIDTH*ROOT.BANDWIDTH_FACTOR)
    for j in range(2048):
      doubleWFnorth[j] = workingWF[j*ROOT.BANDWIDTH_FACTOR] * gain + 0.5 + baseline
    doubleWFsouth = ROOT.EXODoubleWaveform(doubleWFnorth)
    if realnoise:
      funcNorth = getattr(doubleWFnorth,'operator+=<Double_t>')
      funcSouth = getattr(doubleWFsouth,'operator+=<Double_t>')
      doubleWFnorth = funcNorth(wfNorth)
      doubleWFsouth = funcSouth(wfSouth)
    else:
      noiseTransfer.Transform(doubleWFnorth)
      noiseTransfer.Transform(doubleWFsouth)
    wf = doubleWFnorth.Convert()
    finalWFNorth = ROOT.EXOWaveform(wf.GetData(),2048)
    wf = doubleWFsouth.Convert()
    finalWFSouth = ROOT.EXOWaveform(wf.GetData(),2048)
    finalWFNorth.SetSamplingPeriod(doubleWFnorth.GetSamplingPeriod())
    finalWFSouth.SetSamplingPeriod(doubleWFsouth.GetSamplingPeriod())
    finalWFNorth.fChannel = -1
    finalWFSouth.fChannel = -2
    #finalWFNorth.GimmeHist().Draw()
    #raw_input("Enter to continue")

    proclist = ROOT.EXOReconProcessList()
    proclist.Add(finalWFNorth,ROOT.EXOReconUtil.kAPD)
    proclist.Add(finalWFSouth,ROOT.EXOReconUtil.kAPD)
    for threshold in thresholds:
      thresh[0] = threshold
      mfFinder.SetAPDSumThresholdFactor(threshold)
      for window in windows:
        win[0] = window
        proclist.ResetIterator()
        mfFinder.SetAPDSmoothWindow(window)
        foundSignals = ROOT.EXOSignalCollection()
        foundSignals.Add(mfFinder.FindSignals(proclist,foundSignals))
        refinedSignals = ROOT.EXOSignalCollection()
        refinedSignals.Add(sigFitter.Extract(proclist,foundSignals))
        chansig = refinedSignals.GetSignalsForChannel(-1)
        chan[0] = -1
        if chansig:
          nsc[0] = chansig.GetNumSignals()
          chansig.ResetIterator()
          sig = chansig.Next()
          while sig:
            northenergyhist.Fill(sig.fMagnitude * ROOT.APD_ADC_FULL_SCALE_ELECTRONS / (ROOT.ADC_BITS * ROOT.APD_GAIN))
            sig = chansig.Next()
        else:
          nsc[0] = 0
        outtree.Fill()
        chansig = refinedSignals.GetSignalsForChannel(-2)
        chan[0] = -2
        if chansig:
          nsc[0] = chansig.GetNumSignals()
          chansig.ResetIterator()
          sig = chansig.Next()
          while sig:
            southenergyhist.Fill(sig.fMagnitude * ROOT.APD_ADC_FULL_SCALE_ELECTRONS / (ROOT.ADC_BITS * ROOT.APD_GAIN))
            sig = chansig.Next()
        else:
          nsc[0] = 0
        outtree.Fill()
  outfile.cd()
  outtree.Write()
  northenergyhist.Write()
  southenergyhist.Write()
  outfile.Close()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" NoiseTraceFile")
    sys.exit(1)
  main(sys.argv[1])
