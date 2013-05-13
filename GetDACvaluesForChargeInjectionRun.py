import ROOT,sys

def main(tree):
  ED = ROOT.EXOEventData()
  tree.SetBranchAddress("EventBranch",ED)
  tree.BuildIndex("fEventNumber")
  crl = tree.GetUserInfo().Last()
  cr = GetFirstBeginSegmentCalibrationRecord(crl)
  crend = GetNextEndSegmentCalibrationRecord(crl,cr)
  while cr:
    print(cr.GetIdentifier(),cr.GetDac(),cr.GetPreviousEventNumber(),crend.GetPreviousEventNumber())
    print(40*"-")
    numCis = 0
    mag = 0.0
    for i in range(cr.GetPreviousEventNumber()+2,crend.GetPreviousEventNumber()+1):
      tree.GetEntryWithIndex(i)
      for cis in ED.GetChargeInjectionSignalArray():
        if cis.fChannel == 0:
          numCis += 1
          mag += cis.fMagnitude
    print(numCis,mag/numCis)
    print(40*"-")
    cr = GetNextBeginSegmentCalibrationRecord(crl,cr)
    crend = GetNextEndSegmentCalibrationRecord(crl,cr)

def GetFirstBeginSegmentCalibrationRecord(crl):
  cr = crl.GetNextRecord('EXOControlRecord')()
  return GetNextBeginSegmentCalibrationRecord(crl,cr)

def GetNextBeginSegmentCalibrationRecord(crl,cr):
  if not cr:
    return None
  cr = crl.GetNextRecord('EXOControlRecord')(cr)
  while not isinstance(cr,ROOT.EXOBeginSegmentInternalCalibrationRunRecord):
    if isinstance(cr,ROOT.EXOEndInternalCalibrationRunRecord):
      return None
    cr = crl.GetNextRecord('EXOControlRecord')(cr)
  return cr

def GetNextEndSegmentCalibrationRecord(crl,cr):
  if not cr:
    return None
  cr = crl.GetNextRecord('EXOControlRecord')(cr)
  while not isinstance(cr,ROOT.EXOEndSegmentInternalCalibrationRunRecord):
    if isinstance(cr,ROOT.EXOEndInternalCalibrationRunRecord):
      return None
    cr = crl.GetNextRecord('EXOControlRecord')(cr)
  return cr

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: "+sys.argv[0]+" file")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  f = ROOT.TFile(sys.argv[1])
  t = f.Get("tree")
  main(t)
