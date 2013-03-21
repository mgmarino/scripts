import ROOT,sys,random
from math import sqrt,pi,cos,sin

def main(tree):
  dX = ROOT.RooRealVar("dX","dX",-200,200)
  dY = ROOT.RooRealVar("dY","dY",-200,200)
  dX.setBins(400)
  dY.setBins(400)
  frameX = dX.frame()
  frameY = dY.frame()
  print("Creating dataset")
  data = CreateXYdataSet(tree,dX,dY)
  data.Print()
  print("Creating right pdf")
  rightHist = CreateXYrightCombinationHist(tree,dX,dY)
  rightXHist = rightHist.reduce(ROOT.RooArgSet(dX))
  rightYHist = rightHist.reduce(ROOT.RooArgSet(dY))
  rightXPdf = ROOT.RooHistPdf("rightXPdf","rightXPdf",ROOT.RooArgSet(dX),rightXHist)
  rightYPdf = ROOT.RooHistPdf("rightYPdf","rightYPdf",ROOT.RooArgSet(dY),rightYHist)
  print("Creating single site pdf")
  ssHist = CreateXYsingleSiteHist(tree,dX,dY)
  ssXHist = ssHist.reduce(ROOT.RooArgSet(dX))
  ssYHist = ssHist.reduce(ROOT.RooArgSet(dY))
  ssXPdf = ROOT.RooHistPdf("ssXPdf","ssXPdf",ROOT.RooArgSet(dX),ssXHist)
  ssYPdf = ROOT.RooHistPdf("ssYPdf","ssYPdf",ROOT.RooArgSet(dY),ssYHist)

  c1 = ROOT.TCanvas("X")
  print("dX RMS of data/pdf: "+str(data.rmsVar(dX).getVal())+"/"+str(rightHist.rmsVar(dX).getVal()))
  data.plotOn(frameX)
  rightXPdf.plotOn(frameX)
  ssXPdf.plotOn(frameX,ROOT.RooFit.LineColor(ROOT.kRed))
  frameX.Draw()
  c1.Update()

  c2 = ROOT.TCanvas("Y")
  print("dY RMS of data/pdf: "+str(data.rmsVar(dY).getVal())+"/"+str(rightHist.rmsVar(dY).getVal()))
  data.plotOn(frameY)
  rightYPdf.plotOn(frameY)
  ssYPdf.plotOn(frameY,ROOT.RooFit.LineColor(ROOT.kRed))
  frameY.Draw()
  c2.Update()
  raw_input("q")

def CreateHistogramPdf(hist,name,dX):
  dataHist = ROOT.RooDataHist(name+"Hist",name+"Hist",ROOT.RooArgList(dX),hist)
  histPdf = ROOT.EXOhistPdf(name+"Pdf",name+"Pdf",ROOT.RooArgList(dX),dataHist,0)
  return histPdf,dataHist

def CreateXYsingleSiteHist(tree,dX,dY):
  tempfile = ROOT.TFile("tempfile.root","RECREATE")
  copytree = tree.CopyTree("NCL == 1 && abs(CC.fX) < 200 && CC.fRawEnergy > 300 && dX < "+str(dX.getMax())+" && dX > "+str(dX.getMin())+" && dY < "+str(dY.getMax())+" && dY > "+str(dY.getMin()))
  data = ROOT.RooDataSet("data","data",ROOT.RooArgSet(dX,dY),ROOT.RooFit.Import(copytree))
  histSingleSite = ROOT.RooDataHist("histSingleSite","histSingleSite",ROOT.RooArgSet(dX,dY))
  histSingleSite.add(data)
  return histSingleSite

def CreateXYrightCombinationHist(tree,dX,dY):
  dU = ROOT.RooRealVar("dU","dU",dX.getMin(),dX.getMax())
  dV = ROOT.RooRealVar("dV","dV",dX.getMin(),dX.getMax())
  tempfile = ROOT.TFile("tempfile.root","RECREATE")
  copytree = tree.CopyTree("abs(CC.fX) < 200 && CC.fRawEnergy > 300 && dU < "+str(dU.getMax())+" && dU > "+str(dU.getMin())+" && dV < "+str(dV.getMax())+" && dV > "+str(dV.getMin()))
  dataUV = ROOT.RooDataSet("dataUV","dataUV",ROOT.RooArgSet(dU,dV),ROOT.RooFit.Import(copytree))
  dX_formula = ROOT.RooFormulaVar("dX","dX","dV - dU",ROOT.RooArgList(dU,dV))
  dY_formula = ROOT.RooFormulaVar("dY","dY","(dU + dV) / sqrt(3.0)",ROOT.RooArgList(dU,dV))
  dataUV.addColumn(dX_formula)
  dataUV.addColumn(dY_formula)
  histFullRight = ROOT.RooDataHist("histFullRight","histFullRight",ROOT.RooArgSet(dX,dY))
  histFullRight.add(dataUV)
  return histFullRight

def CreateXgaussianPdf(dX,mean,sigma):
  dX_GaussianPdf = ROOT.RooGaussian("dX_GaussianPdf","dX_GaussianPdf",dX,mean,sigma)
  return dX_GaussianPdf

def CreateXfaultyCombinationPdf(N,dX,attenuation):
  histX_Faulty = ROOT.RooDataHist("histX_Faulty","histX_Faulty",ROOT.RooArgSet(dX))
  for i in range(N):
    x1,y1 = ExponentialHexagonXY(171.,254.,0.,attenuation)
    x2,y2 = ExponentialHexagonXY(171.,x1,y1,attenuation)
    u1,v1 = XYtoUV(x1,y1)
    u2,v2 = XYtoUV(x2,y2)
    X1,Y1 = UVtoXY(u1,v2)
    X2,Y2 = UVtoXY(u2,v1)
    dist11 = (x1-X1)**2 + (y1-Y1)**2
    dist12 = (x1-X2)**2 + (y1-Y2)**2
    distX = x1-X1
    if dist11 > dist12:
      distX = x1-X2
    dX.setVal(distX)
    histX_Faulty.add(ROOT.RooArgSet(dX))
    dX.setVal(-distX)
    histX_Faulty.add(ROOT.RooArgSet(dX))
  dX_FaultyPdf = ROOT.RooHistPdf("dX_FaultyPdf","dX_FaultyPdf",ROOT.RooArgSet(dX),histX_Faulty)
  return dX_FaultyPdf,histX_Faulty

def CreateXYdataSet(tree,dX,dY):
  tempfile = ROOT.TFile("tempfile.root","RECREATE")
  copytree = tree.CopyTree("abs(CC.fX) < 200 && CC.fRawEnergy > 300 && dX < "+str(dX.getMax())+" && dX > "+str(dX.getMin()))
  dataX = ROOT.RooDataSet("dataFull","dataFull",ROOT.RooArgSet(dX,dY),ROOT.RooFit.Import(copytree))
  return dataX

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
  factor = 2./sqrt(3.)
  while r > maxR:
    x = random.uniform(-maxR,maxR)
    y = random.uniform(-maxR*factor,maxR*factor)
    u,v = XYtoUV(x,y)
    r = max(abs(x),abs(u),abs(v))
  return x,y

def ExponentialHexagonXY(maxR,x1,y1,attenuation):
  r = maxR + 1
  while r > maxR:
    phi = random.uniform(0,2*pi)
    length = random.expovariate(1./attenuation)
    x = length * cos(phi) + x1
    y = length * sin(phi) + y1
    u,v = XYtoUV(x,y)
    r = max(abs(x),abs(u),abs(v))
  return x,y

def XYtoUV(x,y):
  u = -0.5*x + 0.5*sqrt(3.0)*y
  v =  0.5*x + 0.5*sqrt(3.0)*y
  return u,v

def UVtoXY(u,v):
  y = (u+v)/sqrt(3.0)
  x = v - u
  return x,y

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" AccuracyFile.root")
    print("\nAccuracyFile.root should be a file created by ReconAccuracyStudy.py")
    #print("FaultyHist.root should be a file created by FaultyClusteringDXpdf.py")
    sys.exit(1)
  #ROOT.gSystem.Load("libEXOUtilities")
  ROOT.gSystem.Load("~/EXO/EXO_Fitting/EXO_Fitting/lib/libEXOFitting")
  #f2 = ROOT.TFile(sys.argv[2])
  #hist = f2.Get("hDX")
  f = ROOT.TFile(sys.argv[1])
  t = f.Get("AccuracyTree")
  main(t)
