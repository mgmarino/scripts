import ROOT,math

def main():
  ROOT.gSystem.Load("libEXOROOT")
  ROOT.gStyle.SetOptStat(0)
  cluster = ROOT.EXOClusteringModule()
  lowerx = -250
  upperx = 250
  lowery = -250
  uppery = 250
  nbinsx = upperx - lowerx
  nbinsy = uppery - lowery
  hist = ROOT.TH2D("hist","Distance from wire hexagon pdf",nbinsx,lowerx,upperx,nbinsy,lowery,uppery)
  hist.GetXaxis().SetTitle("X (mm)")
  hist.GetYaxis().SetTitle("Y (mm)")
  for i,x in enumerate(range(lowerx,upperx)):
    for j,y in enumerate(range(lowery,uppery)):
      coord = ROOT.EXOCoordinates(ROOT.EXOMiscUtil.kXYCoordinates,x,y,100.0,0.0)
      val = math.exp(-cluster.positionNLPdf(coord.GetU(),coord.GetV()))
      hist.SetBinContent(i,j,val)
  c1 = ROOT.TCanvas()
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  main()
