import ROOT,sys

def main(filenames):
  ROOT.gSystem.Load("libEXOUtilities")

  hist1 = ROOT.TH2D("hist1","X Y position of PCDs in events with unclustered clusters",100,-300,300,100,-200,200)
  hist1.GetXaxis().SetTitle("X")
  hist1.GetYaxis().SetTitle("Y")
  
  t = ROOT.TChain("tree")
  for f in filenames:
    t.Add(f)

  for i in range(t.GetEntries()):
    t.GetEntry(i)
    ED = t.EventBranch
    notClustered = False
    for j in range(ED.GetNumChargeClusters()):
      cc = ED.GetChargeCluster(j)
      if abs(cc.fX) > 200:
        notClustered = True
        break
    if notClustered:
      npcds = ED.fMonteCarloData.GetNumPixelatedChargeDeposits()
      for j in range(npcds):
        for pcd in ED.fMonteCarloData.GetPixelatedChargeDepositsArray():
          coord = pcd.GetPixelCenter()
          hist1.Fill(coord.GetX(),coord.GetY())

  canvas1 = ROOT.TCanvas("canvas1")
  hist1.Draw("colz")
  raw_input("hit enter to quit")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " file(s)")
    sys.exit(1)
  main(sys.argv[1:])

