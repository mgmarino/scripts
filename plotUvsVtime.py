import ROOT,sys

if len(sys.argv) != 2:
  print("usage: " + sys.argv[0] + " file")
  sys.exit(1)

ROOT.gSystem.Load("libEXOROOT")

hist = ROOT.TH1D("hist","hist",400,-20,20)

f = ROOT.TFile(sys.argv[1])
t = f.Get("tree")
ED = ROOT.EXOEventData()
t.SetBranchAddress("EventBranch",ED)

for i in range(t.GetEntries()):
  t.GetEntry(i)
  for j in range(ED.GetNumUWireSignals()):
    uws = ED.GetUWireSignal(j)
    for k in range(ED.GetNumVWireSignals()):
      vws = ED.GetVWireSignal(k)
      timediff = (uws.fTime - vws.fTime)/1000.
      hist.Fill(timediff)

canvas1 = ROOT.TCanvas("canvas1")
hist.Draw()
raw_input("hit enter to quit")
