import ROOT,sys,random
from math import sqrt

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  f = ROOT.TFile(filename)
  #t = f.Get("AccuracyTree")
  hist = f.Get("hist")
  dU = ROOT.RooRealVar("dU","dU",-200,200)
  dV = ROOT.RooRealVar("dV","dV",-200,200)
  pdfU,pdfV = CreateReconErrorWirePdfs(dU,dV,160,5,180,100000,hist)
  frame = dU.frame()
  pdfU.plotOn(frame)
  frame.Draw()
  raw_input("q")

def CreateXrightCombinationPdf(h_dUdV_right):
  dU = ROOT.RooRealVar("dU","dU",-200,200)
  dV = ROOT.RooRealVar("dV","dV",-200,200)
  dX = ROOT.RooFormulaVar("dX","dX","dU - dV",ROOT.RooArgList(dU,dV))
  histUV = ROOT.RooDataHist("histUV","histUV",ROOT.RooArgList(dU,dV),h_dUdV_right)
  dXpdf = ROOT.RooHistPdf("dXpdf","dXpdf",ROOT.RooArgList(dX),ROOT.RooArgList(dU,dV),histUV)

def CreateReconErrorWirePdfs(dU,dV,rCut,lowerZCut,upperZCut,N,numPCDhist):
  histU = ROOT.RooDataHist("hUWireReconError","hUWireReconError",ROOT.RooArgSet(dU))
  histV = ROOT.RooDataHist("hVWireReconError","hVWireReconError",ROOT.RooArgSet(dV))
  nPCD = ROOT.RooRealVar("nPCD","nPCD",0,50)
  histNpcd = ROOT.RooDataHist("histNpcd","histNpcd",ROOT.RooArgList(nPCD),numPCDhist)
  NpcdPdf = ROOT.RooHistPdf("NpcdPdf","NpcdPdf",ROOT.RooArgList(nPCD),ROOT.RooArgList(nPCD),histNpcd)
  frame = nPCD.frame()
  NpcdPdf.plotOn(frame)
  frame.Draw()
  raw_input("c")
  nPCDset = NpcdPdf.generate(ROOT.RooArgSet(nPCD),N)
  for i in range(N):
    argset = nPCDset.get(i)
    nPCDs = int(argset["nPCD"].getVal())
    x1,y1 = RandomHexagonXY(171.)
    z1 = random.uniform(lowerZCut,upperZCut)
    nearestXYZ = (1000.,1000.,1000.)
    nearestDist = 3000.
    for j in range(max(1,nPCDs)):
      x2,y2 = RandomCircleXY(rCut)
      z2 = random.uniform(lowerZCut,upperZCut)
      dist = GetDistance((x1,y1,z1),(x2,y2,z2))
      if dist < nearestDist:
        nearestDist = dist
        nearestXYZ = (x2,y2,z2)
    u1,v1 = XYtoUV(x1,y1)
    u2,v2 = XYtoUV(x2,y2)
    dU.setVal(u1-u2)
    dV.setVal(v1-v2)
    histU.add(ROOT.RooArgSet(dU))
    histV.add(ROOT.RooArgSet(dV))
  pdfU = ROOT.RooHistPdf("pdfUWireReconError","pdfUWireReconError",ROOT.RooArgList(dU),ROOT.RooArgList(dU),histU)
  pdfV = ROOT.RooHistPdf("pdfVWireReconError","pdfVWireReconError",ROOT.RooArgList(dV),ROOT.RooArgList(dV),histV)
  return pdfU,pdfV
  

def GetDistance(r1,r2):
  val = 0
  for i in range(3):
    val += (r1[i] - r2[i])**2
  return sqrt(val)

def RandomCircleXY(maxR):
  upper = maxR**2
  r2 = upper + 1
  while r2 > upper:
    x = random.uniform(0,maxR)
    y = random.uniform(0,maxR)
    r2 = x**2 + y**2
  return x,y

def RandomHexagonXY(maxR):
  r = maxR + 1
  while r > maxR:
    x = random.uniform(0,maxR)
    y = random.uniform(0,maxR)
    u,v = XYtoUV(x,y)
    r = max(x,u,v)
  return x,y

def XYtoUV(x,y):
  u = -0.5*x + 0.5*sqrt(3.0)*y
  v =  0.5*x + 0.5*sqrt(3.0)*y
  return u,v
  

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" AccuracyFile.root")
    sys.exit(1)
  main(sys.argv[1])
