import ROOT,sys

def main(filenames):
  ROOT.gSystem.Load("libEXOUtilities")

  selection = ROOT.TEntryList()

  t = ROOT.TChain("tree")
  for f in filenames:
    t.Add(f)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    UonlyClusters = []
    VonlyClusters = []
    for j in range(ED.GetNumChargeClusters()):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fRawEnergy) < 0.000001:
        VonlyClusters.append(cc)
      elif abs(cc.fAmplitudeInVChannels) < 0.000001:
        UonlyClusters.append(cc)

    done = False
    for uc in UonlyClusters:
      if done:
        break
      for vc in VonlyClusters:
        timediff = (uc.fCollectionTime - vc.fCollectionTime) / 1000
        if timediff > -4. and timediff < 4.:
          selection.Enter(i)
          print(ED.fEventNumber)
          done = True
          break

  infiles = raw_input("Enter files that contain the waveforms: ")
  outfile = raw_input("Enter output file: ")
  SaveSelection(selection,infiles,outfile)

def SaveSelection(selection,infiles,outfile):
  t = ROOT.TChain("tree")
  t.Add(infiles)
  t.SetEntryList(selection)
  out = ROOT.TFile(outfile,"RECREATE")
  copy = t.CopyTree("")
  copy.Write()
  out.Close()

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])

