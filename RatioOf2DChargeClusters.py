import ROOT,sys

def main(filename,nbins):
  ROOT.gSystem.Load("libEXOUtilities")
  f = ROOT.TFile(filename)
  t = f.Get("tree")
  binstring = str(nbins)
  hist = ROOT.TH1D("hist","V-wire efficiency",nbins,0,3000)
  t.Draw("fChargeClusters.fRawEnergy>>hFull("+binstring+",0,3000)","fChargeClusters.fRawEnergy < 3000","goff")
  t.Draw("fChargeClusters.fRawEnergy>>hGood("+binstring+",0,3000)","fChargeClusters.fRawEnergy < 3000 && fChargeClusters.fAmplitudeInVChannels > 0","goff")
  hFull = ROOT.gDirectory.Get("hFull")
  hGood = ROOT.gDirectory.Get("hGood")
  hFull.Sumw2()
  hGood.Sumw2()
  hist.Divide(hGood,hFull,1,1,"B")
  hist.Draw("E")
  answer = ""
  while not contains(answer,["Y","y","N","n"]):
    answer = raw_input("Do you want to save the histogram? (Y/N)")
  if contains(answer,["Y","y"]):
    out = raw_input("Please enter filename: ")
    outfile = ROOT.TFile(out,"RECREATE")
    hist.Write()

def contains(str, set):
  for c in set:
    if c == str:
      return True
  return False

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " filename nbins")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]))
