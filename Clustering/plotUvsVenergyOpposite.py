import ROOT,sys

def main(filename,detHalf):
  ROOT.gStyle.SetPalette(1)

  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  urange = 5000
  vrange = 1400

  hist1 = ROOT.TH2D("hist1","Total event energy in detector half "+str(detHalf),150,0,urange,150,0,vrange)
  hist1.GetXaxis().SetTitle("Total gain corrected collection energy in event")
  hist1.GetYaxis().SetTitle("Total gain corrected induction energy in event")

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
      if ROOT.EXOMiscUtil.GetTPCSide(uws.fChannel) != detHalf:
        continue
      uenergy += uws.fCorrectedEnergy
    if bad:
      continue
    for j in range(ED.GetNumVWireSignals()):
      vws = ED.GetVWireSignal(j)
      if ROOT.EXOMiscUtil.GetTPCSide(vws.fChannel) != detHalf:
        continue
      venergy += vws.fCorrectedMagnitude
    if(uenergy > 0 and venergy > 0):
      hist1.Fill(uenergy,venergy)

  canvas1 = ROOT.TCanvas("canvas1")
  canvas1.SetLogz()
  hist1.Draw("colz")
  answer = ""
  while not answer in ["Y","y","N","n"]:
    answer = raw_input("Do you want to save the histogram? (Y/N): ")
  if answer in ["Y","y"]:
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    hist1.Write(key)

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("usage: " + sys.argv[0] + " filename DetectorHalf")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]))
