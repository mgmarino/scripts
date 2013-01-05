import ROOT,math

def main():
  ROOT.gSystem.Load("libEXOROOT")
  ROOT.gStyle.SetOptStat(0)
  cluster = ROOT.EXOClusteringModule()
  minT = -5000
  maxT = 5000
  stepT = 100
  minZ = 0
  maxZ = 200
  stepZ = 1
  Tbins = range(minT,maxT,stepT)
  Zbins = range(minZ,maxZ,stepZ)
  hist = ROOT.TH2D("hist","hist",len(Zbins),minZ,maxZ,len(Tbins),minT/1000.,maxT/1000.)
  hist.SetTitle("U-V time difference pdf")
  hist.GetXaxis().SetTitle("Z (mm)")
  hist.GetYaxis().SetTitle("#DeltaT (#mus)")
  for x,z in enumerate(Zbins):
    for y,t in enumerate(Tbins):
      val = cluster.timeNLPdf(0.,t,z,False)
      print("val(t = " + str(t/1000.) + ", z = " + str(z) +") = " + str(val))
      hist.SetBinContent(x,y,val)
  c1 = ROOT.TCanvas()
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  main()
