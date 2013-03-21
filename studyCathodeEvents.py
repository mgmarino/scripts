from __future__ import with_statement
from math import sqrt
import ROOT,sys

def main(tree,outfile):
  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)
  histDUcombined = ROOT.TH1D("histDUcombined","#Delta U combined charge clusters (north - south)",800,-200,200)
  histDUcombined.GetXaxis().SetTitle("#Delta U (mm)")
  histDVcombined = ROOT.TH1D("histDVcombined","#Delta V combined charge clusters (north - south)",800,-200,200)
  histDVcombined.GetXaxis().SetTitle("#Delta V (mm)")
  histDUVcombined = ROOT.TH1D("histDUVcombined","U(TPC1) - V(TPC2) combined charge clusters",800,-200,200)
  histDUVcombined.GetXaxis().SetTitle("#Delta UV (mm)")
  histDVUcombined = ROOT.TH1D("histDVUcombined","V(TPC1) - U(TPC2) combined charge clusters",800,-200,200)
  histDVUcombined.GetXaxis().SetTitle("#Delta VU (mm)")
  histDXcombined = ROOT.TH1D("histDXcombined","#Delta X combined charge clusters (north - south)",800,-200,200)
  histDXcombined.GetXaxis().SetTitle("#Delta X (mm)")
  histDYcombined = ROOT.TH1D("histDYcombined","#Delta Y combined charge clusters (north - south)",800,-200,200)
  histDYcombined.GetXaxis().SetTitle("#Delta Y (mm)")
  histDUuncombined = ROOT.TH1D("histDUuncombined","#Delta U uncombined charge clusters (north - south)",800,-200,200)
  histDUuncombined.GetXaxis().SetTitle("#Delta U (mm)")
  histDVuncombined = ROOT.TH1D("histDVuncombined","#Delta V uncombined charge clusters (north - south)",800,-200,200)
  histDVuncombined.GetXaxis().SetTitle("#Delta V (mm)")
  histDUVuncombined = ROOT.TH1D("histDUVuncombined","U(TPC1) - V(TPC2) uncombined charge clusters",800,-200,200)
  histDUVuncombined.GetXaxis().SetTitle("#Delta UV (mm)")
  histDVUuncombined = ROOT.TH1D("histDVUuncombined","V(TPC1) - U(TPC2) uncombined charge clusters",800,-200,200)
  histDVUuncombined.GetXaxis().SetTitle("#Delta VU (mm)")
  histDXuncombined = ROOT.TH1D("histDXuncombined","#Delta X uncombined charge clusters (north - south)",800,-200,200)
  histDXuncombined.GetXaxis().SetTitle("#Delta X (mm)")
  histDYuncombined = ROOT.TH1D("histDYuncombined","#Delta Y uncombined charge clusters (north - south)",800,-200,200)
  histDYuncombined.GetXaxis().SetTitle("#Delta Y (mm)")
  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    for cc in ED.GetChargeClusterArray():
      if cc.fDetectorHalf > 1 :
        print("Combined cc in run/event "+str(ED.fRunNumber)+" / "+str(ED.fEventNumber))
        u1,v1,u2,v2 = GetUVofCombinedCluster(cc)
        if u1:
          x1,y1 = UVtoXY(u1,v1,100)
          x2,y2 = UVtoXY(u2,v2,-100)
          histDUcombined.Fill(u1-u2)
          histDVcombined.Fill(v1-v2)
          histDUVcombined.Fill(u1-v2)
          histDVUcombined.Fill(v1-u2)
          histDXcombined.Fill(x1-x2)
          histDYcombined.Fill(y1-y2)
    cc1,cc2 = FindCathodeClusters(ED)
    if not cc1:
      continue
    #if GetNumChannels(cc1) < 2 and GetNumChannels(cc2) < 2:
    #  continue
    print("Uncombined cc which might be split in run/event "+str(ED.fRunNumber)+" / "+str(ED.fEventNumber))
    histDUuncombined.Fill(cc1.fU-cc2.fU)
    histDVuncombined.Fill(cc1.fV-cc2.fV)
    histDUVuncombined.Fill(cc1.fU-cc2.fV)
    histDVUuncombined.Fill(cc1.fV-cc2.fU)
    histDXuncombined.Fill(cc1.fX-cc2.fX)
    histDYuncombined.Fill(cc1.fY-cc2.fY)

  f = ROOT.TFile(outfile,"RECREATE")
  histDUcombined.Write()
  histDVcombined.Write()
  histDUVcombined.Write()
  histDVUcombined.Write()
  histDXcombined.Write()
  histDYcombined.Write()
  histDUuncombined.Write()
  histDVuncombined.Write()
  histDUVuncombined.Write()
  histDVUuncombined.Write()
  histDXuncombined.Write()
  histDYuncombined.Write()
  f.Close()

def GetNumChannels(cc):
  chans = set()
  if type(cc) == ROOT.EXOChargeCluster:
    for i in range(cc.GetNumUWireSignals()):
      chans.add(cc.GetUWireSignalChannelAt(i))
  else:
    for uws in cc:
      chans.add(uws.fChannel)
  return len(chans)

def FindCathodeClusters(ED):
  if ED.GetNumScintillationClusters() != 1:
    return None,None
  for i in range(ED.GetNumChargeClusters()):
    cc1 = ED.GetChargeCluster(i)
    if cc1.fCorrectedEnergy < 1:
      continue
    if abs(cc1.fZ) > 5:
      continue
    for j in range(i+1,ED.GetNumChargeClusters()):
      cc2 = ED.GetChargeCluster(j)
      if cc2.fCorrectedEnergy < 1:
        continue
      if abs(cc2.fZ) > 5:
        continue
      if cc1.fDetectorHalf == cc2.fDetectorHalf:
        continue
      if cc1.fDetectorHalf == 0:
        return cc1,cc2
      else:
        return cc2,cc1
  return None,None

def UVtoXY(u,v,z):
  y = (u+v)/sqrt(3.0)
  if z > 0.0:
    x = v - u
  else:
    x = u - v
  return x,y

def GetUVofCombinedCluster(cc):
  assert(cc.fDetectorHalf > 1)
  uws1 = []
  uws2 = []
  vws1 = []
  vws2 = []
  for i in range(cc.GetNumUWireSignals()):
    uws = cc.GetUWireSignalAt(i)
    if ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel) == ROOT.EXOMiscUtil.kNorth:
      uws1.append(uws)
    else:
      uws2.append(uws)
  #if GetNumChannels(uws1) < 2 and GetNumChannels(uws2) < 2:
  #  return None,None,None,None
  for i in range(cc.GetNumVWireSignals()):
    vws = cc.GetVWireSignalAt(i)
    if ROOT.EXOMiscUtil.GetTPCSide(vws.fChannel) == ROOT.EXOMiscUtil.kNorth:
      vws1.append(vws)
    else:
      vws2.append(vws)
  u1,_ = GetMeanPositionAndEnergyOfSignals(uws1)
  u2,_ = GetMeanPositionAndEnergyOfSignals(uws2)
  v1,_ = GetMeanPositionAndEnergyOfSignals(vws1)
  v2,_ = GetMeanPositionAndEnergyOfSignals(vws2)
  return u1,v1,u2,v2

def GetMeanPositionAndEnergyOfSignals(signals):
  pos = 0
  energy = 0
  for sig in signals:
    if type(sig) == ROOT.EXOUWireSignal:
      e = sig.fCorrectedEnergy
    elif type(sig) == ROOT.EXOVWireSignal:
      e = sig.fCorrectedMagnitude
    else:
      raise TypeError
    pos += ROOT.EXOMiscUtil.GetMeanUorVPositionFromChannel(sig.fChannel) * e
    energy += e
  pos /= energy
  return pos,energy

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: "+sys.argv[0]+" outfile.root filelist.dat")
    print("\nfilelist.dat should contain a list of ROOT files to process")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  with open(sys.argv[2]) as f:
    for line in f:
      t.Add(line[:-1])
  print("Chain contains "+str(t.GetNtrees())+" trees")
  main(t,sys.argv[1])
