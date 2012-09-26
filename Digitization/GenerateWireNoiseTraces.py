import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOROOT")
  f = ROOT.TFile(sys.argv[1])
  t = f.Get("tree")

  noisetagger = ROOT.EXOAlphaNoiseTagger()
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  t.GetEntry(0)

  output = ROOT.TFile("NoiseTraces"+str(t.EventBranch.fRunNumber)+".root","RECREATE")
  outtree = ROOT.TTree("TraceTree","TraceTree")
  waveforms = []
  for i in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE):
    waveforms.append(ROOT.EXODoubleWaveform())
    waveforms[-1].SetLength(2048)
    outtree.Branch("ch"+str(i),"EXODoubleWaveform",waveforms[-1])

  n = t.GetEntries()
  for i in range(n):
    if not i%(n/100):
      print("processing entry "+str(i)+" ("+str(float(i)/n*100.)+"%)")
    t.GetEntry(i)
    if ED.fEventHeader.fSumTriggerRequest or ED.fEventHeader.fIndividualTriggerRequest:
      continue
    wfd = ED.GetWaveformData()
    wfd.Decompress()
    if not i:
      noisetagger.BeginOfRun(ED)
    noisetagger.ProcessEvent(ED)
    if ED.fEventHeader.fTaggedAsNoise or ED.fEventHeader.fTaggedAsMuon:
      continue
    good = True
    for j in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE):
      waveforms[j] = wfd.GetWaveformWithChannel(j).Convert()
      outtree.SetBranchAddress("ch"+str(j),waveforms[j])
      if waveforms[j].GetLength() != 2048: 
        good = False
        break
    if not good:
      print("Entry " + str(i) + " had incomplete waveform(s)")
      continue
    outtree.Fill()

  output.cd()
  outtree.Write()
  output.Close()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" LowBGDataFile")
    sys.exit(1)
  main(sys.argv[1])
