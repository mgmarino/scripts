import ROOT,sys

def main(files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)

  hist = ROOT.TH1I("hist","hist",10,0,10)
  histEnergy = ROOT.TH2D("histEnergy","histEnergy",100,0,3000,10,0,10)

  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  #calib = ROOT.EXOEnergyCalib.GetInstanceForFlavor("vanilla","vanilla","vanilla")

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    for cc in ED.GetChargeClusterArray():
      channels = set()
      for j in range(cc.GetNumUWireSignals()):
        channels.add(cc.GetUWireSignalChannelAt(j))
      histEnergy.Fill(cc.fPurityCorrectedEnergy,len(channels))
      hist.Fill(len(channels))

  c1 = ROOT.TCanvas("c1")
  hist.Draw()
  c2 = ROOT.TCanvas("c2")
  histEnergy.Draw("colz")
  raw_input("hit enter to quit")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: "+argv[0]+" file[s]")
    sys.exit(1)
  main(sys.argv[1:])
