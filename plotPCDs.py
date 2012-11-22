import ROOT,math,sys

def main(files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  t.Draw("fMonteCarloData.fPixelatedChargeDeposits.GetPixelCenter().GetY():fMonteCarloData.fPixelatedChargeDeposits.GetPixelCenter().GetX()")
  lines = []
  for i in range(6):
    x1,y1,x2,y2 = GetEdges(i*math.pi/3.)
    lines.append(ROOT.TLine(x1,y1,x2,y2))
    lines[-1].SetLineColor(ROOT.kRed)
    lines[-1].SetLineWidth(2)
    lines[-1].Draw("same")
  raw_input("hit enter to quit")

def GetEdges(rotAngle):
  x1 = (ROOT.CHANNEL_WIDTH * ROOT.NCHANNEL_PER_WIREPLANE)/2.
  y1 = x1 / math.sqrt(3.0)
  x2 = x1
  y2 = -y1

  cos = math.cos(rotAngle)
  sin = math.sin(rotAngle)
  X1 = cos*x1 - sin*y1
  X2 = cos*x2 - sin*y2
  Y1 = sin*x1 + cos*y1
  Y2 = sin*x2 + cos*y2

  return X1,Y1,X2,Y2

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])
