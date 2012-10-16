import ROOT,sys

def main(oldfiles,newfiles):
  ROOT.gSystem.Load("libEXOUtilities")
  tOld = ROOT.TChain("tree")
  tOld.Add(oldfiles)
  tNew = ROOT.TChain("tree")
  tNew.Add(newfiles)
  if tOld.GetEntries() != tNew.GetEntries():
    print("Error, old / new number of events differ! (" + str(tOld.GetEntries()) + "/" + str(tNew.GetEntries()) + ")")
    sys.exit(1)

  hOldMore = ROOT.TH2D("hOldMore","hOldMore",100,-300,300,100,-200,200)
  hNewMore = ROOT.TH2D("hNewMore","hNewMore",100,-300,300,100,-200,200)
  hTimeDiffToNearestCCall = ROOT.TH1D("hTimeDiffToNearestCCall","hTimeDiffToNearestCCall",100,-20,20)
  hTimeDiffToNearestCC = ROOT.TH1D("hTimeDiffToNearestCC","hTimeDiffToNearestCC",100,-20,20)
  hTimeDiffToNearestCC.SetLineColor(ROOT.kRed)
  hTimeDiffToNearestV = ROOT.TH1D("hTimeDiffToNearestV","hTimeDiffToNearestV",100,-20,20)
  hUVenergy = ROOT.TH2D("hUVenergy","hUVenergy",100,0,3000,100,0,600)
  edOld = ROOT.EXOEventData()
  edNew = ROOT.EXOEventData()
  tOld.SetBranchAddress("EventBranch",edOld)
  tNew.SetBranchAddress("EventBranch",edNew)
  for i in range(tOld.GetEntries()):
    tOld.GetEntry(i)
    tNew.GetEntry(i)
    #print("Processing event " + str(edOld.fEventNumber))
    nscOld = edOld.GetNumScintillationClusters()
    nscNew = edOld.GetNumScintillationClusters()
    if nscOld != nscNew:
      print("Warning, old / new nsc differ! (" + str(nscOld) + "/" + str(nscNew) + ")")
      continue
    if nscOld != 1:
      continue
    CCInWindowOld = []
    CCInWindowNew = []
    nclOld = edOld.GetNumChargeClusters()
    nclNew = edNew.GetNumChargeClusters()
    for j in range(nclOld):
      cc = edOld.GetChargeCluster(j)
      if InsideHexAndWindow(cc):
        CCInWindowOld.append(j)
        minTimeDiff = 30000.
        for k in range(edOld.GetNumChargeClusters()):
          if k == j:
            continue
          cc2 = edOld.GetChargeCluster(k)
          if not OnSameTPC(cc,cc2):
            continue
          diff = cc.fCollectionTime - cc2.fCollectionTime
          if abs(diff) < abs(minTimeDiff):
            minTimeDiff = diff
        hTimeDiffToNearestCCall.Fill(minTimeDiff/1000.)
    for j in range(nclNew):
      cc = edNew.GetChargeCluster(j)
      if InsideHexAndWindow(cc):
        CCInWindowNew.append(j)
    if len(CCInWindowOld) != len(CCInWindowNew):
      uenergy, venergy = 0.,0.
      for j in range(edNew.GetNumUWireSignals()):
        uenergy += edNew.GetUWireSignal(j).fCorrectedEnergy
      for j in range(edNew.GetNumVWireSignals()):
        venergy += edNew.GetVWireSignal(j).fCorrectedMagnitude
      hUVenergy.Fill(uenergy,venergy)
      for j in CCInWindowOld:
        cc = edOld.GetChargeCluster(j)
        hOldMore.Fill(cc.fX,cc.fY)
        minTimeDiff = 30000.
        for k in range(edOld.GetNumChargeClusters()):
          if k == j:
            continue
          cc2 = edOld.GetChargeCluster(k)
          if not OnSameTPC(cc,cc2):
            continue
          diff = cc.fCollectionTime - cc2.fCollectionTime
          if abs(diff) < abs(minTimeDiff):
            minTimeDiff = diff
        hTimeDiffToNearestCC.Fill(minTimeDiff/1000.)
        for k in range(edNew.GetNumChargeClusters()):
          ccNew = edNew.GetChargeCluster(k)
          if abs(ccNew.fPurityCorrectedEnergy - cc.fPurityCorrectedEnergy) < 1:
            #print("Think I found corresponding New cluster. The positions are:")
            #print("  posOld = " + str(cc.fX) + " " + str(cc.fY) + " " + str(cc.fZ) + ", energy = " + str(cc.fPurityCorrectedEnergy))
            #print("  posNew = " + str(ccNew.fX) + " " + str(ccNew.fY) + " " + str(ccNew.fZ) + ", energy = " + str(cc.fPurityCorrectedEnergy))
            break
        minVtimeDiff = 30000
        for k in range(edNew.GetNumVWireSignals()):
          vws = edNew.GetVWireSignal(k)
          diff = ccNew.fCollectionTime - vws.fTime
          if abs(diff) < abs(minVtimeDiff):
            minVtimeDiff = diff
        hTimeDiffToNearestV.Fill(minVtimeDiff/1000.)
        
        #print("  posCC " + str(j) + " = " + str(cc.fX) + " " + str(cc.fY) + " " + str(cc.fZ) + ", energy = " + str(cc.fPurityCorrectedEnergy))
      #print("position of new ccs in window:")
      for j in CCInWindowNew:
        cc = edNew.GetChargeCluster(j)
        hNewMore.Fill(cc.fX,cc.fY)
        #print("  posCC " + str(j) + " = " + str(cc.fX) + " " + str(cc.fY) + " " + str(cc.fZ) + ", energy = " + str(cc.fPurityCorrectedEnergy))
      #print("")
  c1 = ROOT.TCanvas("c1")
  hOldMore.Draw("colz")
  c2 = ROOT.TCanvas("c2")
  hNewMore.Draw("colz")
  c3 = ROOT.TCanvas("c3")
  hTimeDiffToNearestCCall.Draw()
  hTimeDiffToNearestCC.Draw("same")
  c4 = ROOT.TCanvas("c4")
  hTimeDiffToNearestV.Draw()
  c5 = ROOT.TCanvas("c5")
  hUVenergy.Draw("colz")
  raw_input("quit")

def InsideHexAndWindow(cc):
  if abs(cc.fZ) > 185 or abs(cc.fX) > 176:
    return False
  if cc.fPurityCorrectedEnergy > 1000 and cc.fPurityCorrectedEnergy < 3000:
    return True
  return False

def OnSameTPC(cc1,cc2):
  return ROOT.EXOMiscUtil.OnSameDetectorHalf(cc1.GetUWireSignalAt(0).fChannel,cc2.GetUWireSignalAt(0).fChannel)

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " oldfile newfile")
    sys.exit(1)
  main(sys.argv[1],sys.argv[2])
