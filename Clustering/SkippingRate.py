import ROOT,sys

def main(t):
  h = ROOT.TH2D("h","h",20,-0.5,20.5,50,0,3000)
  h.GetXaxis().SetTitle("Number of U-wire signals")
  h.GetYaxis().SetTitle("Energy")
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  numTotalEvents = 0
  numBadEvents = 0
  numBadDuringSirenEvents = 0
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    if ED.fEventHeader.fTaggedAsNoise or ED.fEventHeader.fTaggedAsMuon:
      continue
    numTotalEvents += 1
    if ED.fSkippedByClustering:
      numBadEvents += 1
      energy = 0
      for uws in ED.GetUWireSignalArray():
        energy += uws.fCorrectedEnergy
      h.Fill(ED.GetNumUWireSignals(),energy)
      if ED.fEventHeader.fSirenActiveInCR:
        numBadDuringSirenEvents += 1
  print(str(float(numBadEvents)/float(numTotalEvents)*100.) + "% of events skipped by clustering.")
  print("During " + str(float(numBadDuringSirenEvents)/float(numBadEvents)*100.) + "% of skipped events the CR siren was active.")
  h.Draw("colz")
  raw_input("q")

if __name__ == "__main__":
  ROOT.gSystem.Load("libEXOCalibUtilities")
  chain = ROOT.TChain("tree")
  if len(sys.argv) == 1:
    ds = ROOT.EXORunInfoManager.GetDataSet("Data/Processed/processed","quality==\"GOLDEN\"&&run>=2464&&run<=3564")
    for run in ds:
      for f in run.GetRunFiles():
        print(f.GetFileLocation())
        chain.Add(f.GetFileLocation())
  else:
    for f in sys.argv[1:]:
      chain.Add(f)
  main(chain)
