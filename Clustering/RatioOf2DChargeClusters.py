import ROOT,sys

def main(files,nbins,rng,zCut):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  binstring = str(nbins)
  hist = ROOT.TH1D("hist","2D reconstruction rate",nbins,0,rng)
  hist.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histSS = ROOT.TH1D("histSS","Single Site 2D reconstruction rate",nbins,0,rng)
  histSS.GetXaxis().SetTitle("Charge cluster energy (keV)")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hFull("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hGood("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hFullSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut)+" && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 1 && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hGoodSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut)+" && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 1. && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
  hFull = ROOT.gDirectory.Get("hFull")
  hGood = ROOT.gDirectory.Get("hGood")
  hBad = ROOT.TH1F(hFull)
  hBad.Add(hGood,-1)
  hGood.SetLineColor(ROOT.kBlue)
  hGood.SetMarkerColor(ROOT.kBlue)
  hBad.SetLineColor(ROOT.kRed)
  hBad.SetMarkerColor(ROOT.kRed)
  hFullSS = ROOT.gDirectory.Get("hFullSS")
  hGoodSS = ROOT.gDirectory.Get("hGoodSS")
  hBadSS = ROOT.TH1F(hFullSS)
  hBadSS.Add(hGoodSS,-1)
  hGoodSS.SetLineColor(ROOT.kBlue)
  hGoodSS.SetMarkerColor(ROOT.kBlue)
  hBadSS.SetLineColor(ROOT.kRed)
  hBadSS.SetMarkerColor(ROOT.kRed)
  c1 = ROOT.TCanvas("c1")
  hFull.Draw()
  hGood.Draw("same")
  hBad.Draw("same")
  raw_input("hit enter to continue")
  hFullSS.Draw()
  hGoodSS.Draw("same")
  hBadSS.Draw("same")
  raw_input("hit enter to continue")
  hFull.Sumw2()
  hGood.Sumw2()
  hFullSS.Sumw2()
  hGoodSS.Sumw2()
  hist.Divide(hGood,hFull,1,1,"B")
  histSS.Divide(hGoodSS,hFullSS,1,1,"B")
  hist.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    hist.Write(key)
    outfile.Close()
  histSS.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the single site histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    histSS.Write(key)
    outfile.Close()

if __name__ == "__main__":
  if len(sys.argv) < 5:
    print("usage: " + sys.argv[0] + " nbins range zCut file(s)")
    sys.exit(1)
  main(sys.argv[4:],int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
