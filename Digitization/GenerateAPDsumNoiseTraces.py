import ROOT,sys,math

if len(sys.argv) != 2:
  print("usage: "+sys.argv[0]+" LowBGDataFile")
  sys.exit(1)

ROOT.gSystem.Load("libEXOROOT")
f = ROOT.TFile(sys.argv[1])
t = f.Get("tree")

ED = ROOT.EXOEventData()
t.SetBranchAddress("EventBranch",ED)
t.GetEntry(0)

output = ROOT.TFile("NoiseTraces"+str(t.EventBranch.fRunNumber)+".root","RECREATE")
outtree = ROOT.TTree("TraceTree","TraceTree")
wfNorth = ROOT.EXODoubleWaveform()
wfNorth.SetLength(2048)
wfSouth = ROOT.EXODoubleWaveform()
wfSouth.SetLength(2048)
outtree.Branch("wfNorth","EXODoubleWaveform",wfNorth)
outtree.Branch("wfSouth","EXODoubleWaveform",wfSouth)

counter = 0

n = t.GetEntries()
for i in range(n):
  if not i%(n/100):
    print("processing entry "+str(i)+" ("+str(float(i)/n*100.)+"%)")
  t.GetEntry(i)
  if ED.fEventHeader.fTaggedAsNoise or ED.fEventHeader.fTaggedAsMuon:
    continue
  if ED.fEventHeader.fSumTriggerRequest or ED.fEventHeader.fIndividualTriggerRequest:
    continue
  wfd = ED.GetWaveformData()
  wfd.Decompress()
  wfNorth.Zero()
  wfSouth.Zero()
  for j in range(1,37):
    wf1 = wfd.GetWaveformWithChannel(152+j).Convert()
    if wf1.GetLength() != 2048: continue
    wf2 = wfd.GetWaveformWithChannel(189+j).Convert()
    if wf2.GetLength() != 2048: continue
    if counter == 0:
      wfNorth.SetSamplingFreq(wf1.GetSamplingFreq())
      wfSouth.SetSamplingFreq(wf2.GetSamplingFreq())
    wfNorth += wf1
    wfSouth += wf2
  counter += 1
  outtree.Fill()

outtree.Write()
output.Close()
