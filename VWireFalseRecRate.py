# This script calculates the probability of falsely reconstructing a V-wire signal,
# I.e. the probability of HAVING AN EVENT with reconstructed V-wire signal although
# the waveforms contain just noise.
# As input a file containing digitized waveforms without signals (just noise) is assumed.

import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  falsecounter = 0
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    if ED.GetNumVWireSignals():
      falsecounter += 1
  ratio = float(falsecounter) / float(t.GetEntries())
  print("Probability of having an event with falsely reconstructed V-wire signal: " + str(100*ratio) + "%")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
