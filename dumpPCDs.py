import ROOT,sys

def main(filename,outfilename = "PCDdump.dat"):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  t.Add(filename)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  f = open(outfilename,'w')
  f.write("Event\tX\tY\tZ\tEnergy\n")
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    for j in range(npcds):
      pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(j)
      enum = ED.fEventNumber
      energy = pcd.fTotalEnergy
      x = pcd.GetPixelCenter().GetX()
      y = pcd.GetPixelCenter().GetY()
      z = pcd.GetPixelCenter().GetZ()
      f.write(str(enum) + "\t" + str(x) + "\t" + str(y) + "\t" + str(z) + "\t" + str(energy) + "\n")
  f.close()

if __name__ == "__main__":
  if len(sys.argv) not in [2,3]:
    print("usage: " + sys.argv[0] + " infile [outfile]")
    sys.exit(1)
  if len(sys.argv) == 2:
    main(sys.argv[1])
  else:
    main(sys.argv[1],sys.argv[2])
