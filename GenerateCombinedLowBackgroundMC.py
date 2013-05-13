import ROOT,sys,os

def main(FitResult):
  components = GetComponents(FitResult)
  PrintComponents(components)
  GenerateMixedTree(components,300000)

def GetComponents(FitResult):
  components = {"num_ActiveLXe_Rn222" : [0.0,"ActiveLXe_Rn222/"],
                "num_ActiveLXe_Xe135" : [0.0,"ActiveLXe_Xe135/"],
                "num_AirGap_214_Bi_nochain" : [0.0,"AirGap_214_Bi_nochain/"],
                "num_AllVessel_Co60" : [0.0,"AllVessel_Co60/"],
                "num_AllVessel_K40" : [0.0,"AllVessel_K40/"],
                "num_AllVessel_Th232" : [0.0,"AllVessel_Th232/"],
                "num_AllVessel_U238" : [0.0,"AllVessel_U238/"],
                "num_AllVessel_Zn65" : [0.0,"AllVessel_Zn65/"],
                "num_CathodeSurf_Bi214_nochain" : [0.0,"CathodeSurf_Bi214_nochain/"],
                "num_InactiveLXe_Rn222" : [0.0,"InactiveLXe_Rn222/"],
                "num_bb2n" : [0.0,"bb2n/"]}
  params = FitResult.floatParsFinal()
  for key in components:
    components[key][0] = int(params[params.index(key)].getVal())
  return components

def GenerateMixedTree(components,numEvents):
  mcBaseDir = "/nfs/slac/g/exo_data2/exo_data/data/MC/P3_LB/"
  chain = ROOT.TChain("tree")
  sumComponents = GetSumOfComponents(components)
  i = 0
  for key,value in components.iteritems():
    numEntries = int(float(value[0])/float(sumComponents)*float(numEvents))
    tree = ROOT.TChain("tree")
    tree.Add(mcBaseDir+value[1]+"*.root")
    filename = "mergefile"+str(i)+".root"
    f = ROOT.TFile(filename,"RECREATE")
    outtree = tree.CloneTree(numEntries)
    print("Should have added "+str(numEntries)+" entries")
    print("Clonetree has "+str(outtree.GetEntries())+" entries")
    f.Write()
    f.Close()
    chain.Add(filename)
    print("Chain has "+str(chain.GetEntries())+" entries")
    print("")
    i += 1
  chain.Merge("CombinedLBMC.root")
  for j in range(i):
    os.remove("mergefile"+str(j)+".root")

def GetSumOfComponents(components):
  sum = 0
  for key,value in components.iteritems():
    sum += value[0]
  return sum

def PrintComponents(components):
  for key,value in components.iteritems():
    print(key+": "+str(value[0]))

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" FitResultFile")
    sys.exit(1)
  ROOT.gSystem.Load("$EXODIR/wolfhart/EXO_Fitting_svn/branches/EXO_Fitting_3rdAnalysis_RC/EXO_Fitting/lib/libEXOFitting")
  f = ROOT.TFile(sys.argv[1])
  wsp2 = f.Get("wsp2")
  FitResult = wsp2.genobj("nll")
  main(FitResult)
