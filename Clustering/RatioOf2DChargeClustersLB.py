import ROOT,sys

def main(nbins,rng,zCut):
  ROOT.gSystem.Load("libEXOUtilities")
  basePath = "/nfs/slac/g/exo_data3/exo_data/data/WIPP/processed/"
  runs = [3004,3009,3012,3015,3021,3025,3029,3033,3045,3049,3052,3056,3061,3071,3085,3088,3092,3093,3096,3101,3106,3117]
  t = ROOT.TChain("tree")
  for run in runs:
    t.Add(basePath + str(run) + "/proc0000" + str(run) + "*.root")
  binstring = str(nbins)
  hist = ROOT.TH1D("hist","2D reconstruction rate",nbins,0,rng)
  hist.GetXaxis().SetTitle("Charge cluster energy (keV)")
  t.Draw("fChargeClusters.fRawEnergy>>hFull("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  t.Draw("fChargeClusters.fRawEnergy>>hGood("+binstring+",0,"+str(rng)+")","fChargeClusters.fRawEnergy < "+str(rng)+" && abs(fChargeClusters.fX) < 172 && abs(fChargeClusters.fZ) < "+str(zCut),"goff")
  hFull = ROOT.gDirectory.Get("hFull")
  hGood = ROOT.gDirectory.Get("hGood")
  hFull.Sumw2()
  hGood.Sumw2()
  hist.Divide(hGood,hFull,1,1,"B")
  hist.Draw("E")
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

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("usage: " + sys.argv[0] + " nbins range zCut")
    sys.exit(1)
  main(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
