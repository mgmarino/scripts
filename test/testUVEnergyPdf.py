import ROOT,math

def main():
  ROOT.gSystem.Load("libEXOROOT")
  cluster = ROOT.EXOClusteringModule()
  nbins = 200
  upperU = 2000
  upperV = 500
  hist = ROOT.TH2D("hist","hist",nbins,0,upperU,nbins,0,upperV)
  for j,v in enumerate(range(0,upperV,upperV/nbins)):
    for i,u in enumerate(range(0,upperU,upperU/nbins)):
      val = math.exp(-cluster.energyNLPdf(u,v))
      #val = -cluster.energyNLPdf(u,v)
      hist.SetBinContent(i,j,val)
  c1 = ROOT.TCanvas()
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  main()
