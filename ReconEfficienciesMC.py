import ROOT,sys

def main(tree):
  hAll = ROOT.TH1D("hAll","hAll",100,0,3000)
  hAllZcut = ROOT.TH1D("hAllZcut","hAllZcut",100,0,3000)
  hScintgood = ROOT.TH1D("hScintgood","hScintgood",100,0,3000)
  hScintgoodZcut = ROOT.TH1D("hScintgoodZcut","hScintgoodZcut",100,0,3000)
  hUgood = ROOT.TH1D("hUgood","hUgood",100,0,3000)
  hUgoodZcut = ROOT.TH1D("hUgoodZcut","hUgoodZcut",100,0,3000)
  hVgood = ROOT.TH1D("hVgood","hVgood",100,0,3000)
  hVgoodZcut = ROOT.TH1D("hVgoodZcut","hVgoodZcut",100,0,3000)

  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)

  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    if not AllPixelsInsideHexagon(ED):
      continue
    energy = GetTrueEnergy(ED)
    hAll.Fill(energy)
    if AllPixelsInsideZCut(ED):
      insideZcut = True
      hAllZcut.Fill(energy)
    else:
      insideZcut = False
    if ED.GetNumScintillationClusters() > 0:
      hScintgood.Fill(energy)
      if insideZcut:
        hScintgoodZcut.Fill(energy)
    if ED.GetNumUWireSignals() > 0:
      hUgood.Fill(energy)
      if insideZcut:
        hUgoodZcut.Fill(energy)
    if ED.GetNumVWireSignals() > 0:
      hVgood.Fill(energy)
      if insideZcut:
        hVgoodZcut.Fill(energy)
  #hAll.Draw()
  #raw_input("c")
  #hScintgood.Draw()
  #raw_input("c")
  #hUgood.Draw()
  #raw_input("c")
  #hVgood.Draw()
  #raw_input("c")
  #hVgoodZcut.Draw()
  #raw_input("q")
  hScintEff = ROOT.TGraphAsymmErrors(hScintgood,hAll)
  hScintEff.SetName("rateScint")
  hScintEffZcut = ROOT.TGraphAsymmErrors(hScintgoodZcut,hAllZcut)
  hScintEffZcut.SetName("rateScintZcut")
  hUeff = ROOT.TGraphAsymmErrors(hUgood,hAll)
  hUeff.SetName("rateU")
  hUeffZcut = ROOT.TGraphAsymmErrors(hUgoodZcut,hAllZcut)
  hUeffZcut.SetName("rateUZcut")
  hVeff = ROOT.TGraphAsymmErrors(hVgood,hAll)
  hVeff.SetName("rateV")
  hVeffZcut = ROOT.TGraphAsymmErrors(hVgoodZcut,hAllZcut)
  hVeffZcut.SetName("rateVZcut")
  f = ROOT.TFile("ReconEfficienciesMC.root","RECREATE")
  hScintEff.Write()
  hScintEffZcut.Write()
  hUeff.Write()
  hUeffZcut.Write()
  hVeff.Write()
  hVeffZcut.Write()
  f.Close()

def AllPixelsInsideHexagon(ED):
  crossing = ROOT.EXOWireCrossing.GetInstance()
  for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
    if crossing.GetDistanceFromHexagon(pcd.GetPixelCenter()) > 0:
      return False
  return True

def AllPixelsInsideZCut(ED):
  for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
    if abs(pcd.GetPixelCenter().GetZ()) > 182:
      return False
  return True

def GetTrueEnergy(ED):
  energy = 0.0
  for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
    energy += pcd.fTotalEnergy
  return energy*1000

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: "+sys.argv[0]+" file[s]")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  chain = ROOT.TChain("tree")
  for f in sys.argv[1:]:
    chain.Add(f)
  main(chain)
