import ROOT,sys

def main(workspaceFile,outfile):

  ROOT.gROOT.SetStyle("Plain")
  ROOT.gSystem.Load("$EXODIR/wolfhart/EXO_Fitting_svn/trunk/EXO_Fitting/lib/libEXOFitting")
  fitter = ROOT.EXOFitter()
  fitter.fUseBetaScale = False

  ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING);

  min = 700.
  max = 3500.
  nBins = 200
 
  min2 = fitter.fMCminSD
  max2 = fitter.fMCmaxSD
  nBins2 = fitter.fMCbinsSD


  binnedFit = True 
  b1 = ROOT.RooBinning(nBins,min,max)
  b2 = ROOT.RooBinning(nBins2,min2,max2)
 
 
  fitter.LoadWorkspace(workspaceFile)

  fitter.fNumCPU=4
 
  wsp = fitter.GetWorkspace()

  # get variables and formula
  energy_ss = wsp.var("energy_ss")
  energy_ms = wsp.var("energy_ms")
  # make sure the variables exist in the worksapce
  if not energy_ss:
    print("Warning: energy_ss does not exist in the workspace.")
    sys.exit(1)
  if not energy_ms:
    print("Warning: energy_ms does not exist in the workspace.")
    sys.exit(1)
  
  energy_ss.setBinning(b1)
  energy_ms.setBinning(b1)

  standoff = wsp.var("standoff_distance")
  standoff.setBinning(b2)

  # get Data
  EXOData_run2 = wsp.data("EXOData_run2")
  if not EXOData_run2:
    print("Warning: EXOData_run2 does not exist in the workspace.")
    sys.exit(1)
  
  # create subset of data with muon veto applied
  cut = "energy_ss > " + str(min) + " && energy_ss < " + str(max)
  cut += " &&numSite==numSite::single && diagCut == diagCut::yes"
  cut += " && standoff_distance > " + str(min2) + " && standoff_distance < " + str(max2)

  # Create single site subset
  EXOData_veto_run2_ss = EXOData_run2.reduce(ROOT.RooArgSet(energy_ss,standoff),cut)
  EXOData_veto_run2_ss.SetName("EXOData_veto_run2_ss")

  cut = "energy_ms > " + str(min) + " && energy_ms < " + str(max) + " &&numSite==numSite::multiple"
  cut += " && diagCut == diagCut::yes"
  cut += " && standoff_distance > " + str(min2) + " && standoff_distance < " + str(max2)

  # Create multi site subset
  EXOData_veto_run2_ms = EXOData_run2.reduce(ROOT.RooArgSet(energy_ms,standoff),cut)
  EXOData_veto_run2_ms.SetName("EXOData_veto_run2_ms")

  hdata_ss = EXOData_veto_run2_ss.binnedClone()
  hdata_ss.SetName("hdata_ss")
  hdata_ms = EXOData_veto_run2_ms.binnedClone()
  hdata_ms.SetName("hdata_ms")
 
  data_ss = EXOData_veto_run2_ss
  if binnedFit:
    data_ss = hdata_ss
  data_ms = EXOData_veto_run2_ms
  if binnedFit:
    data_ms = hdata_ms

  # Get PDFs
  epdf_ss = fitter.GetSourcePdf("SourceP4_px_228Th_Pdf",ROOT.kSingleSite)
  if not epdf_ss:
    print("Could not load SS source pdf. returning 1")
    sys.exit(1)
  epdf_ms = fitter.GetSourcePdf("SourceP4_px_228Th_Pdf",ROOT.kMultiSite)
  if not epdf_ms:
    print("Could not load MS source pdf. returning 1")
    sys.exit(1)

  nll_ss = ROOT.RooNLLVar("nll_ss","nll_ss",epdf_ss,data_ss,ROOT.RooFit.Extended(True),ROOT.RooFit.NumCPU(fitter.fNumCPU))
  nll_ms = ROOT.RooNLLVar("nll_ms","nll_ms",epdf_ms,data_ms,ROOT.RooFit.Extended(True),ROOT.RooFit.NumCPU(fitter.fNumCPU))
  
  nM = ROOT.RooRealVar("nM","nM",EXOData_veto_run2_ms.sumEntries())
  nS = ROOT.RooRealVar("nS","nS",EXOData_veto_run2_ss.sumEntries())

  mcS = epdf_ss.findServer("model_ss_nevents")
  mcS.setVal(nS.getVal())
  mcM = epdf_ms.findServer("model_ms_nevents")
  mcM.setVal(nM.getVal())

 
  # include constraint on the SSMS ratio
  ssms = ROOT.RooFormulaVar("ssms","ssms","@0/(@0+@1)",ROOT.RooArgList(mcS,mcM))
  ssms0 = fitter.GetSSMSRatio("SourceP4_px_228Th",energy_ss.getMin(),energy_ss.getMax())
  erSSMS = ROOT.RooRealVar("erSSMS","erSSMS",ssms0/(1.+ssms0)*0.3) #dummy error
  ssms0var = ROOT.RooRealVar("ssms0var","ssms0var",ssms0/(1.+ssms0))
  gc = ROOT.EXOgaussianConstraint("gc","gc",ROOT.RooArgList(ssms),ROOT.RooArgList(ssms0var),ROOT.RooArgList(erSSMS))
  gc.setNLval(True)
 
  nll = ROOT.RooAddition("nll","nll",ROOT.RooArgSet(nll_ss, nll_ms, gc))
  
  m = ROOT.RooMinuit(nll)
  m.migrad()
  
  fitresult = m.save()

  print("Fraction Data: " + str(nS.getVal()/(nS.getVal()+nM.getVal())))
  print("Fraction MC: " + str(ssms.getVal()))
  print("Fraction MC initial: " + str(ssms0var.getVal()))
  
  # create plot frame for single sites
  frame_ss = energy_ss.frame()
  data_ss.plotOn(frame_ss, ROOT.RooFit.MarkerSize(0.8), ROOT.RooFit.DrawOption("PZ"))
  # create plot frame for multiple sites
  frame_ms = energy_ms.frame()
  data_ms.plotOn(frame_ms, ROOT.RooFit.MarkerSize(0.8), ROOT.RooFit.DrawOption("PZ"))
  
  frds = standoff.frame()
  frdm = standoff.frame()
  data_ss.plotOn(frds, ROOT.RooFit.MarkerSize(0.8),ROOT.RooFit.DrawOption("PZ"))
  data_ms.plotOn(frdm, ROOT.RooFit.MarkerSize(0.8),ROOT.RooFit.DrawOption("PZ"))
  

  hss = frame_ss.getHist()
  hms = frame_ms.getHist()
  if hss:
    for i in range(energy_ss.getBins()):
      el = hss.GetEYlow()[i]
      eh = hss.GetEYhigh()[i]
      if(el==0 and eh!=0):
        hss.GetEYhigh()[i]=0
  if hms: 
    for i in range(energy_ms.getBins()):
      el = hms.GetEYlow()[i]
      eh = hms.GetEYhigh()[i]
      if(el==0 and eh!=0):
        hms.GetEYhigh()[i]=0

  epdf_ss.plotOn(frame_ss, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected))
  epdf_ms.plotOn(frame_ms, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected))
  epdf_ss.plotOn(frds, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected))
  epdf_ms.plotOn(frdm, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected))

  npars = fitresult.floatParsInit().getSize()

  frame_ss.SetTitle("Single Site, #chi^{2}/ndf = " + str(frame_ss.chiSquare(npars/2)))
  frame_ms.SetTitle("Multi Site, #chi^{2}/ndf = " + str(frame_ms.chiSquare(npars/2)))
  
  cSourceFitter = ROOT.TCanvas("cSourceFitterWeakTh228", "Source Fitting", 1200, 600)
  cSourceFitter.Divide(2, 1)
  
  cSourceFitter.cd(1)
  frame_ss.Draw()
  
  cSourceFitter.cd(2)
  frame_ms.Draw()
  
  c2 = ROOT.TCanvas("c2_WeakTh228","c2_WeakTh228",1200,600)
  c2.Divide(1,2)
  c2.cd(1)
  frame_ss.Draw()
  c2.cd(2)
  frame_ms.Draw()

  c3 = ROOT.TCanvas("c3","c3",1200,600)
  c3.Divide(2,1)
  c3.cd(1)
  frds.Draw()
  c3.cd(2)
  frdm.Draw()

  print(frame_ss.chiSquare(npars/2))
  print(frame_ms.chiSquare(npars/2))
  
  #out = ROOT.TFile("outfile","RECREATE")
  #cSourceFitter.Write()
  #c2.Write()
  #c3.Write()
  #wsp2 = ROOT.RooWorkspace("wsp2","wsp2")
  #tmpDir = ROOT.gDirectory
  #ROOT.gDirectory = ROOT.gROOT
  #frame_ss.SetName("frs")
  #frame_ms.SetName("frm")
  #wsp2.import(frame_ss)
  #wsp2.import(frame_ms)
  #gDirectory = tmpDir
  #wsp2.import(fitresult)
  #wsp2.Write()
  #out.Close()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " infile outfile")
    sys.exit(1)
  main(sys.argv[1],sys.argv[2])
