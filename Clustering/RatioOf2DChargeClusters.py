import ROOT,sys

def GetNumSite(sc):
  ncc = sc.GetNumChargeClusters()
  if ncc == 1:
    cc = sc.GetChargeClusterAt(0)
    Uchannels = set()
    for i in range(cc.GetNumUWireSignals()):
      Uchannels.add(cc.GetUWireSignalAt(i).fChannel)
    if len(Uchannels) > 2:
      return 2
    return 1
  return ncc

def DatabaseFlavor(isMC,numSite):
  if isMC:
    if numSite > 1:
      return "MCMS"
    else:
      return "MCSS"
  else:
    if numSite > 1:
      return "MS"
    else:
      return "SS"

def main(files,nbins,rng,zCut):
  ROOT.gSystem.Load("libEXOUtilities")
  ROOT.gSystem.Load("libEXOCalibUtilities")

  hSSgood = ROOT.TH1D("hSSgood","hSSgood",nbins,0,rng)
  hSSfull = ROOT.TH1D("hSSfull","hSSfull",nbins,0,rng)
  hMSgood = ROOT.TH1D("hMSgood","hMSgood",nbins,0,rng)
  hMSfull = ROOT.TH1D("hMSfull","hMSfull",nbins,0,rng)

  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)

  calib = ROOT.EXOCalibManager.GetCalibManager()
  calib.SetMetadataAccessType("mysql")
  calib.SetPort(3306)
  calib.SetUser("rd_exo_cond_ro")
  calib.SetHost("mysql-node03.slac.stanford.edu")

  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    if ED.GetNumScintillationClusters() != 1:
      continue
    sc = ED.GetScintillationCluster(0)
    numSite = GetNumSite(sc)
    if numSite == 0:
      continue
    for j in range(sc.GetNumChargeClusters()):
      cc = sc.GetChargeClusterAt(j)
      if abs(cc.fZ) > zCut:
        continue
      if ED.fEventHeader.fIsMonteCarloEvent:
        uncalibratedEnergy = cc.fRawEnergy
      else:
        uncalibratedEnergy = cc.fPurityCorrectedEnergy
      good = abs(cc.fX) < 200
      energyCal = calib.getCalib("energy-rotation",DatabaseFlavor(ED.fEventHeader.fIsMonteCarloEvent,numSite),ED.fEventHeader)
      energy = energyCal.CalibratedChargeEnergy(uncalibratedEnergy)
      if numSite > 1:
        hMSfull.Fill(energy)
        if good:
          hMSgood.Fill(energy)
      else:
        hSSfull.Fill(energy)
        if good:
          hSSgood.Fill(energy)
  hSSfull.Sumw2()
  hSSgood.Sumw2()
  hMSfull.Sumw2()
  hMSgood.Sumw2()
  rateSS = ROOT.TGraphAsymmErrors(hSSgood,hSSfull)
  rateMS = ROOT.TGraphAsymmErrors(hMSgood,hMSfull)
  funct = ROOT.TF1("funct","[0] * 0.5 * (1 + TMath::Erf((x-[1]) / (sqrt(2)*[2])))",0,rng)
  funct.SetParameter(0,1)
  funct.SetParameter(1,250)
  funct.SetParameter(2,150)
  rateSS.Fit(funct,"RE")
  print("SS: limit = "+str(funct.GetParameter(0))+" +- "+str(funct.GetParError(0))+", thresh = "+str(funct.GetParameter(1))+" +- "+str(funct.GetParError(1))+", rise = "+str(funct.GetParameter(2))+" +- "+str(funct.GetParError(2)))

  c1 = ROOT.TCanvas("c1","SS")
  rateSS.Draw("AP")
  c2 = ROOT.TCanvas("c2","MS")
  rateMS.Draw("AP")

  raw_input("hit enter to quit")


if __name__ == "__main__":
  if len(sys.argv) < 5:
    print("usage: " + sys.argv[0] + " nbins range zCut file(s)")
    sys.exit(1)
  main(sys.argv[4:],int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
