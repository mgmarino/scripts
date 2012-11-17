import ROOT,sys

def main(files,nbins,rng):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  hist = ROOT.TH1D("hist","Average Multiplicity",nbins,0,rng)
  hist.GetXaxis().SetTitle("Total event energy")
  histCount = ROOT.TH1D("histCount","Average Multiplicity",nbins,0,rng)

  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    ncl = ED.GetNumChargeClusters()
    nclWithEnergy = 0
    sumEnergy = 0.
    for j in range(ncl):
      cc = ED.GetChargeCluster(j)
      sumEnergy += cc.fCorrectedEnergy
      if cc.fRawEnergy > 0.000001:
        nclWithEnergy += 1
    for j in range(nclWithEnergy):
      hist.Fill(sumEnergy)
    if nclWithEnergy:
      histCount.Fill(sumEnergy)

  hist.Divide(histCount)
  hist.Draw("E")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print("usage: "+sys.argv[0]+" nbins range file(s)")
    sys.exit(1)
  main(sys.argv[3:],int(sys.argv[1]),int(sys.argv[2]))
