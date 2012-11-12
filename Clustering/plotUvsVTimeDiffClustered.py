import ROOT,sys

def main(filenames):
  ROOT.gSystem.Load("libEXOUtilities")

  hist = ROOT.TH1D("hist","hist",400,-20,20)
  hist.GetXaxis().SetTitle("U-time - V-time")

  hist2 = ROOT.TH2D("hist2","",100,0,3000,100,-20,20)
  hist2.GetXaxis().SetTitle("Energy")
  hist2.GetYaxis().SetTitle("U-time - V-time")

  hist3 = ROOT.TH2D("hist3","",100,-200,200,100,-20,20)
  hist3.GetXaxis().SetTitle("Z")
  hist3.GetYaxis().SetTitle("U-time - V-time")

  hist4 = ROOT.TH2D("hist4","",10,0,10,100,-20,20)
  hist4.GetXaxis().SetTitle("# V-signals")
  hist4.GetYaxis().SetTitle("U-time - V-time")

  hist5 = ROOT.TH2D("hist5","",100,0,800,100,-20,20)
  hist5.GetXaxis().SetTitle("V-Energy")
  hist5.GetYaxis().SetTitle("U-time - V-time")

  hist6 = ROOT.TH2D("hist6","",152,0,152,100,-20,20)
  hist6.GetXaxis().SetTitle("Average V-channel")
  hist6.GetYaxis().SetTitle("U-time - V-time")
  
  t = ROOT.TChain("tree")
  for f in filenames:
    t.Add(f)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    Clusters = []
    for j in range(ED.GetNumChargeClusters()):
      cc = ED.GetChargeCluster(j)
      if cc.fRawEnergy > 0 and cc.fAmplitudeInVChannels > 0:
        Clusters.append(cc)

    for uc in Clusters:
      timeOfMaxV = 0
      maxV = 0
      channel = 0
      for j in range(uc.GetNumVWireSignals()):
        vs = uc.GetVWireSignalAt(j)
        channel+= vs.fChannel
        if vs.fCorrectedMagnitude > maxV:
          maxV = vs.fCorrectedMagnitude
          timeOfMaxV = vs.fTime
      channel /= uc.GetNumVWireSignals()
      timediff = (uc.fCollectionTime - timeOfMaxV) / 1000
      hist.Fill(timediff)
      hist2.Fill(uc.fCorrectedEnergy,timediff)
      hist3.Fill(uc.fZ,timediff)
      hist4.Fill(uc.GetNumVWireSignals(),timediff)
      hist5.Fill(uc.fCorrectedAmplitudeInVChannels,timediff)
      hist6.Fill(channel,timediff)

  canvas1 = ROOT.TCanvas("canvas1")
  hist.Draw()
  canvas2 = ROOT.TCanvas("canvas2")
  hist2.Draw("colz")
  canvas3 = ROOT.TCanvas("canvas3")
  hist3.Draw("colz")
  canvas4 = ROOT.TCanvas("canvas4")
  hist4.Draw("colz")
  canvas5 = ROOT.TCanvas("canvas5")
  hist5.Draw("colz")
  canvas6 = ROOT.TCanvas("canvas6")
  hist6.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])

