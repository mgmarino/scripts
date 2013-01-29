import ROOT,sys,Files

def Process(old,new,minrun,maxrun,runtypeCheck):
  oldfiles = filter(runtypeCheck,Files.GetFilesIn(old,minrun,maxrun))
  newfiles = filter(runtypeCheck,Files.GetFilesIn(new,minrun,maxrun))
  oldhist,oldhistSS = GetHist(oldfiles,"old")
  newhist,newhistSS = GetHist(newfiles,"new")
  newhist.SetLineColor(ROOT.kRed)
  newhistSS.SetLineColor(ROOT.kRed)
  oldhist.SetTitle("old")
  newhist.SetTitle("new")
  oldhistSS.SetTitle("old")
  newhistSS.SetTitle("new")
  oldhist.GetYaxis().SetRangeUser(0,1.1)
  oldhistSS.GetYaxis().SetRangeUser(0,1.1)
  newhist.GetYaxis().SetRangeUser(0,1.1)
  newhistSS.GetYaxis().SetRangeUser(0,1.1)
  oldhist.GetYaxis().SetTitle("CC 2D recon rate")
  oldhistSS.GetYaxis().SetTitle("CC SS 2D recon rate")
  newhist.GetYaxis().SetTitle("CC 2D recon rate")
  newhistSS.GetYaxis().SetTitle("CC SS 2D recon rate")
  c1 = ROOT.TCanvas()
  oldhist.Draw()
  newhist.Draw("same")
  c1.BuildLegend()
  c2 = ROOT.TCanvas()
  oldhistSS.Draw()
  newhistSS.Draw("same")
  c2.BuildLegend()
  raw_input("hit enter to quit")

def GetHist(files,name):
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  nbins = 100
  rng = 3000
  zCut = 160
  binstring = str(nbins)
  hist = ROOT.TH1D(name,"2D reconstruction rate",nbins,0,rng)
  hist.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histSS = ROOT.TH1D(name+"SS","Single Site 2D reconstruction rate",nbins,0,rng)
  histSS.GetXaxis().SetTitle("Charge cluster energy (keV)")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hFull("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hGood("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hFullSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut)+" && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 1 && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>hGoodSS("+binstring+",0,"+str(rng)+")","fChargeClusters.fCorrectedEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut)+" && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 1. && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
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
  return hist,histSS


if __name__ == "__main__":
  ROOT.gSystem.Load("libEXOUtilities")
  Process("$EXODATA3/Archived/masked_1_9_13","$EXODATA3/masked",4000,4600,Files.IsPhysics)
