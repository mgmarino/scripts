import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  f = ROOT.TFile(filename)
  t = f.Get("tree")
  t.Draw("fChargeClusters.fCorrectedAmplitudeInVChannels:fChargeClusters.fPurityCorrectedEnergy>>h(100,0,4000,100,0,1000)","","colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
