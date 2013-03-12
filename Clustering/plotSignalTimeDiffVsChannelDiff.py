import ROOT,sys

def main(files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)

  hU = ROOT.TH2D("hU","hU",5,-2,3,100,-10,10)
  hV = ROOT.TH2D("hV","hV",9,-4,5,100,-20,20)
  hVmax = ROOT.TH2D("hVmax","hVmax",9,-4,5,100,-20,20)
  hDiff1 = ROOT.TH1D("hDiff1","hDiff1",100,-20,20)
  hDiff2 = ROOT.TH1D("hDiff2","hDiff2",100,-20,20)
  hDiff2.SetLineColor(ROOT.kRed)
  hDiff3 = ROOT.TH1D("hDiff3","hDiff3",100,-20,20)
  hDiff3.SetLineColor(ROOT.kBlue)
  hDiff4 = ROOT.TH1D("hDiff4","hDiff4",100,-20,20)
  hDiff4.SetLineColor(5)

  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nuws = ED.GetNumUWireSignals()
    for j in range(nuws):
      uws1 = ED.GetUWireSignal(j)
      for k in range(nuws):
        if k == j:
          continue
        uws2 = ED.GetUWireSignal(k)
        hU.Fill(uws1.fChannel-uws2.fChannel,(uws1.fTime-uws2.fTime)/1000.)
    nvws = ED.GetNumVWireSignals()
    eVmax = 0.
    for j in range(nvws):
      vws1 = ED.GetVWireSignal(j)
      if vws1.fCorrectedMagnitude > eVmax:
        eVmax = vws1.fCorrectedMagnitude
        Vmax = vws1
      for k in range(nvws):
        if k == j:
          continue
        vws2 = ED.GetVWireSignal(k)
        hV.Fill(vws1.fChannel-vws2.fChannel,(vws1.fTime-vws2.fTime)/1000.)
    for j in range(nvws):
      vws = ED.GetVWireSignal(j)
      if vws != Vmax:
        diff = vws.fChannel-Vmax.fChannel
        timeDiff = (vws.fTime - Vmax.fTime)/1000.
        hVmax.Fill(diff,timeDiff)
        if abs(diff) == 1:
          hDiff1.Fill(timeDiff)
        elif abs(diff) == 2:
          hDiff2.Fill(timeDiff)
        elif abs(diff) == 3:
          hDiff3.Fill(timeDiff)
        elif abs(diff) == 4:
          hDiff4.Fill(timeDiff)
  c1 = ROOT.TCanvas("c1")
  hU.Draw("colz")
  c2 = ROOT.TCanvas("c2")
  hV.Draw("colz")
  c3 = ROOT.TCanvas("c3")
  hVmax.Draw("colz")
  c4 = ROOT.TCanvas("c4")
  hDiff1.Draw()
  hDiff2.Draw("same")
  hDiff3.Draw("same")
  hDiff4.Draw("same")
  raw_input("enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])
