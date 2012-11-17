import ROOT,sys

def main(files,nbins,rng,zCut,energyThresh):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  binstring = str(nbins)
  histFull = ROOT.TH1D("histFull","per-event rate of missing the 2D position of at least one CC above "+str(energyThresh)+" keV",nbins,0,rng)
  histFull.GetXaxis().SetTitle("Energy of largest cluster in event (keV)")
  hist = ROOT.TH1D("hist","per-event rate of missing the 2D position of at least one CC above "+str(energyThresh)+" keV",nbins,0,rng)
  hist.GetXaxis().SetTitle("Energy of largest cluster in event (keV)")
  hist.SetLineColor(ROOT.kRed)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    AllClustered = True
    MaxEnergy = 0.0
    ncl = ED.GetNumChargeClusters()
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fZ) > zCut:
        continue
      if cc.fCorrectedEnergy > MaxEnergy:
        MaxEnergy = cc.fCorrectedEnergy
      if abs(cc.fX) > 172 and cc.fRawEnergy > energyThresh:
        AllClustered = False
    if MaxEnergy > 0:
      histFull.Fill(MaxEnergy)
      if not AllClustered:
        hist.Fill(MaxEnergy)


  c1 = ROOT.TCanvas("c1")
  histFull.Draw()
  hist.Draw("same")
  raw_input("hit enter to continue")
  histFull.Sumw2()
  hist.Sumw2()
  h = ROOT.TH1D(histFull)
  h.Divide(hist,histFull,1,1,"B")
  h.Draw("E")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the histogram? (Y/N)")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    h.Write(key)
    outfile.Close()

if __name__ == "__main__":
  if len(sys.argv) < 6:
    print("usage: " + sys.argv[0] + " nbins range zCut energyThreshold file(s)")
    sys.exit(1)
  main(sys.argv[5:],int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]))
