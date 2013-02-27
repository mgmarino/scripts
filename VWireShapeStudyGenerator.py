import ROOT,sys
import os.path

def main(runs):
  ROOT.gSystem.Load("libEXOUtilities")
  tWF = ROOT.TChain("tree")
  tREC = ROOT.TChain("tree")
  for runstring in runs:
    rawPath,recPath = GetFilesForRun(int(runstring))
    tWF.Add(rawPath)
    tREC.Add(recPath)

  EDwf = ROOT.EXOEventData()
  tWF.SetBranchAddress("EventBranch",EDwf)
  EDrec = ROOT.EXOEventData()
  tREC.SetBranchAddress("EventBranch",EDrec)

  assert(tWF.GetEntries() == tREC.GetEntries())

  zWaveforms = []
  for i in range(-200,201,1):
    wf = ROOT.EXOIntWaveform()
    wf.SetLength(512)
    zWaveforms.append(wf)

  for i in range(tWF.GetEntries()):
    tWF.GetEntry(i)
    tREC.GetEntry(i)
    assert(EDwf.fRunNumber == EDrec.fRunNumber)
    assert(EDwf.fEventNumber == EDrec.fEventNumber)
    wfd = EDwf.GetWaveformData()
    wfd.Decompress()
    for cc in EDrec.GetChargeClusterArray():
      if abs(cc.fZ) > 200:
        continue
      vws = GetLargestVSignal(cc)
      if vws and vws.fTime/1000. > 256 and vws.fTime/1000. < 1792:
        wf = wfd.GetWaveformWithChannel(vws.fChannel)
        if wf.size() != 2048:
          print("skipping waveform of size "+str(wf.size()))
          continue
        subWf = GetSubWaveform(wf,vws.fTime)
        index = 200 + int(cc.fZ)
        if cc.fZ > 0:
          index -= 1
        zWaveforms[index] += subWf
  outfile = ROOT.TFile("Vstudy.root","RECREATE")
  for i,wf in enumerate(zWaveforms):
    wf.Write("WF_Z_"+str(i-200))
  outfile.Close()


def GetLargestVSignal(cc):
  largest = None
  maxE = 0
  for i in range(cc.GetNumVWireSignals()):
    vws = cc.GetVWireSignalAt(i)
    if vws.fCorrectedMagnitude > maxE:
      largest = vws
      maxE = vws.fCorrectedMagnitude
  return largest

def GetFilesForRun(run):
  recPath = os.path.expandvars("$EXODATA3/masked/"+str(run)+"/masked"+str(run).zfill(8)+"-000.root")
  for i in range(2,6):
    rawPath = os.path.expandvars("$EXODATA"+str(i)+"/root/"+str(run)+"/run"+str(run).zfill(8)+"-000.root")
    if os.path.isfile(rawPath):
      return rawPath,recPath

def GetSubWaveform(wf,time):
  index = wf.GetIndexAtTime(time)
  lower = index - 256
  upper = index + 256
  assert(lower >= 0)
  assert(upper <= 2048)
  return wf.SubWaveform(lower,upper)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: "+sys.argv[0]+" run[s]")
    sys.exit(1)
  main(sys.argv[1:])
