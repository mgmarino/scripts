#########################################################################
# 
# This script calculates the minimum 3D distance of a found charge cluster
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

  histMinDist = ROOT.TH1D("histMinDist","Position reconstruction uncertainty in R",200,0,100)
  histMinDist.GetXaxis().SetTitle("Radial distance to nearest PCD (mm)")
  histMinDistZ = ROOT.TH1D("histMinDistZ","Position reconstruction uncertainty in Z",200,0,100)
  histMinDistZ.GetXaxis().SetTitle("Axial distance to nearest PCD (mm)")
  histMinDistZGoodR = ROOT.TH1D("histMinDistZGoodR","Position reconstruction uncertainty in Z [has 2D pos]",200,0,100)
  histMinDistZGoodR.GetXaxis().SetTitle("Axial distance to nearest PCD (mm)")
  histDistEnergy = ROOT.TH2D("histDistEnergy","R Position uncertainty vs Energy",100,0,3000,100,0,100)
  histDistEnergy.GetXaxis().SetTitle("Energy")
  histDistEnergy.GetYaxis().SetTitle("Radial distance to nearest PCD (mm)")
  histDistZEnergy = ROOT.TH2D("histDistZEnergy","Z Position uncertainty vs Energy",100,0,3000,100,0,100)
  histDistZEnergy.GetXaxis().SetTitle("Energy")
  histDistZEnergy.GetYaxis().SetTitle("Axial distance to nearest PCD (mm)")
  histDistZEnergyGoodR = ROOT.TH2D("histDistZEnergyGoodR","Z Position uncertainty vs Energy [has 2D pos]",100,0,3000,100,0,100)
  histDistZEnergyGoodR.GetXaxis().SetTitle("Energy")
  histDistZEnergyGoodR.GetYaxis().SetTitle("Axial distance to nearest PCD (mm)")

  histBlob = ROOT.TH1D("histBlob","histBlob",100,-200,200)
  histBlob2D = ROOT.TH2D("histBlob2D","histBlob2D",100,-300,300,100,-200,200)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    ncl = ED.GetNumChargeClusters()
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fZ) > zCut:
        continue
      mindist = 999.
      mindistZ = 999.
      for k in range(npcds):
        pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(k)
        pcdX = pcd.GetPixelCenter().GetX()
        pcdY = pcd.GetPixelCenter().GetY()
        pcdZ = pcd.GetPixelCenter().GetZ()
        dist = sqrt((pcdX - cc.fX)**2 + (pcdY - cc.fY)**2)
        distZ = abs(pcdZ - cc.fZ)
        if dist < mindist:
          mindist = dist
          minpixel = pcd
        if distZ < mindistZ:
          mindistZ = distZ
          minpixelZ = pcd
      histMinDist.Fill(mindist)
      histMinDistZ.Fill(mindistZ)
      if abs(cc.fX) < 400:
        histMinDistZGoodR.Fill(mindistZ)
        histDistZEnergyGoodR.Fill(cc.fRawEnergy,mindistZ)
      histDistEnergy.Fill(cc.fRawEnergy,mindist)
      histDistZEnergy.Fill(cc.fRawEnergy,mindistZ)
      if cc.fRawEnergy > 150 and mindistZ < 100 and mindistZ > 15:
        #print(minpixelZ.GetPixelCenter().GetZ())
        #histBlob.Fill(minpixel.GetPixelCenter().GetZ())
        #histBlob2D.Fill(minpixel.GetPixelCenter().GetX(),minpixel.GetPixelCenter().GetY())
        histBlob.Fill(cc.fZ)
        histBlob2D.Fill(cc.fX,cc.fY)
  histMinDist.Scale(1./t.GetEntries())
  histMinDistZ.Scale(1./t.GetEntries())
  histMinDistZGoodR.Scale(1./t.GetEntries())
  histDistEnergy.Scale(1./t.GetEntries())
  histDistZEnergy.Scale(1./t.GetEntries())
  histDistZEnergyGoodR.Scale(1./t.GetEntries())

  c1 = ROOT.TCanvas("c1","R",1000,600)
  c1.Divide(2)
  pad1 = c1.cd(1)
  pad1.SetLogy(True)
  histMinDist.Draw()
  pad2 = c1.cd(2)
  pad2.SetLogz(True)
  histDistEnergy.Draw("colz")

  c2 = ROOT.TCanvas("c2","Z",1000,600)
  c2.Divide(2)
  pad1 = c2.cd(1)
  pad1.SetLogy(True)
  histMinDistZ.Draw()
  pad2 = c2.cd(2)
  pad2.SetLogz(True)
  histDistZEnergy.Draw("colz")

  c3 = ROOT.TCanvas("c3","Z good R",1000,600)
  c3.Divide(2)
  pad1 = c3.cd(1)
  pad1.SetLogy(True)
  histMinDistZGoodR.Draw()
  pad2 = c3.cd(2)
  pad2.SetLogz(True)
  histDistZEnergyGoodR.Draw("colz")

  c4 = ROOT.TCanvas("c4","c4")
  histBlob.Draw()
  #histBlob2D.Draw("colz")

  raw_input("hit enter to save and quit")
  #c1.SaveAs("Radius.C")
  #c2.SaveAs("Axial.C")
  #c3.SaveAs("AxialGoodR.C")

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: " + sys.argv[0] + " zCut file(s)")
    sys.exit(1)
  main(float(sys.argv[1]), sys.argv[2:])
