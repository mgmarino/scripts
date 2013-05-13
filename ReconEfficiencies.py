import ROOT,sys

def main(tree):
  hScintgoodNorth = ROOT.TH1D("hScintgoodNorth","hScintgoodNorth",100,0,3000)
  hScintallNorth = ROOT.TH1D("hScintallNorth","hScintallNorth",100,0,3000)
  hScintgoodSouth = ROOT.TH1D("hScintgoodSouth","hScintgoodSouth",100,0,3000)
  hScintallSouth = ROOT.TH1D("hScintallSouth","hScintallSouth",100,0,3000)
  hVgood = ROOT.TH1D("hVgood","hVgood",100,0,3000)
  hVall = ROOT.TH1D("hVall","hVall",100,0,3000)
  hVgoodZcut = ROOT.TH1D("hVgoodZcut","hVgoodZcut",100,0,3000)
  hVallZcut = ROOT.TH1D("hVallZcut","hVallZcut",100,0,3000)
  hVgood2D = ROOT.TH2D("hVgood2D","hVgood2D",100,0,3000,38,-171,171)
  hVall2D = ROOT.TH2D("hVall2D","hVall2D",100,0,3000,38,-171,171)
  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)

  calib = ROOT.EXOCalibManager.GetCalibManager()
  calib.SetMetadataAccessType("mysql")
  calib.SetPort(3306)
  calib.SetUser("rd_exo_cond_ro")
  calib.SetHost("mysql-node03.slac.stanford.edu")

  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    if ED.fEventHeader.fTaggedAsNoise:
      continue
    if ED.fSkippedByClustering:
      continue

    ncc,energy,tpc,U,Z,X = GetNumEnergyChargeClusters(ED,calib)
    if ncc == 1:
      if HasVWiresFound(ED):
        hVgood.Fill(energy)
        hVgood2D.Fill(energy,U)
      hVall.Fill(energy)
      hVall2D.Fill(energy,U)
      if abs(Z) < 182:
        if HasVWiresFound(ED):
          hVgoodZcut.Fill(energy)
        hVallZcut.Fill(energy)

    nsc = ED.GetNumScintillationClusters()
    if nsc == 1:
      sc = ED.GetScintillationCluster(0)
      if sc.fRawEnergy < 12000.:
        if tpc == 0:
          hScintgoodNorth.Fill(energy)
          hScintallNorth.Fill(energy)
        elif tpc == 1:
          hScintgoodSouth.Fill(energy)
          hScintallSouth.Fill(energy)
    elif nsc == 0:
      if energy > 700.:
        print("No scint, run "+str(ED.fRunNumber)+", event "+str(ED.fEventNumber)+", energy = "+str(energy))
      if tpc == 0:
        hScintallNorth.Fill(energy)
      elif tpc == 1:
        hScintallSouth.Fill(energy)
  hVeff = ROOT.TGraphAsymmErrors(hVgood,hVall)
  hVeff.SetName("rateV")
  hVeffZcut = ROOT.TGraphAsymmErrors(hVgoodZcut,hVallZcut)
  hVeffZcut.SetName("rateVZcut")
  hScinteffNorth = ROOT.TGraphAsymmErrors(hScintgoodNorth,hScintallNorth)
  hScinteffNorth.SetName("rateScintNorth")
  hScinteffSouth = ROOT.TGraphAsymmErrors(hScintgoodSouth,hScintallSouth)
  hScinteffSouth.SetName("rateScintSouth")
  f = ROOT.TFile("ReconEfficiencies.root","RECREATE")
  hVeff.Write()
  hVeffZcut.Write()
  hScinteffNorth.Write()
  hScinteffSouth.Write()
  hVallZcut.Write()
  hScintallNorth.Write()
  hScintallSouth.Write()
  hV2Deff = ROOT.TH2D(hVall2D)
  hV2Deff.SetName("hV2Deff")
  hV2Deff.Divide(hVgood2D,hVall2D)
  hV2Deff.Write()
  f.Close()

def GetNumEnergyChargeClusters(ED,calib):
  ncc = 0
  energy = 0.0
  tpc = -1
  umax = -1.
  zmax = -1.
  allHave2D = True
  emax = 0.
  for cc in ED.GetChargeClusterArray():
    ccEnergy = cc.fPurityCorrectedEnergy
    if ED.fEventHeader.fIsMonteCarloEvent:
      ccEnergy = cc.fRawEnergy
    energy += ccEnergy
    if ccEnergy > emax:
      emax = ccEnergy
      umax = cc.fU
      zmax = cc.fZ
      xmax = cc.fX
    if cc.fRawEnergy > 0.1:
      if abs(cc.fX) > 200.:
        allHave2D = False
      if tpc == -1:
        tpc = cc.fDetectorHalf
      else:
        if tpc != cc.fDetectorHalf:
          tpc = 2
      ncc += 1
  if ED.fEventHeader.fIsMonteCarloEvent:
    energyCal = calib.getCalib("energy-calib-mc","vanilla",ED.fEventHeader)
    energy = energyCal.CalibratedChargeEnergy(energy,ncc)
  else:
    energyCal = ROOT.EXOEnergyCalib.GetInstanceForFlavor("vanilla","vanilla","vanilla")
    energy = energyCal.CalibratedChargeEnergy(energy,ncc,ED.fEventHeader)
  return ncc,energy,tpc,umax,zmax,allHave2D

def HasVWiresFound(ED):
  if ED.GetNumVWireSignals() > 0:
    return True
  return False

if __name__ == "__main__":
  ROOT.gSystem.Load("libEXOCalibUtilities")
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
