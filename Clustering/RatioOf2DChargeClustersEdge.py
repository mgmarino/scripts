import ROOT,sys

def main(filename,nbins,rng,zCut):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  binstring = str(nbins)
  histU = ROOT.TH1D("histU","CC 2D reconstruction rate at U-edge",nbins,0,rng)
  histU.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histUall = ROOT.TH1D("histUall","CC 2D reconstruction rate at U-edge",nbins,0,rng)
  histUgood = ROOT.TH1D("histUgood","CC 2D reconstruction rate at U-edge",nbins,0,rng)
  histV = ROOT.TH1D("histV","CC 2D reconstruction rate at V-edge",nbins,0,rng)
  histV.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histVall = ROOT.TH1D("histVall","CC 2D reconstruction rate at V-edge",nbins,0,rng)
  histVgood = ROOT.TH1D("histVgood","CC 2D reconstruction rate at V-edge",nbins,0,rng)
  histX = ROOT.TH1D("histX","CC 2D reconstruction rate (possibly) at X-edge",nbins,0,rng)
  histX.GetXaxis().SetTitle("Charge cluster energy (keV)")
  histXall = ROOT.TH1D("histXall","CC 2D reconstruction rate (possibly) at X-edge",nbins,0,rng)
  histXgood = ROOT.TH1D("histXgood","CC 2D reconstruction rate (possibly) at X-edge",nbins,0,rng)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  uEdges = set([0,37,76,113])
  vEdges = set([38,75,114,151])
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    ncl = ED.GetNumChargeClusters()
    Xedge = PossibleXEdgeEvent(ED)
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fZ) > zCut:
        continue
      uchannels = set([cc.GetUWireSignalChannelAt(k) for k in range(cc.GetNumUWireSignals())])
      vchannels = set([cc.GetVWireSignalChannelAt(k) for k in range(cc.GetNumVWireSignals())])
      if len(uchannels.intersection(uEdges)):
        histUall.Fill(cc.fRawEnergy)
        if abs(cc.fX) < 172:
          histUgood.Fill(cc.fRawEnergy)
      if len(vchannels.intersection(vEdges)):
        histVall.Fill(cc.fRawEnergy)
        if abs(cc.fX) < 172:
          histVgood.Fill(cc.fRawEnergy)
      if Xedge:
        histXall.Fill(cc.fRawEnergy)
        if abs(cc.fX) < 172:
          histXgood.Fill(cc.fRawEnergy)
  histUall.Sumw2()
  histVall.Sumw2()
  histXall.Sumw2()
  histUgood.Sumw2()
  histVgood.Sumw2()
  histXgood.Sumw2()
  histU.Divide(histUgood,histUall,1,1,"B")
  histV.Divide(histVgood,histVall,1,1,"B")
  histX.Divide(histXgood,histXall,1,1,"B")
  histU.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the U-edge histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    histU.Write(key)
    outfile.Close()
  histV.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the V-edge histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    histV.Write(key)
    outfile.Close()
  histX.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the X-edge histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    histX.Write(key)
    outfile.Close()

def GetXEdgeVChannel(uchannel):
  if uchannel >= 114:
    raise ValueError
  elif uchannel >= 76+19:
    return 114 + (uchannel -(76+19))
  elif uchannel >= 76:
    return 114 + 19 + (uchannel - 76)
  elif uchannel >= 38:
    raise ValueError
  elif uchannel >= 19:
    return 38 + (uchannel -19)
  elif uchannel >= 0:
    return 38 + 19 + uchannel
  raise ValueError

def PossibleXEdgeEvent(ED):
  nuws = ED.GetNumUWireSignals()
  nvws = ED.GetNumVWireSignals()
  vchannels = set()
  for i in range(nuws):
    centralV = GetXEdgeVChannel(ED.GetUWireSignal(i).fChannel)
    #vchannels.add(centralV-1)
    vchannels.add(centralV)
    #vchannels.add(centralV+1)
  for i in range(nvws):
    if ED.GetVWireSignal(i).fChannel in vchannels:
      return True
  return False

if __name__ == "__main__":
  if len(sys.argv) != 5:
    print("usage: " + sys.argv[0] + " filename nbins range zCut")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
