import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  t.Draw("Sum$(fChargeClusters.fPurityCorrectedEnergy)>>hTotal(100,0,3000)","","goff")
  t.Draw("Sum$(fChargeClusters.fAmplitudeInVChannels)>>hTotalV(100,0,600)","","goff")
  t.Draw("fChargeClusters.fY:fChargeClusters.fX>>hXY(100,-300,300,100,-200,200)","","goff")
  histtotal = ROOT.gDirectory.Get("hTotal")
  histtotalV = ROOT.gDirectory.Get("hTotalV")
  histXY = ROOT.gDirectory.Get("hXY")
  histXY.GetXaxis().SetTitle("X (mm")
  histXY.GetYaxis().SetTitle("Y (mm")
  histGoodss = ROOT.TH1D("histGoodss","Single site inside hexagon",100,0,3000)
  histGoodss.GetXaxis().SetTitle("Purity corrected charge energy")
  histBadss = ROOT.TH1D("histBadss","Single site outside hexagon",100,0,3000)
  histBadss.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodms = ROOT.TH1D("histGoodms","Multi site inside hexagon",100,0,3000)
  histGoodms.GetXaxis().SetTitle("Purity corrected charge energy")
  histBadms = ROOT.TH1D("histBadms","Multi site (at least one cc outside hexagon)",100,0,3000)
  histBadms.GetXaxis().SetTitle("Purity corrected charge energy")

  histGoodssGoodZ = ROOT.TH1D("histGoodssGoodZ","Single site inside hexagon |Z| <= 185",100,0,3000)
  histGoodssGoodZ.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodssBadZ = ROOT.TH1D("histGoodssBadZ","Single site inside hexagon |Z| > 185",100,0,3000)
  histGoodssBadZ.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodmsGoodZ = ROOT.TH1D("histGoodmsGoodZ","Multi site inside hexagon |Z| <= 185",100,0,3000)
  histGoodmsGoodZ.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodmsGoodZHighClusterEnergy = ROOT.TH1D("histGoodmsGoodZHighClusterEnergy","Multi site inside hexagon |Z| <= 185 Each cc > 400 keV",100,0,3000)
  histGoodmsGoodZHighClusterEnergy.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodmsGoodZSingleClusters = ROOT.TH1D("histGoodmsGoodZSingleClusters","Single charge cluster MS spectrum",100,0,3000)
  histGoodmsGoodZSingleClusters.GetXaxis().SetTitle("Purity corrected charge energy")
  histGoodmsBadZ = ROOT.TH1D("histGoodmsBadZ","Multi site inside hexagon |Z| > 185",100,0,3000)
  histGoodmsBadZ.GetXaxis().SetTitle("Purity corrected charge energy")

  histGoodssV = ROOT.TH1D("histGoodssV","Single site V-spectrum inside hexagon",100,0,600)
  histGoodssV.GetXaxis().SetTitle("V-energy")
  histBadssV = ROOT.TH1D("histBadssV","Single site V-spectrum outside hexagon",100,0,600)
  histBadssV.GetXaxis().SetTitle("V-energy")
  histGoodZ = ROOT.TH1D("histGoodZ","CC Z-position inside hexagon",100,-200,200)
  histGoodZ.GetXaxis().SetTitle("Z (mm)")
  histBadZ = ROOT.TH1D("histBadZ","CC Z-position outside hexagon",100,-200,200)
  histBadZ.GetXaxis().SetTitle("Z (mm)")

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nsc = ED.GetNumScintillationClusters()
    if nsc != 1:
      continue
    sc = ED.GetScintillationCluster(0)
    ncl = sc.GetNumChargeClusters()
    energy = 0.0
    Venergy = 0.0
    bad = False
    badZ = False
    eachAbove400 = True
    for j in range(ncl):
      cc = sc.GetChargeClusterAt(j)
      if abs(cc.fZ) <= 185 and abs(cc.fX) <= 176 and ncl > 1:
        histGoodmsGoodZSingleClusters.Fill(cc.fPurityCorrectedEnergy)
      if abs(cc.fZ) > 185:
        badZ = True
      if abs(cc.fX) > 176:
        if cc.fPurityCorrectedEnergy > 1000 and ncl == 1:
          print("high energy cc seems to be outside hexagon (run\\event): " + str(ED.fRunNumber) + "\\" + str(ED.fEventNumber) + ", X = " +str(cc.fX) + ", ncl = " + str(ncl))
        bad = True
        histBadZ.Fill(cc.fZ)
      else:
        histGoodZ.Fill(cc.fZ)
      Venergy += cc.fAmplitudeInVChannels
      energy += cc.fPurityCorrectedEnergy
      if cc.fPurityCorrectedEnergy < 400:
        eachAbove400 = False
    if ncl == 1:
      if bad:
        histBadssV.Fill(Venergy)
        histBadss.Fill(energy)
      else:
        histGoodssV.Fill(Venergy)
        histGoodss.Fill(energy)
        if badZ:
          #print("cc near anode in run\\event " + str(ED.fRunNumber) + "\\" + str(ED.fEventNumber))
          histGoodssBadZ.Fill(energy)
        else:
          histGoodssGoodZ.Fill(energy)
    elif ncl > 1:
      if bad:
        histBadms.Fill(energy)
      else:
        histGoodms.Fill(energy)
        if badZ:
          histGoodmsBadZ.Fill(energy)
        else:
          histGoodmsGoodZ.Fill(energy)
          if eachAbove400:
            histGoodmsGoodZHighClusterEnergy.Fill(energy)
  f = ROOT.TFile("Spectrum.root","RECREATE")
  histtotal.Write("hTotal")
  histtotalV.Write("hTotalV")
  histXY.Write("hXY")
  histGoodss.Write("hGoodSS")
  histBadss.Write("hBadSS")
  histGoodms.Write("hGoodMS")
  histBadms.Write("hBadMS")
  histGoodssV.Write("hGoodSSv")
  histBadssV.Write("hBadSSv")
  histGoodZ.Write("hGoodZ")
  histBadZ.Write("hBadZ")
  histGoodssGoodZ.Write("hGoodSSGoodZ")
  histGoodssBadZ.Write("hGoodSSBadZ")
  histGoodmsGoodZ.Write("hGoodMSGoodZ")
  histGoodmsGoodZHighClusterEnergy.Write("hGoodMSGoodZHighClusterEnergy")
  histGoodmsGoodZSingleClusters.Write("hGoodMSGoodZSingleCluster")
  histGoodmsBadZ.Write("hGoodMSBadZ")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + "filename")
    sys.exit(1)
  main(sys.argv[1])
