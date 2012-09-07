import sys,ROOT
from math import sqrt

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  f = ROOT.TFile(filename)
  t = f.Get("tree")
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  histMinDist = ROOT.TH1D("histMinDist","Distances",400,0,400)
  histDistEnergy = ROOT.TH2D("histDistEnergy","Distances vs Energy",100,0,4000,200,0,400)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    ncl = ED.GetNumChargeClusters()
    for j in range(npcds):
      pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(j)
      pcdX = pcd.GetPixelCenter().GetX()
      pcdY = pcd.GetPixelCenter().GetY()
      mindist = 399.
      for k in range(ncl):
        cc = ED.GetChargeCluster(k)
        dist = sqrt((pcdX - cc.fX)**2 + (pcdY - cc.fY)**2)
        if dist < mindist:
          mindist = dist
      histMinDist.Fill(mindist)
      histDistEnergy.Fill(pcd.fTotalEnergy*1000.,mindist)
  c1 = ROOT.TCanvas()
  c1.Divide(2)
  c1.cd(1)
  histMinDist.Draw()
  c1.cd(2)
  histDistEnergy.Draw("colz")
  raw_input("hit enter to quit")


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
