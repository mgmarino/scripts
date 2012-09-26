#########################################################################
# 
# This script calculates the minimum distance of a found charge cluster
# to a Pixelated charge deposit.
#
#########################################################################

import sys,ROOT
from math import sqrt

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  histMinDist = ROOT.TH1D("histMinDist","Distances",400,0,400)
  histMinDist.GetXaxis().SetTitle("Distance to nearest PCD (mm)")
  histDistEnergy = ROOT.TH2D("histDistEnergy","Distances vs Energy",100,0,4000,200,0,400)
  histDistEnergy.GetXaxis().SetTitle("Energy")
  histDistEnergy.GetYaxis().SetTitle("Distance to nearest PCD (mm)")

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    ncl = ED.GetNumChargeClusters()
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      mindist = 399.
      for k in range(npcds):
        pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(k)
        pcdX = pcd.GetPixelCenter().GetX()
        pcdY = pcd.GetPixelCenter().GetY()
        dist = sqrt((pcdX - cc.fX)**2 + (pcdY - cc.fY)**2)
        if dist < mindist:
          mindist = dist
      histMinDist.Fill(mindist)
      histDistEnergy.Fill(cc.fRawEnergy,mindist)
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