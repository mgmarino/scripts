import ROOT,sys

def main(files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  hist = ROOT.TH2D("hist","hist",100,-20,20,100,0,1)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nuws = ED.GetNumUWireSignals()
    for j in range(nuws):
      uws1 = ED.GetUWireSignal(j)
      for k in range(j+1,nuws):
        uws2 = ED.GetUWireSignal(k)
        if abs(uws1.fChannel - uws2.fChannel) == 1:
          if uws1.fCorrectedEnergy > uws2.fCorrectedEnergy:
            hist.Fill((uws1.fTime-uws2.fTime)/1000.,uws2.fCorrectedEnergy/uws1.fCorrectedEnergy)
          else:
            hist.Fill((uws2.fTime-uws1.fTime)/1000.,uws1.fCorrectedEnergy/uws2.fCorrectedEnergy)
  
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])
