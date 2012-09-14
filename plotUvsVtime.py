import ROOT,sys

def main(filename,detHalf):
  ROOT.gSystem.Load("libEXOROOT")

  hist = ROOT.TH1D("hist","hist",400,-20,20)
  hist.GetXaxis().SetTitle("U-time - V-time")

  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    for j in range(ED.GetNumUWireSignals()):
      uws = ED.GetUWireSignal(j)
      if ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel) != detHalf:
        continue
      for k in range(ED.GetNumVWireSignals()):
        vws = ED.GetVWireSignal(k)
        if ROOT.EXOMiscUtil.GetTPCSide(vws.fChannel) != detHalf:
          continue
        timediff = (uws.fTime - vws.fTime)/1000.
        hist.Fill(timediff)

  canvas1 = ROOT.TCanvas("canvas1")
  hist.Draw()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " file detectorHalf")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]))

