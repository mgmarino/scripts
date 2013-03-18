import ROOT,sys,random
from math import sqrt,pi,cos,sin

def main(tree,hist):
  dX = ROOT.RooRealVar("dX","dX",-200,200)
  dX.setBins(400)
  frame = dX.frame()
  print("Creating right pdf")
  rightPdf,rightHist = CreateXrightCombinationPdf(tree,dX)
  print("Creating faulty pdf")
  #faultyPdf,faultyHist = CreateXfaultyCombinationPdf(1000000,dX,30.)
  faultyPdf,faultyHist = CreateHistogramPdf(hist,"faulty",dX)
  rightPdf.plotOn(frame)
  faultyPdf.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed))
  frame.Draw()
  raw_input("c")
  data = CreateXdataSet(tree,dX)
  data.Print()

  numRight = ROOT.RooRealVar("numRight","numRight",120000,1,2e6)
  numFaulty = ROOT.RooRealVar("numFaulty","numFaulty",6000,1,5e5)

  #totalPdf = ROOT.RooAddPdf("totalPdf","totalPdf",ROOT.RooArgList(rightPdf,faultyPdf),ROOT.RooArgList(numRight,numFaulty))
  totalPdf = rightPdf

  numRight.Print()
  numFaulty.Print()
  frame = dX.frame()
  data.plotOn(frame)
  totalPdf.plotOn(frame)
  frame.Draw()
  raw_input("c")

  nll = ROOT.RooNLLVar("nll","nll",totalPdf,data,ROOT.RooFit.Extended(True),ROOT.RooFit.NumCPU(4))
  minimizer = ROOT.RooMinuit(nll)
  print("Starting fit")
  minimizer.migrad()
  print("Fit finished")


  frame = dX.frame()
  data.plotOn(frame)
  totalPdf.plotOn(frame)
  frame.Draw()

  c2 = ROOT.TCanvas("c2")
  resid = frame.residHist()
  frame2 = dX.frame()
  frame2.addPlotable(resid,"P")
  frame2.Draw()
  raw_input("q")

def CreateHistogramPdf(hist,name,dX):
  dataHist = ROOT.RooDataHist(name+"Hist",name+"Hist",ROOT.RooArgList(dX),hist)
  histPdf = ROOT.EXOhistPdf(name+"Pdf",name+"Pdf",ROOT.RooArgList(dX),dataHist,0)
  return histPdf,dataHist

def CreateXrightCombinationPdf(tree,dX):
  dU = ROOT.RooRealVar("dU","dU",dX.getMin(),dX.getMax())
  dV = ROOT.RooRealVar("dV","dV",dX.getMin(),dX.getMax())
  fRawEnergy = ROOT.RooRealVar("fRawEnergy","fRawEnergy",0,10000)
  NCL = ROOT.RooRealVar("NCL","NCL",0,20)
  dataUV = ROOT.RooDataSet("dataUV","dataUV",tree,ROOT.RooArgSet(dU,dV,fRawEnergy,NCL),"NCL == 2 && fRawEnergy > 400 && dU < "+str(dU.getMax())+" && dU > "+str(dU.getMin())+" && dV < "+str(dV.getMax())+" && dV > "+str(dV.getMin()))
  dX_formula = ROOT.RooFormulaVar("dX","dX","dV - dU",ROOT.RooArgList(dU,dV))
  dataUV.addColumn(dX_formula)
  histFullRight = ROOT.RooDataHist("histFullRight","histFullRight",ROOT.RooArgSet(dX))
  histFullRight.add(dataUV,"dX < "+str(dX.getMax())+" && dX > "+str(dX.getMin()))
  del dataUV
  histX_Right = histFullRight.reduce(ROOT.RooArgSet(dX))
  del histFullRight
  dX_RightPdf = ROOT.RooHistPdf("dX_RightPdf","dX_RightPdf",ROOT.RooArgSet(dX),histX_Right)
  return dX_RightPdf,histX_Right

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

def CreateXdataSet(tree,dX):
  fRawEnergy = ROOT.RooRealVar("fRawEnergy","fRawEnergy",0,10000)
  NCL = ROOT.RooRealVar("NCL","NCL",0,20)
  dataFull = ROOT.RooDataSet("dataFull","dataFull",tree,ROOT.RooArgSet(dX,fRawEnergy,NCL),"NCL == 2 && fRawEnergy > 400 && dX < "+str(dX.getMax())+" && dX > "+str(dX.getMin()))
  dataX = dataFull.reduce(ROOT.RooArgSet(dX))
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
  if len(sys.argv) != 3:
    print("usage: "+sys.argv[0]+" AccuracyFile.root FaultyHist.root")
    print("AccuracyFile.root should be a file created by ReconAccuracyStudy.py")
    print("FaultyHist.root should be a file created by FaultyClusteringDXpdf.py")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  ROOT.gSystem.Load("~/EXO/EXO_Fitting/EXO_Fitting/lib/libEXOFitting")
  f2 = ROOT.TFile(sys.argv[2])
  hist = f2.Get("hDX")
  f = ROOT.TFile(sys.argv[1])
  t = f.Get("AccuracyTree")
  main(t,hist)
