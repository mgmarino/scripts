import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  t.Draw("@fChargeClusters.size()>>hist(10,0,10)")
  hist = ROOT.gDirectory.Get("hist")
  hist.SetTitle("Number of Charge clusters per event")
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
    hist.Write(key)
  histWithEnergy = ROOT.TH1I("histWithEnergy","Number of Charge clusters with energy > 0 per event",10,0,10)
  t.GetEntry(0)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nclWithEnergy = len(filter(lambda energy: energy>0, [ED.GetChargeCluster(j).fRawEnergy for j in range(ED.GetNumChargeClusters())]))
    histWithEnergy.Fill(nclWithEnergy)
  histWithEnergy.Draw()
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
    histWithEnergy.Write(key)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
