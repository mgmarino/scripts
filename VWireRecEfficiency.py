# This script calculates the probability of reconstructing a V-wire signal
# vs original energy. As input a file containing digitized waveforms
# with one v-wire signal per event is assumed.

import ROOT,sys

def main(filename,nbins,rng):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  binstring = str(nbins)
  hist = ROOT.TH1D("hist","V-wire reconstruction efficiency",nbins,0,rng)
  hist.GetXaxis().SetTitle("simulated Energy (keV)")
  hFull = ROOT.TH1D("hFull","",nbins,0,rng)
  hGood = ROOT.TH1D("hGood","",nbins,0,rng)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    energy = 0.
    channels = set()
    for j in range(npcds):
      pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(j)
      energy += pcd.fTotalEnergy
      channels = channels.union(set([ch for ch in pcd.fWireChannelsAffected]))
    energy *= 1000.
    hFull.Fill(energy)
    nvws = ED.GetNumVWireSignals()
    foundchannel = False
    for j in range(nvws):
      vws = ED.GetVWireSignal(j)
      if vws.fChannel in channels:
        foundchannel = True
    if foundchannel:
      hGood.Fill(energy)
  hFull.Sumw2()
  hGood.Sumw2()
  hist.Divide(hGood,hFull,1,1,"B")
  hist.Draw("E")
  answer = ""
  while not contains(answer,["Y","y","N","n"]):
    answer = raw_input("Do you want to save the histogram? (Y/N): ")
  if contains(answer,["Y","y"]):
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    hist.Write(key)

def contains(str, set):
  for c in set:
    if c == str:
      return True
  return False

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("usage: " + sys.argv[0] + " filename nbins range")
    sys.exit(1)
  main(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
