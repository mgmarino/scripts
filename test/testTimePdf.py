import ROOT,math

def main():
  ROOT.gSystem.Load("libEXOROOT")
  cluster = ROOT.EXOClusteringModule()
  lowert = -5
  uppert = 5
  nbins = (uppert - lowert) * 10
  hist = ROOT.TH1D("hist","hist",nbins,lowert,uppert)
  for i in range(nbins):
    time = (lowert + float(i)/10.)*1000.
    #val = math.exp(-cluster.timeNLPdf(0.,time))
    val = cluster.timeNLPdf(0.,time)
    print("val(t = " + str(time/1000.) + ") = " + str(val))
    hist.SetBinContent(i,val)
  c1 = ROOT.TCanvas()
  hist.Draw()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  main()
