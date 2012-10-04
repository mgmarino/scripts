import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")

  urange = 6000
  vrange = 1200

  hist1 = ROOT.TH2D("hist1","hist1",100,0,urange,100,0,vrange)
  hist1.GetXaxis().SetTitle("Total gain corrected collection energy in event")
  hist1.GetYaxis().SetTitle("Total gain corrected induction energy in event")
  hist1.SetTitle("TOTAL event energy")

  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    uenergy = 0.0
    venergy = 0.0
    bad = False
    for j in range(ED.GetNumUWireSignals()):
      uws = ED.GetUWireSignal(j)
      if uws.fTime < 120.*1000.:
        bad = True
        break
      uenergy += uws.fCorrectedEnergy
    if bad:
      continue
    for j in range(ED.GetNumVWireSignals()):
      venergy += ED.GetVWireSignal(j).fCorrectedMagnitude
    if(uenergy > 0 and venergy > 0):
      hist1.Fill(uenergy,venergy)
    if(uenergy > 3000) and (venergy < 400):
      print("(u,v) = ("+str(uenergy)+","+str(venergy)+") in run\\event: "+str(ED.fRunNumber)+"\\"+str(ED.fEventNumber))


  canvas1 = ROOT.TCanvas("canvas1")
  canvas1.SetLogz()
  hist1.Draw("colz")
  canvas1.Update()

  canvas2 = ROOT.TCanvas("canvas2")
  prof = hist1.ProfileX()
  prof.Draw()
  canvas2.Update()

  canvas3 = ROOT.TCanvas("canvas3")
  hist3 = hist1.ProjectionX()
  hist3.SetName("hist3")
  hist3.SetTitle("sigmas")
  hist3.GetXaxis().SetTitle("energy")
  hist3.GetYaxis().SetTitle("sigma")
  for i in range(1,hist1.GetNbinsX()+1):
    proj = hist1.ProjectionY("proj",i,i)
    hist3.SetBinContent(i,proj.GetRMS())
  hist3.Draw()
  canvas3.Update()

  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the profile? (Y/N): ")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    prof.Write(key)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " file")
    sys.exit(1)
  main(sys.argv[1])

