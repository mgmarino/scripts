import ROOT,sys,os

def GetFilesIn(basedir,minrun,maxrun):
  expandtop = os.path.expandvars(basedir)
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

def GetRunTypeSourceTypeAndPosition(file):
  f = ROOT.TFile(file)
  t = f.Get("tree")
  rec = t.GetUserInfo().Last().GetNextRecord('EXOBeginRecord')()
  flavor =  rec.GetRunFlavor()
  if flavor == ROOT.EXOBeginRecord.kDatSrcClb:
    sourcerec = ROOT.EXOBeginSourceCalibrationRunRecord()
    t.GetUserInfo().Last().GetNextRecord(sourcerec, ROOT.EXOBeginSourceCalibrationRunRecord.Class())
    source = sourcerec.GetSourceType()
    pos = sourcerec.GetSourcePosition()
    return flavor, source, pos
  return flavor, None, None

def GetRunType(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  return flavor

def IsPhysics(file):
  flavor = GetRunType(file)
  return flavor == ROOT.EXOBeginRecord.kDatPhysics

def IsSource(file):
  flavor = GetRunType(file)
  return flavor == ROOT.EXOBeginRecord.kDatSrcClb

def IsThorium(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  if flavor != ROOT.EXOBeginRecord.kDatSrcClb:
    return False
  if source not in [ROOT.EXOBeginSourceCalibrationRunRecord.kThStrong,ROOT.EXOBeginSourceCalibrationRunRecord.kThWeak]:
    return False
  return True

def IsCobalt(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  if flavor != ROOT.EXOBeginRecord.kDatSrcClb:
    return False
  if source not in [ROOT.EXOBeginSourceCalibrationRunRecord.kCoStrong,ROOT.EXOBeginSourceCalibrationRunRecord.kCoWeak]:
    return False
  return True

def IsStrongTh(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  if flavor != ROOT.EXOBeginRecord.kDatSrcClb:
    return False
  if source != ROOT.EXOBeginSourceCalibrationRunRecord.kThStrong:
    return False
  return True

def IsWeakThAnode(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  if flavor != ROOT.EXOBeginRecord.kDatSrcClb:
    return False
  if source != ROOT.EXOBeginSourceCalibrationRunRecord.kThWeak:
    return False
  if pos not in [ROOT.EXOBeginSourceCalibrationRunRecord.kP2_pz, ROOT.EXOBeginSourceCalibrationRunRecord.kP2_nz]:
    return False
  return True

def IsWeakThCathode(file):
  flavor, source, pos = GetRunTypeSourceTypeAndPosition(file)
  if flavor != ROOT.EXOBeginRecord.kDatSrcClb:
    return False
  if source != ROOT.EXOBeginSourceCalibrationRunRecord.kThWeak:
    return False
  if pos not in [ROOT.EXOBeginSourceCalibrationRunRecord.kP4_px, ROOT.EXOBeginSourceCalibrationRunRecord.kP4_py, ROOT.EXOBeginSourceCalibrationRunRecord.kP4_ny]:
    return False
  return True
