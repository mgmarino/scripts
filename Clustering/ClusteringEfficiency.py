import ROOT,sys
from math import sqrt

def main(t):
  nbins = 300
  rng = 3000

  hSSgood = ROOT.TH1D("hSSgood","hSSgood",nbins,0,rng)
  hSSfull = ROOT.TH1D("hSSfull","hSSfull",nbins,0,rng)
  hSSgoodZcut = ROOT.TH1D("hSSgoodZcut","hSSgoodZcut",nbins,0,rng)
  hSSfullZcut = ROOT.TH1D("hSSfullZcut","hSSfullZcut",nbins,0,rng)
  hMSgood = ROOT.TH1D("hMSgood","hMSgood",nbins,0,rng)
  hMSfull = ROOT.TH1D("hMSfull","hMSfull",nbins,0,rng)
  hMSgoodZcut = ROOT.TH1D("hMSgoodZcut","hMSgoodZcut",nbins,0,rng)
  hMSfullZcut = ROOT.TH1D("hMSfullZcut","hMSfullZcut",nbins,0,rng)
  hMSTotalgood = ROOT.TH1D("hMSTotalgood","hMSTotalgood",nbins,0,rng)
  hMSTotalfull = ROOT.TH1D("hMSTotalfull","hMSTotalfull",nbins,0,rng)
  hMSTotalgoodZcut = ROOT.TH1D("hMSTotalgoodZcut","hMSTotalgoodZcut",nbins,0,rng)
  hMSTotalfullZcut = ROOT.TH1D("hMSTotalfullZcut","hMSTotalfullZcut",nbins,0,rng)
  hMSTotalWithEnergygood = ROOT.TH1D("hMSTotalWithEnergygood","hMSTotalWithEnergygood",nbins,0,rng)
  hMSTotalWithEnergyfull = ROOT.TH1D("hMSTotalWithEnergyfull","hMSTotalWithEnergyfull",nbins,0,rng)
  hMSTotalWithEnergygoodZcut = ROOT.TH1D("hMSTotalWithEnergygoodZcut","hMSTotalWithEnergygoodZcut",nbins,0,rng)
  hMSTotalWithEnergyfullZcut = ROOT.TH1D("hMSTotalWithEnergyfullZcut","hMSTotalWithEnergyfullZcut",nbins,0,rng)

  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    if ED.fEventHeader.fTaggedAsNoise:
      continue

    numSite = GetNumSite(ED)
    if numSite < 1:
      continue
    nsc = ED.GetNumScintillationClusters()
    totalEnergy = 0.0
    allGood = True
    allWithEnergyGood = True
    allWithinZ = True
    for cc in ED.GetChargeClusterArray():
      energy = GetEnergy(cc,ED)
      totalEnergy += energy
      good = abs(cc.fX) < 200
      withEnergyGood = good
      if energy < 0.01:
        witEnergyGood = True
      withinZ = abs(cc.fZ) < 182

      if numSite == 1:
        hSSfull.Fill(energy)
        if good:
          hSSgood.Fill(energy)
        if withinZ and nsc == 1:
          hSSfullZcut.Fill(energy)
          if good:
            hSSgoodZcut.Fill(energy)
      else:
        hMSfull.Fill(energy)
        if good:
          hMSgood.Fill(energy)
        if withinZ and nsc == 1:
          hMSfullZcut.Fill(energy)
          if good:
            hMSgoodZcut.Fill(energy)

      allGood = allGood and good
      allWithEnergyGood = allWithEnergyGood and withEnergyGood 
      allWithinZ = allWithinZ and withinZ

    if numSite > 1:
      hMSTotalfull.Fill(totalEnergy)
      if allGood:
        hMSTotalgood.Fill(totalEnergy)
      hMSTotalWithEnergyfull.Fill(totalEnergy)
      if allWithEnergyGood:
        hMSTotalWithEnergygood.Fill(totalEnergy)
      if allWithinZ and nsc == 1:
        hMSTotalfullZcut.Fill(totalEnergy)
        if allGood:
          hMSTotalgoodZcut.Fill(totalEnergy)
        hMSTotalWithEnergyfullZcut.Fill(totalEnergy)
        if allWithEnergyGood:
          hMSTotalWithEnergygoodZcut.Fill(totalEnergy)

  rateSS = ROOT.TGraphAsymmErrors(hSSgood,hSSfull)
  rateSS.SetName("rateSS")
  rateSSZcut = ROOT.TGraphAsymmErrors(hSSgoodZcut,hSSfullZcut)
  rateSSZcut.SetName("rateSSZcut")
  rateMS = ROOT.TGraphAsymmErrors(hMSgood,hMSfull)
  rateMS.SetName("rateMS")
  rateMSZcut = ROOT.TGraphAsymmErrors(hMSgoodZcut,hMSfullZcut)
  rateMSZcut.SetName("rateMSZcut")
  rateMStotal = ROOT.TGraphAsymmErrors(hMSTotalgood,hMSTotalfull)
  rateMStotal.SetName("rateMStotal")
  rateMStotalZcut = ROOT.TGraphAsymmErrors(hMSTotalgoodZcut,hMSTotalfullZcut)
  rateMStotalZcut.SetName("rateMStotalZcut")
  rateMStotalWithEnergy = ROOT.TGraphAsymmErrors(hMSTotalWithEnergygood,hMSTotalWithEnergyfull)
  rateMStotalWithEnergy.SetName("rateMStotalWithEnergy")
  rateMStotalWithEnergyZcut = ROOT.TGraphAsymmErrors(hMSTotalWithEnergygoodZcut,hMSTotalWithEnergyfullZcut)
  rateMStotalWithEnergyZcut.SetName("rateMStotalWithEnergyZcut")

  fout = ROOT.TFile("ClusteringEfficiency.root","RECREATE")
  rateSS.Write()
  rateSSZcut.Write()
  rateMS.Write()
  rateMSZcut.Write()
  rateMStotal.Write()
  rateMStotalZcut.Write()
  rateMStotalWithEnergy.Write()
  rateMStotalWithEnergyZcut.Write()
  hSSfullZcut.Write()
  hMSfullZcut.Write()
  hMSTotalfullZcut.Write()

def GetNumSite(ED,sc = None):
  if sc:
    culler = ROOT.EXOClusterCull()
    ses = culler.ClusterCull(sc,ED)
    return ses.GetNumSite()
  else:
    #This should mimic the GetNumSite() of EXOScintEventSummary / EXOClusterCull
    nsite = 0
    lastNotCulled = None
    for cc in ED.GetChargeClusterArray():
      if sqrt(cc.fX**2 + cc.fY**2) > 183:
        continue
      nsite += 1
      lastNotCulled = cc
    if nsite != 1:
      return nsite
    channels = set()
    for i in range(cc.GetNumUWireSignals()):
      channels.add(cc.GetUWireSignalAt(i).fChannel)
    if len(channels) > 2:
      return 2
    return 1

def GetEnergy(cc,ED):
  if ED.fEventHeader.fIsMonteCarloEvent:
    uncalibratedEnergy = cc.fRawEnergy
    energyCal = calib.getCalib("energy-calib-mc","vanilla",ED.fEventHeader)
    energy = energyCal.CalibratedChargeEnergy(uncalibratedEnergy,1)
  else:
    uncalibratedEnergy = cc.fPurityCorrectedEnergy
    energyCal = ROOT.EXOEnergyCalib.GetInstanceForFlavor("vanilla","vanilla","vanilla")
    energy = energyCal.CalibratedChargeEnergy(uncalibratedEnergy,1,ED.fEventHeader)
  return energy

if __name__ == "__main__":
  ROOT.gSystem.Load("libEXOCalibUtilities")

  calib = ROOT.EXOCalibManager.GetCalibManager()
  calib.SetMetadataAccessType("mysql")
  calib.SetPort(3306)
  calib.SetUser("rd_exo_cond_ro")
  calib.SetHost("mysql-node03.slac.stanford.edu")

  chain = ROOT.TChain("tree")
  if len(sys.argv) == 1:
    ds = ROOT.EXORunInfoManager.GetDataSet("Data/Processed/processed","quality==\"GOLDEN\"&&run>=2464&&run<=3564")
    for run in ds:
      for f in run.GetRunFiles():
        print(f.GetFileLocation())
        chain.Add(f.GetFileLocation())
  else:
    for f in sys.argv[1:]:
      chain.Add(f)
  main(chain)
