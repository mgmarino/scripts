import ROOT,sys

def main(tree):
  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)
  hist = ROOT.TH1D("hist","Spectrum of smallest (MS) clusters",300,0,3000)
  hist.GetXaxis().SetTitle("Calibrated (charge) energy (keV)")

  calib = ROOT.EXOCalibManager.GetCalibManager()
  calib.SetMetadataAccessType("mysql")
  calib.SetPort(3306)
  calib.SetUser("rd_exo_cond_ro")
  calib.SetHost("mysql-node03.slac.stanford.edu")

  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    if ED.GetNumScintillationClusters() > 1:
      continue
    if ED.fEventHeader.fTaggedAsMuon:
      continue
    if ED.fEventHeader.fTaggedAsNoise:
      continue
    if ED.GetNumChargeClusters() < 2:
      continue
    smallestE = 9999.
    numEnergy = 0
    for cc in ED.GetChargeClusterArray():
      if ED.fEventHeader.fIsMonteCarloEvent:
        energyCal = calib.getCalib("energy-calib-mc","vanilla",ED.fEventHeader)
        energy = energyCal.CalibratedChargeEnergy(cc.fRawEnergy,1)
      else:
        energyCal = ROOT.EXOEnergyCalib.GetInstanceForFlavor("vanilla","vanilla","vanilla")
        energy = energyCal.CalibratedChargeEnergy(cc.fPurityCorrectedEnergy,1,ED.fEventHeader)
      if energy > 0.01:
        numEnergy += 1
        if energy < smallestE:
          smallestE = energy
    if numEnergy > 1:
      hist.Fill(smallestE)
  f = ROOT.TFile("SmallestClusterSpectrum.root","RECREATE")
  hist.Write()
  f.Close()
  hist.Draw()
  raw_input("q")

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
