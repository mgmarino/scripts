#########################################################################
# 
# This script finds the nearest (in 3D) charge cluster for each PCD
# and saves the distance to this charge cluster in U, V, and Z and 
# some additional information to a tree.
#
#########################################################################

import sys,ROOT
from math import sqrt
from array import array

def FillTree(intree):
  dU = array('d',[0])
  dV = array('d',[0])
  dU3D = array('d',[0])
  dV3D = array('d',[0])
  dX = array('d',[0])
  dY = array('d',[0])
  dZ = array('d',[0])
  dR = array('d',[0])
  dD = array('d',[0])
  outTree = ROOT.TTree("AccuracyTree","AccuracyTree")
  outTree.Branch("CC",ROOT.EXOChargeCluster())
  outTree.Branch("nearestPCD",ROOT.EXOMCPixelatedChargeDeposit())
  outTree.Branch("nearestUPCD",ROOT.EXOMCPixelatedChargeDeposit())
  outTree.Branch("nearestVPCD",ROOT.EXOMCPixelatedChargeDeposit())
  outTree.Branch("dU",dU,"dU/D")
  outTree.Branch("dV",dV,"dV/D")
  outTree.Branch("dU3D",dU3D,"dU3D/D")
  outTree.Branch("dV3D",dV3D,"dV3D/D")
  outTree.Branch("dX",dX,"dX/D")
  outTree.Branch("dY",dY,"dY/D")
  outTree.Branch("dZ",dZ,"dZ/D")
  outTree.Branch("dR",dR,"dR/D")
  outTree.Branch("dD",dD,"dD/D")

  ED = ROOT.EXOEventData()
  intree.SetBranchAddress("EventBranch",ED)
  for i in range(intree.GetEntries()):
    intree.GetEntry(i)
    ncc = ED.GetNumChargeClusters()
    npcd = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    for cc in ED.GetChargeClusterArray():
      nearestPCD = None
      nearestDist = 999999.
      for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
        distance = Get3DDistance(cc,pcd)
        if distance < nearestDist:
          nearestDist = distance
          nearestPCD = pcd 
      if nearestPCD:
        pixel = nearestPCD.GetPixelCenter()
        dU3D[0] = cc.fU - pixel.GetU()
        dV3D[0] = cc.fV - pixel.GetV()
        dX[0] = cc.fX - pixel.GetX()
        dY[0] = cc.fY - pixel.GetY()
        dZ[0] = cc.fZ - pixel.GetZ()
        dR[0] = sqrt(dX[0]**2 + dY[0]**2)
        dD[0] = nearestDist
      else:
        nearestPCD = ROOT.EXOMCPixelatedChargeDeposit()
        dU3D[0] = 999
        dV3D[0] = 999
        dX[0] = 999
        dY[0] = 999
        dZ[0] = 999
        dR[0] = 999
        dD[0] = 999

      nearestUPCD = None
      nearestUDist = 999999.
      for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
        pixel = pcd.GetPixelCenter()
        distance = cc.fU - pixel.GetU()
        if abs(distance) < abs(nearestUDist):
          nearestUDist = distance
          nearestUPCD = pcd 
      if nearestUPCD:
        dU[0] = nearestUDist
      else:
        nearestUPCD = ROOT.EXOMCPixelatedChargeDeposit()
        dU[0] = 999
      
      nearestVPCD = None
      nearestVDist = 999999.
      for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
        pixel = pcd.GetPixelCenter()
        distance = cc.fV - pixel.GetV()
        if abs(distance) < abs(nearestVDist):
          nearestVDist = distance
          nearestVPCD = pcd 
      if nearestVPCD:
        dV[0] = nearestVDist
      else:
        nearestVPCD = ROOT.EXOMCPixelatedChargeDeposit()
        dV[0] = 999

      outTree.SetBranchAddress("CC",cc)
      outTree.SetBranchAddress("nearestPCD",nearestPCD)
      outTree.SetBranchAddress("nearestUPCD",nearestUPCD)
      outTree.SetBranchAddress("nearestVPCD",nearestVPCD)
      outTree.Fill()

  return outTree

def Get3DDistance(cc,pcd):
  pixel = pcd.GetPixelCenter()
  dX = cc.fX - pixel.GetX()
  dY = cc.fY - pixel.GetY()
  dZ = cc.fZ - pixel.GetZ()
  return sqrt(dX**2 + dY**2 + dZ**2)

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: "+sys.argv[0]+" outfile infile[s]")
    sys.exit(1)
  inTree = ROOT.TChain("tree")
  for f in sys.argv[2:]:
    inTree.Add(f)
  outFile = ROOT.TFile(sys.argv[1],"NEW")
  if not outFile.IsOpen():
    print("Could not open outfile, does it already exist?")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  outTree = FillTree(inTree)
  outFile.cd()
  outTree.Write()
