import ROOT,sys,random
from math import sqrt

def main(outname,tree):
  smear = True
  hist = ROOT.TH1D("hDX","hDX",400,-200,200)
  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)
  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    ncl = ED.GetNumChargeClusters()
    if ncl != 2:
      continue
    cc1 = ED.GetChargeCluster(0)
    cc2 = ED.GetChargeCluster(1)
    if abs(cc1.fZ - cc2.fZ) > 6:
      continue
    nsc = HowManySharedChannels(cc1,cc2)
    print(nsc)
    if nsc:
      continue
    x1,y1 = cc1.fX,cc1.fY
    x2,y2 = cc2.fX,cc2.fY
    u1,v1 = XYtoUV(x1,y1)
    if smear:
      u1 += random.uniform(-4.5,4.5)
      v1 += random.gauss(0,1.7)
    u2,v2 = XYtoUV(x2,y2)
    if smear:
      u2 += random.uniform(-4.5,4.5)
      v2 += random.gauss(0,1.7)
    X1,Y1 = UVtoXY(u1,v2)
    X2,Y2 = UVtoXY(u2,v1)
    dist11 = (x1-X1)**2 + (y1-Y1)**2
    dist12 = (x1-X2)**2 + (y1-Y2)**2
    distX = x1-X1
    if dist11 > dist12:
      distX = x1-X2
    hist.Fill(distX)
    hist.Fill(-distX)
  hist.Draw()
  raw_input("q")
  fout = ROOT.TFile(outname,"RECREATE")
  hist.Write()
  fout.Close()
    
def HowManySharedChannels(cc1,cc2):
  channels1 = set()
  channels2 = set()
  for i in range(cc1.GetNumUWireSignals()):
    channels1.add(cc1.GetUWireSignalChannelAt(i))
  for i in range(cc2.GetNumUWireSignals()):
    channels2.add(cc2.GetUWireSignalChannelAt(i))
  return len(channels1 & channels2)

def XYtoUV(x,y):
  u = -0.5*x + 0.5*sqrt(3.0)*y
  v =  0.5*x + 0.5*sqrt(3.0)*y
  return u,v

def UVtoXY(u,v):
  y = (u+v)/sqrt(3.0)
  x = v - u
  return x,y

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: "+sys.argv[0]+" outfile infile[s]")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in sys.argv[2:]:
    t.Add(f)
  main(sys.argv[1],t)
