import ROOT,sys

def main(workspaces):

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
 
 
  frameDataSS = ROOT.RooPlot()
  frameDataMS = ROOT.RooPlot()
  framePdfSS = ROOT.RooPlot()
  framePdfMS = ROOT.RooPlot()
 
  for i,workspace in enumerate(workspaces):
    fitter.LoadWorkspace(workspace)
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

    if not i:
      frameDataSS = energy_ss.frame()
      frameDataMS = energy_ms.frame()
      framePdfSS = energy_ss.frame()
      framePdfMS = energy_ms.frame()
    
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

    data_ss.plotOn(frameDataSS, ROOT.RooFit.MarkerSize(0.8), ROOT.RooFit.DrawOption("PZ"), ROOT.RooFit.MarkerColor(i+1), ROOT.RooFit.LineColor(i+1))
    data_ms.plotOn(frameDataMS, ROOT.RooFit.MarkerSize(0.8), ROOT.RooFit.DrawOption("PZ"), ROOT.RooFit.MarkerColor(i+1), ROOT.RooFit.LineColor(i+1))
    epdf_ss.plotOn(framePdfSS, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected), ROOT.RooFit.LineColor(i+1))
    epdf_ms.plotOn(framePdfMS, ROOT.RooFit.Normalization(1.,ROOT.RooAbsReal.RelativeExpected), ROOT.RooFit.LineColor(i+1))

  c1 = ROOT.TCanvas("c1","Weak Th Data",1200,700)
  c1.Divide(1,2)
  c1.cd(1)
  frameDataSS.Draw()
  c1.cd(2)
  frameDataMS.Draw()

  c2 = ROOT.TCanvas("c2","Weak Th Pdf",1200,700)
  c2.Divide(1,2)
  c2.cd(1)
  framePdfSS.Draw()
  c2.cd(2)
  framePdfMS.Draw()

  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("usage: " + sys.argv[0] + " workspace1 workspace2 [workspace3 ...]")
    sys.exit(1)
  main(sys.argv[1:])
