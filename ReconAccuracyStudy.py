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
  U = array('d',[0])
  V = array('d',[0])
  X = array('d',[0])
  Y = array('d',[0])
  Z = array('d',[0])
  pcdEnergy = array('d',[0])
  nearestCCEnergy = array('d',[0])
  dU = array('d',[0])
  dV = array('d',[0])
  dZ = array('d',[0])
  outTree = ROOT.TTree("AccuracyTree","AccuracyTree")
  outTree.Branch("U",U,"U/D")
  outTree.Branch("V",V,"V/D")
  outTree.Branch("X",X,"X/D")
  outTree.Branch("Y",Y,"Y/D")
  outTree.Branch("Z",Z,"Z/D")
  outTree.Branch("pcdEnergy",pcdEnergy,"pcdEnergy/D")
  outTree.Branch("nearestCCEnergy",nearestCCEnergy,"nearestCCEnergy/D")
  outTree.Branch("dU",dU,"dU/D")
  outTree.Branch("dV",dV,"dV/D")
  outTree.Branch("dZ",dZ,"dZ/D")

  ED = ROOT.EXOEventData()
  intree.SetBranchAddress("EventBranch",ED)
  for i in range(intree.GetEntries()):
    intree.GetEntry(i)
    ncc = ED.GetNumChargeClusters()
    npcd = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
      nearestCC = None
      nearestDist = 999999.
      for cc in ED.GetChargeClusterArray():
        distance = Get3DDistance(cc,pcd)
        if distance < nearestDist:
          nearestDist = distance
          nearestCC = cc
      pixel = pcd.GetPixelCenter()
      U[0] = pixel.GetU()
      V[0] = pixel.GetV()
      X[0] = pixel.GetX()
      Y[0] = pixel.GetY()
      Z[0] = pixel.GetZ()
      pcdEnergy[0] = pcd.fTotalEnergy*1000
      if nearestCC:
        nearestCCEnergy[0] = nearestCC.fRawEnergy
        dU[0] = nearestCC.fU - U[0]
        dV[0] = nearestCC.fV - V[0]
        dZ[0] = nearestCC.fZ - Z[0]
      else:
        nearestCCEnergy[0] = -999
        dU[0] = 999
        dV[0] = 999
        dZ[0] = 999
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
