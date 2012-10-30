import ROOT,sys

def main(filename,nbins,rng,zCut):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  binstring = str(nbins)
  hist = ROOT.TH1D("hist","2D reconstruction rate",nbins,0,rng)
  hist.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histSS = ROOT.TH1D("histSS","Single Site 2D reconstruction rate",nbins,0,rng)
  histSS.GetXaxis().SetTitle("Charge cluster energy (keV)")
  t.Draw("fChargeClusters.fRawEnergy>>hFull("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fRawEnergy>>hGood("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fRawEnergy>>hFullSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut)+" && @fChargeClusters.size() == 1","goff")
  t.Draw("fChargeClusters.fRawEnergy>>hGoodSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut)+" && @fChargeClusters.size() == 1","goff")
  hFull = ROOT.gDirectory.Get("hFull")
  hGood = ROOT.gDirectory.Get("hGood")
  hFullSS = ROOT.gDirectory.Get("hFullSS")
  hGoodSS = ROOT.gDirectory.Get("hGoodSS")
  hFull.Sumw2()
  hGood.Sumw2()
  hFullSS.Sumw2()
  hGoodSS.Sumw2()
  hist.Divide(hGood,hFull,1,1,"B")
  histSS.Divide(hGoodSS,hFullSS,1,1,"B")
  c1 = ROOT.TCanvas("c1")
  hFullSS.Draw()
  c2 = ROOT.TCanvas("c2")
  hGoodSS.Draw()
  raw_input("hit enter to continue")
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
  if len(sys.argv) != 5:
    print("usage: " + sys.argv[0] + " filename nbins range zCut")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
