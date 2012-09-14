import ROOT,sys

def main(Zpos):
  ROOT.gSystem.Load("libEXOUtilities")
  lowerx = -250
  upperx = 250
  lowery = -250
  uppery = 250
  nbinsx = upperx - lowerx
  nbinsy = uppery - lowery
  hist = ROOT.TH2D("hist","hist",nbinsx,lowerx,upperx,nbinsy,lowery,uppery)
  for i,x in enumerate(range(lowerx,upperx)):
    for j,y in enumerate(range(lowery,uppery)):
      coord = ROOT.EXOCoordinates(ROOT.EXOMiscUtil.kXYCoordinates,x,y,Zpos,0)
      crossing = ROOT.EXOWireCrossing.GetInstance()
      hist.SetBinContent(i,j,crossing.GetDistanceFromHexagon(coord))
  hist.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage : " + sys.argv[0] + " Zpos")
    sys.exit(1)
  main(float(sys.argv[1]))
