import ROOT,sys

if len(sys.argv) != 2:
  print("usage: " + sys.argv[0] + " file")
  sys.exit(1)

ROOT.gSystem.Load("libEXOROOT")

urange = 5000
vrange = 1400

hist1 = ROOT.TH2D("hist1","hist1",150,0,urange,150,0,vrange)
hist1.GetXaxis().SetTitle("Total gain corrected collection energy in event")
hist1.GetYaxis().SetTitle("Total gain corrected induction energy in event")
hist1.SetTitle("TOTAL event energy")

hist2 = ROOT.TH1D("hist2","hist2",400,-1000,1000)

f = ROOT.TFile(sys.argv[1])
t = f.Get("tree")
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


canvas1 = ROOT.TCanvas("canvas1")
canvas1.Divide(2,2)
canvas1.cd(1)
canvas1.SetLogz()
hist1.Draw("colz")

canvas1.cd(2)
prof = hist1.ProfileX()
low = input("enter fit range lower boundary: ")
high = input("enter fit range upper boundary: ")
prof.Fit("pol1","","",low,high)
scale = 1./prof.GetListOfFunctions().At(0).GetParameter(1)
print("Scale = " + str(scale))
canvas1.Update()

canvas1.cd(3)
hist3 = hist1.ProjectionX()
hist3.SetName("hist3")
hist3.SetTitle("sigmas")
hist3.GetXaxis().SetTitle("energy")
hist3.GetYaxis().SetTitle("sigma")
#canvas2 = ROOT.TCanvas("canvas2")
for i in range(1,hist1.GetNbinsX()+1):
  proj = hist1.ProjectionY("proj",i,i)
  #proj.Draw()
  #canvas2.Update()
  #raw_input("continue")
  hist3.SetBinContent(i,proj.GetRMS())
hist3.Draw()

canvas1.cd(4)
for i in range(t.GetEntries()):
  t.GetEntry(i)
  uenergy = 0.0
  venergy = 0.0
  for j in range(ED.GetNumUWireSignals()):
    uenergy += ED.GetUWireSignal(j).fRawEnergy
  for j in range(ED.GetNumVWireSignals()):
    venergy += ED.GetVWireSignal(j).fMagnitude
  if(uenergy > 0):
    hist2.Fill(venergy*scale - uenergy)
hist2.Draw()
canvas1.Update()

raw_input("hit enter to quit")
