#########################################################################
# 
# This script calculates the minimum distance of a found charge cluster
# to a Pixelated charge deposit.
#
#########################################################################

import sys,ROOT
from math import sqrt

def main(zCut, files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  histMinDist = ROOT.TH1D("histMinDist","Distances",400,0,400)
  histMinDist.GetXaxis().SetTitle("Distance to nearest PCD (mm)")
  histDistEnergy = ROOT.TH2D("histDistEnergy","Distances vs Energy",100,0,3000,100,0,100)
  histDistEnergy.GetXaxis().SetTitle("Energy")
  histDistEnergy.GetYaxis().SetTitle("Distance to nearest PCD (mm)")

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    ncl = ED.GetNumChargeClusters()
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fZ) > zCut:
        continue
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
  histMinDist.Scale(1./t.GetEntries())
  histDistEnergy.Scale(1./t.GetEntries())
  c1 = ROOT.TCanvas("c1","c1",1000,600)
  c1.Divide(2)
  pad1 = c1.cd(1)
  pad1.SetLogy(True)
  histMinDist.Draw()
  pad2 = c1.cd(2)
  pad2.SetLogz(True)
  histDistEnergy.Draw("colz")
  raw_input("hit enter to quit")


if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: " + sys.argv[0] + " zCut file(s)")
    sys.exit(1)
  main(float(sys.argv[1]), sys.argv[2:])
