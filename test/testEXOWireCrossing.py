import ROOT,sys

def main(Zpos):
  ROOT.gSystem.Load("libEXOUtilities")
  lower = -250
  upper = 250
  nbins = upper - lower
  hist = ROOT.TH2D("hist","hist",nbins,lower,upper,nbins,lower,upper)
  for x in range(lower,upper):
    for y in range(lower,upper):
      coord = ROOT.EXOCoordinates(ROOT.EXOMiscUtil.kXYCoordinates,x,y,Zpos,0)
      crossing = ROOT.EXOWireCrossing.GetInstance()
      hist.SetBinContent(x-lower,y-lower,crossing.GetDistanceFromHexagon(coord))
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage : " + sys.argv[0] + " Zpos")
    sys.exit(1)
  main(float(sys.argv[1]))
