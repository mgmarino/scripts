import ROOT,math

def main():
  ROOT.gSystem.Load("libEXOROOT")
  cluster = ROOT.EXOClusteringModule()
  nbins = 300
  upperU = nbins*10 
  upperV = nbins*3
  hist = ROOT.TH2D("hist","hist",nbins,0,upperU,nbins,0,upperV)
  for j,v in enumerate(range(0,upperV,upperV/nbins)):
    for i,u in enumerate(range(0,upperU,upperU/nbins)):
      #val = math.exp(-cluster.energyNLPdf(u,v,0))
      val = cluster.energyNLPdf(u,v,0)
      hist.SetBinContent(i,j,val)
  c1 = ROOT.TCanvas()
  hist.Draw("colz")
  answer = ""
  while not answer in ["y","Y","n","N"]:
    answer = raw_input("do you want to save the histogram? (Y/N) ")
  if answer in ["y","Y"]:
    fname = raw_input("Please enter filename: ")
    f = ROOT.TFile(fname,"UPDATE")
    f.ls()
    key = raw_input("Please enter object key: ")
    hist.Write(key)
    f.Close()

if __name__ == "__main__":
  main()
