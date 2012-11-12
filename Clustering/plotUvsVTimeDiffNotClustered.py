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

  hist7 = ROOT.TH1D("hist7","hist7",400,-20,20)
  hist7.GetXaxis().SetTitle("Time of largest U - V-time")

  hist8 = ROOT.TH2D("hist8","Energy of unclustered clusters",100,0,3000,100,0,800)
  hist8.GetXaxis().SetTitle("Deposition Energy")
  hist8.GetYaxis().SetTitle("Induction Energy")

  hist9 = ROOT.TH1D("hist9","Time diff of high-U low-V clusters with |Z| < 160",400,-20,20)
  hist9.GetXaxis().SetTitle("U-time - V-time")

  hist10 = ROOT.TH1D("hist10","Z of high-U low-V clusters",200,-200,200)
  hist10.GetXaxis().SetTitle("Z")
  
  t = ROOT.TChain("tree")
  for f in filenames:
    t.Add(f)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    maxE = 0
    UonlyClusters = []
    VonlyClusters = []
    largestCC = None
    for j in range(ED.GetNumChargeClusters()):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fRawEnergy) < 0.000001:
        VonlyClusters.append(cc)
      elif abs(cc.fAmplitudeInVChannels) < 0.000001:
        UonlyClusters.append(cc)
        if cc.fCorrectedEnergy > maxE:
          maxE = cc.fCorrectedEnergy
          largestCC = cc

    for vc in VonlyClusters:
        if(largestCC):
          timediff = (largestCC.fCollectionTime - vc.fCollectionTime) / 1000
          hist7.Fill(timediff)

    for uc in UonlyClusters:
      for vc in VonlyClusters:
        timediff = (uc.fCollectionTime - vc.fCollectionTime) / 1000
        hist.Fill(timediff)
        hist2.Fill(uc.fCorrectedEnergy,timediff)
        hist3.Fill(uc.fZ,timediff)
        hist4.Fill(vc.GetNumVWireSignals(),timediff)
        hist5.Fill(vc.fCorrectedAmplitudeInVChannels,timediff)
        nvws = vc.GetNumVWireSignals()
        channel = 0
        for j in range(nvws):
          channel += vc.GetVWireSignalAt(j).fChannel
        channel /= nvws
        hist6.Fill(channel,timediff)
        hist8.Fill(uc.fCorrectedEnergy,vc.fCorrectedAmplitudeInVChannels)
        if uc.fCorrectedEnergy > 1200 and vc.fCorrectedAmplitudeInVChannels < 100:
          if abs(uc.fZ) < 160:
            hist9.Fill(timediff)
          hist10.Fill(uc.fZ)
        if timediff < -2. and timediff > -4.:
          print(ED.fEventNumber)

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
  canvas7 = ROOT.TCanvas("canvas7")
  hist7.Draw()
  canvas8 = ROOT.TCanvas("canvas8")
  hist8.Draw("colz")
  canvas9 = ROOT.TCanvas("canvas9")
  hist9.Draw()
  canvas10 = ROOT.TCanvas("canvas10")
  hist10.Draw()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])

