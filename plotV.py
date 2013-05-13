from __future__ import with_statement
import ROOT,sys

def main(t):
  t.Draw("fChargeClusters.fV>>h(800,-200,200)")
  raw_input("quit")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" filelist.dat")
    print("\nfilelist.dat should contain a list of ROOT files to process")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  with open(sys.argv[1]) as f:
    for line in f:
      t.Add(line[:-1])
  print("Chain contains "+str(t.GetNtrees())+" trees")
  main(t)
