import ROOT,sys,glob
from math import sqrt

def Run(prefix, **kwargs):
  crl = kwargs['ControlRecordList']
  beginRecord = crl.GetNextRecord('EXOBeginRecord')()
  if beginRecord.GetRunFlavor() not in [ROOT.EXOBeginRecord.kDatPhysics,
                                        ROOT.EXOBeginRecord.kDatSrcClb]:
    return

  tree = kwargs['EventTree']
  if tree.GetEntries() < 10000:
    return

  maxEnergy = 1000
  nBins = 50
  zCut = 200 


  baseCut = "fChargeClusters.fCorrectedEnergy < "+str(maxEnergy)+" && abs(fChargeClusters.fZ) < "+str(zCut)+" && abs(Sum$(fChargeClusters.fRawEnergy) - Max$(fChargeClusters.fRawEnergy)) < 1 && Max$(fChargeClusters.GetNumUWireSignals()) < 3"

  goodCut = baseCut + " && abs(fChargeClusters.fX) < 172"

  tree.Draw(WhatToDraw("hFullSS",nBins,maxEnergy),baseCut,"goff")
  tree.Draw(WhatToDraw("hGoodSS",nBins,maxEnergy),goodCut,"goff")

  hFull = ROOT.gDirectory.Get("hFullSS")
  hGood = ROOT.gDirectory.Get("hGoodSS")
  hFull.Sumw2()
  hGood.Sumw2()
  hRate = ROOT.TGraphAsymmErrors(hGood,hFull)
  
  funct = ROOT.TF1("funct","[0] * 0.5 * (1 + TMath::Erf((x-[1]) / (sqrt(2)*[2])))",0,maxEnergy)
  funct.SetParameter(0,1)
  funct.SetParameter(1,250)
  funct.SetParameter(2,150)
  hRate.Fit(funct,"QRE")
  #hRate.Draw("AP")
  #raw_input("hit enter to quit")
  params = []
  for i in range(3):
    params.append((funct.GetParameter(i),funct.GetParError(i)))
  return { "2D_RATE_LIMIT" : params[0],
           "2D_RATE_THRESHOLD" : params[1],
           "2D_RATE_RISE" : params[2] }

def WhatToDraw(histname,nBins,maxEnergy):
  return "fChargeClusters.fCorrectedEnergy>>"+histname+"("+str(nBins)+",0,"+str(maxEnergy)+")"


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0] + " run")
    sys.exit(1)

  ROOT.gSystem.Load("libEXOUtilities")
  path = '/nfs/slac/g/exo_data3/exo_data/data/WIPP/masked/'+sys.argv[1]+"/*.root"
  t = ROOT.TChain("tree")
  t.Add(path)
  SortedFiles = glob.glob(path)
  if len(SortedFiles) < 1:
    print('No files found for run '+sys.argv[1])
    sys.exit(1)
  SortedFiles.sort()
  LastFile = ROOT.TFile(SortedFiles.pop())
  LastTree = LastFile.Get("tree")
  crl = LastTree.GetUserInfo().At(1)
  print(Run("prefix", EventTree = t, ControlRecordList = crl))
