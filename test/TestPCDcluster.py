import ROOT,sys
from Cluster import Cluster

def main(filename):
  ROOT.gSystem.Load("libEXOROOT")
  f = ROOT.TFile(filename)
  t = f.Get("tree")
  ED = ROOT.EXOEventData()
  cl = Cluster()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    cl.doit(ED)
    ncl = cl.GetNumClusters()
    print("Event " + str(ED.fEventNumber) + " has " + str(ED.fMonteCarloData.GetNumPixelatedChargeDeposits()) + "pcds and " + str(ncl) + " pcd clusters")
    for cluster in cl.clusters:
      print(cluster)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
