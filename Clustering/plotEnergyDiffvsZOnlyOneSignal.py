import ROOT,sys

def main(filenames):
  ROOT.gSystem.Load("libEXOUtilities")

  hist1 = ROOT.TH2D("hist1","hist1",100,0,210,100,-1,1)
  hist1.GetXaxis().SetTitle("Z (mm)")
  hist1.GetYaxis().SetTitle("Relative V-energy difference")
  hist1.SetTitle("Single U-wire energy diff")

  t = ROOT.TChain("tree")
  for file in filenames:
    t.Add(file)
  ED = ROOT.EXOEventData()
  t.SetBranchAddress("EventBranch",ED)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    nuws = ED.GetNumUWireSignals()
    if nuws != 1:
      continue
    nsc = ED.GetNumScintillationClusters()
    if nsc != 1:
      continue
    uws = ED.GetUWireSignal(0)
    if uws.fTime < 120000.:
      continue

    sc = ED.GetScintillationCluster(0)

    venergy = 0
    for j in range(ED.GetNumVWireSignals()):
      vws = ED.GetVWireSignal(j)
      venergy += vws.fCorrectedMagnitude
    UtoV = UtoVenergy(uws.fCorrectedEnergy)
    energyDiff = (venergy - UtoV) / UtoV
    Z = CalculateZ(sc.fTime,uws.fTime)

    hist1.Fill(Z,energyDiff)

  canvas1 = ROOT.TCanvas("canvas1")
  canvas1.SetLogz()
  hist1.Draw("colz")
  canvas1.Update()
  raw_input("hit enter to quit")

def UtoVenergy(u):
  return u * 0.2378 - 30.79

def CalculateZ(scintTime, chargeTime):
    driftDist = 1.71 * (chargeTime - scintTime)/1000.
    return ROOT.CATHODE_APDFACE_DISTANCE - ROOT.APDPLANE_UPLANE_DISTANCE - driftDist

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])

