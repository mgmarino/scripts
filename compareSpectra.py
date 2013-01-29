import ROOT,sys,Files

def Process(old,new,minrun,maxrun,runtypeCheck):
  print("overall files in new directory:")
  print(Files.GetFilesIn(new,minrun,maxrun))
  oldfiles = filter(runtypeCheck,Files.GetFilesIn(old,minrun,maxrun))
  print("Old files to be processed:")
  print("---------------------------------------------------------------")
  for f in oldfiles:
    print f
  print("---------------------------------------------------------------")
  print("\n\n")
  newfiles = filter(runtypeCheck,Files.GetFilesIn(new,minrun,maxrun))
  print("New files to be processed:")
  print("---------------------------------------------------------------")
  for f in newfiles:
    print f
  print("---------------------------------------------------------------")
  print("\n\n")
  oldCSS,oldCMS,oldSSS,oldSMS = GetHist(oldfiles,"old")
  newCSS,newCMS,newSSS,newSMS = GetHist(newfiles,"new")
  newCSS.SetLineColor(ROOT.kRed)
  newCMS.SetLineColor(ROOT.kRed)
  newSSS.SetLineColor(ROOT.kRed)
  newSMS.SetLineColor(ROOT.kRed)
  newCSS.SetTitle("new")
  newCMS.SetTitle("new")
  newSSS.SetTitle("new")
  newSMS.SetTitle("new")
  oldCSS.SetTitle("old")
  oldCMS.SetTitle("old")
  oldSSS.SetTitle("old")
  oldSMS.SetTitle("old")
  c1 = ROOT.TCanvas("c1","Charge",1200,400)
  c1.Divide(2,1)
  pad = c1.cd(1)
  oldCSS.Draw()
  newCSS.Draw("same")
  pad.BuildLegend()
  pad = c1.cd(2)
  oldCMS.Draw()
  newCMS.Draw("same")
  pad.BuildLegend()
  c2 = ROOT.TCanvas("c2","Scint",1200,400)
  c2.Divide(2,1)
  pad = c2.cd(1)
  oldSSS.Draw()
  newSSS.Draw("same")
  pad.BuildLegend()
  pad = c2.cd(2)
  oldSMS.Draw()
  newSMS.Draw("same")
  pad.BuildLegend()

  c1.SaveAs("Charge.C")
  c2.SaveAs("Scint.C")

def GetHist(files,name):
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  print("tree for name "+name+" contains "+str(t.GetEntries())+" entries")
  nbins = 100
  zCut = 160
  binstring = str(nbins)

  t.Draw("fChargeClusters.fCorrectedEnergy>>"+name+"ChargeSS("+binstring+",0,3000)","@fScintClusters.size() == 1 && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 0.1 && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
  t.Draw("fChargeClusters.fCorrectedEnergy>>"+name+"ChargeMS("+binstring+",0,3000)","@fScintClusters.size() == 1 && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) >= 0.1 || Max$(fChargeClusters.GetNumUWireSignals()) > 2","goff")
  t.Draw("fScintClusters.GetCountsSumOnAPDPlane(0) + fScintClusters.GetCountsSumOnAPDPlane(1)>>"+name+"ScintSS("+binstring+",0,60000)","@fScintClusters.size() == 1 && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 0.1 && Max$(fChargeClusters.GetNumUWireSignals()) < 3","goff")
  t.Draw("fScintClusters.GetCountsSumOnAPDPlane(0) + fScintClusters.GetCountsSumOnAPDPlane(1)>>"+name+"ScintMS("+binstring+",0,60000)","@fScintClusters.size() == 1 && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) >= 0.1 || Max$(fChargeClusters.GetNumUWireSignals()) > 2","goff")

  chargeSS = ROOT.gDirectory.Get(name+"ChargeSS")
  chargeMS = ROOT.gDirectory.Get(name+"ChargeMS")
  scintSS = ROOT.gDirectory.Get(name+"ScintSS")
  scintMS = ROOT.gDirectory.Get(name+"ScintMS")

  return chargeSS,chargeMS,scintSS,scintMS


if __name__ == "__main__":
  ROOT.gROOT.SetBatch(True)
  ROOT.gSystem.Load("libEXOUtilities")
  Process("$EXODATA3/Archived/masked_1_9_13","$EXODATA3/masked",4000,4628,Files.IsThorium)
