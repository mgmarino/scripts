import ROOT,sys

def main(files):
  ROOT.gSystem.Load("libEXOUtilities")
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  view3D = ROOT.EXO3DView()
  view3D.SetReflectorInvisible()
  view3D.SetFieldRingInvisible()
  view3D.SetAPDInvisible()
  view3D.SetVesselInvisible()
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)
  for i in range(t.GetEntries()):
    t.GetEntry(i)
    npcd = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
    for j in range(npcd):
      pcd = ED.fMonteCarloData.GetPixelatedChargeDeposit(j)
      view3D.Draw(pcd)
      raw_input("hit enter to continue")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])
