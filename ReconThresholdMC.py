import ROOT,sys

def main(files):
  ROOT.gSystem.Load("libEXOCalibUtilities")
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


def GetTrueSmearedEnergyOfDeposits(ED):
  energy = 0
  for pcd in ED.fMonteCarloData.GetMCPixelatedChargeDepositsArray():
    if pcd.fDepositChannel >= 0
      energy += pcd.fTotalEnergy * 1000.
  return SmearedEnergy(energy)

def SmearedEnergy(energy):
  resCalib = calib.GetCali
  
