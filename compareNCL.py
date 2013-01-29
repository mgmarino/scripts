import ROOT,sys,os

def GetFiles(top,minrun,maxrun):
  expandtop = os.path.expandvars(top)
  paths = []
  for root, dirs, files in os.walk(expandtop):
    try:
      run = int(root[-4:])
    except(ValueError):
      continue
    if run < minrun or run > maxrun:
      continue
    for file in files:
      path = os.path.join(root,file)
      if not ".root" == path[-5:]:
        continue
      paths.append(path)
  return paths

def GetRunType(file):
  f = ROOT.TFile(file)
  t = f.Get("tree")
  rec = t.GetUserInfo().Last().GetNextRecord('EXOBeginRecord')()
  return rec.GetRunFlavor()

def IsPhysics(file):
  return GetRunType(file) == ROOT.EXOBeginRecord.kDatPhysics

def IsSource(file):
  return GetRunType(file) == ROOT.EXOBeginRecord.kDatSrcClb

def Process(old,new,minrun,maxrun):
  oldfiles = filter(IsPhysics,GetFiles(old,minrun,maxrun))
  newfiles = filter(IsPhysics,GetFiles(new,minrun,maxrun))
  oldhist = GetHist(oldfiles,"old")
  newhist = GetHist(newfiles,"new")
  newhist.SetLineColor(ROOT.kRed)
  oldhist.Draw()
  newhist.Draw("same")
  raw_input("hit enter to quit")

def GetHist(files,name):
  t = ROOT.TChain("tree")
  for f in files:
    t.Add(f)
  t.Draw("@fChargeClusters.size()>>"+name+"(10,0,10)","","")
  return ROOT.gDirectory.Get(name)


if __name__ == "__main__":
  ROOT.gSystem.Load("libEXOUtilities")
  Process("$EXODATA3/Archived/masked_1_9_13","$EXODATA3/masked",4600,4640)
