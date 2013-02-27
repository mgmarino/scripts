import ROOT,sys

def main(files,detHalf):
  ROOT.gSystem.Load("libEXOROOT")

  hist = ROOT.TH1D("hist","hist",400,-20,20)
  hist.GetXaxis().SetTitle("U-time - V-time")

  hist2 = ROOT.TH2D("hist2","",100,-3,130,100,-10,10)
  hist2.GetXaxis().SetTitle("U-time - Scint-time")
  hist2.GetYaxis().SetTitle("U-time - V-time")

  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nsc = ED.GetNumScintillationClusters()
    if nsc != 1:
      continue
    sc = ED.GetScintillationCluster(0)
    for j in range(ED.GetNumUWireSignals()):
      uws = ED.GetUWireSignal(j)
      timeToScint = (uws.fTime - sc.fTime)/1000.
      if detHalf != 2 and ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel) != detHalf:
        continue
      maxSigTimeDiff = -999.
      maxSigEnergy = -999.
      for k in range(ED.GetNumVWireSignals()):
        vws = ED.GetVWireSignal(k)
        if ROOT.EXOMiscUtil.GetTPCSide(vws.fChannel) != ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel):
          continue
        if vws.fCorrectedMagnitude > maxSigEnergy:
          maxSigEnergy = vws.fCorrectedMagnitude
          maxSigTimeDiff = (uws.fTime - vws.fTime)/1000.
      if maxSigEnergy > 0:
        hist.Fill(maxSigTimeDiff)
        hist2.Fill(timeToScint,maxSigTimeDiff)

  canvas1 = ROOT.TCanvas("canvas1")
  hist.Draw()
  canvas2 = ROOT.TCanvas("canvas2")
  hist2.Draw()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: " + sys.argv[0] + " detectorHalf file[s]")
    print("set detectorHalf=2 to use whole detector")
    sys.exit(1)
  main(sys.argv[2:],int(sys.argv[1]))
