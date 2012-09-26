import ROOT,sys,random,math
from array import array

realnoise = True

if len(sys.argv) > 2:
  print("usage: "+sys.argv[0]+" [NoiseTraceFile]")
  print("if NoiseTraceFile is not specified, simulated noise will be used")
  sys.exit(1)
elif len(sys.argv) == 1:
  realnoise = False
  print("No NoiseTraceFile specified, will use simulated noise")

ROOT.gSystem.Load("libEXOROOT")

energy = array('d',[0.0])
thresh = array('d',[0.0])
win = array('i',[0])
nsc = array('i',[0])
chan = array('i',[0])

time = 1024*1000
nevents = 20000
maxmagnitude = 15000
#thresholds = [4.0,4.5,5.0,5.5,6.0]
thresholds = [4.0,5.0]
#windows = [0,2,4,6,8,10,12,14,16]
windows = [0,4]
gain = ROOT.ADC_BITS/ROOT.APD_ADC_FULL_SCALE_ELECTRONS*ROOT.APD_GAIN
napdspp = 36
baseline = float(ROOT.APD_ADC_BASELINE_COUNTS*napdspp)
if realnoise:
  baseline = 0.

traceFile = ROOT.TFile
traceTree = ROOT.TTree()
ntraces = 0
wfNorth = ROOT.EXODoubleWaveform()
wfSouth = ROOT.EXODoubleWaveform()
noiseTransfer = ROOT.EXOAddNoise()

if realnoise:
  traceFile = ROOT.TFile(sys.argv[1])
  traceTree = traceFile.Get("TraceTree")
  ntraces = traceTree.GetEntries()
  traceTree.SetBranchAddress("wfNorth",wfNorth)
  traceTree.SetBranchAddress("wfSouth",wfSouth)
else:
  noiseTransfer.AddDiffStageWithTime(10000.0)
  noiseTransfer.AddDiffStageWithTime(10000.0)
  noiseTransfer.AddDiffStageWithTime(300000.0)
  noiseTransfer.AddIntegStageWithTime(3000.0)
  noiseTransfer.AddIntegStageWithTime(3000.0)
  noiseTransfer.SetNoiseMagnitude(2000. * math.sqrt(napdspp) * ROOT.ADC_BITS / ROOT.APD_ADC_FULL_SCALE_ELECTRONS)

outFilename = "Efficiencies.root"
if realnoise:
  outFilename = "Efficiencies-realnoise.root"
outfile = ROOT.TFile(outFilename,"RECREATE")
outtree = ROOT.TTree("EffTree","EffTree")
outtree.Branch("thresh",thresh,"thresh/D")
outtree.Branch("energy",energy,"energy/D")
outtree.Branch("win",win,"win/I")
outtree.Branch("nsc",nsc,"nsc/I")
outtree.Branch("chan",chan,"chan/I")

transfer = ROOT.EXOTransferFunction()
transfer.AddDiffStageWithTime(10000.0)
transfer.AddDiffStageWithTime(10000.0)
transfer.AddDiffStageWithTime(300000.0)
transfer.AddIntegStageWithTime(3000.0)
transfer.AddIntegStageWithTime(3000.0)

talkto = ROOT.EXOTalkToManager()
sigModMgr = ROOT.EXOSignalModelManager()
mfFinder = ROOT.EXOMatchedFilterFinder()
mfFinder.TalkTo("/rec/matched_filter_finder",talkto)
sigFitter = ROOT.EXOSignalFitter()
sigFitter.TalkTo("/rec/signal_fitter",talkto)
sigModMgr.AddRegisteredObject(mfFinder)
sigModMgr.AddRegisteredObject(sigFitter)
sigModMgr.BuildSignalModelForChannelOrTag(-1,ROOT.EXOAPDSignalModelBuilder(transfer))
sigModMgr.BuildSignalModelForChannelOrTag(-2,ROOT.EXOAPDSignalModelBuilder(transfer))
#talkto.InterpretCommand("/rec/matched_filter_finder/verbose/plot APD true")
#talkto.InterpretCommand("/rec/signal_fitter/verbose/plot APD true")

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
    doubleWFnorth += wfNorth
    doubleWFsouth += wfSouth
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
