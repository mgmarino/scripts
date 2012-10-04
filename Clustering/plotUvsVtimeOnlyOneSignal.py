import ROOT,sys

def main(filename,detHalf):
  ROOT.gSystem.Load("libEXOROOT")

  hist = ROOT.TH1D("hist","hist",400,-15,15)
  hist.GetXaxis().SetTitle("U-time - V-time")
  hist2 = ROOT.TH2D("hist2","",100,-3,130,100,-10,10)
  hist2.GetXaxis().SetTitle("U-time - Scint-time")
  hist2.GetYaxis().SetTitle("U-time - V-time")

  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nuws = ED.GetNumUWireSignals()
    if nuws != 1:
      continue
    nsc = ED.GetNumScintillationClusters()
    if nsc != 1:
      continue
    sc = ED.GetScintillationCluster(0)
    nvws = ED.GetNumVWireSignals()
    uws = ED.GetUWireSignal(0)
    timeToScint = (uws.fTime - sc.fTime)/1000.
    if detHalf != 2 and ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel) != detHalf:
      continue
    #if timeToScint < 10:
      #continue
    maxSigTimeDiff = -999.
    maxSigEnergy = -999.
    for j in range(nvws):
      vws = ED.GetVWireSignal(j)
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
  canvas2.SetLogz()
  hist2.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if not (len(sys.argv) in [2,3]):
    print("usage: " + sys.argv[0] + " file [detectorHalf]")
    sys.exit(1)
  if len(sys.argv) == 3:
    main(sys.argv[1],int(sys.argv[2]))
  else:
    main(sys.argv[1],2)

