import ROOT,sys
from math import sqrt

def main(files):
  channels = range(0,38) + range(2*38,3*38)
  channelcounts = dict((c,[0,0.,0.]) for c in channels)
  lastsignal = dict((c,[-1,0.,0.]) for c in channels)
  eventcounts = 0
  for filename in files:
    f = ROOT.TFile(filename)
    tree = f.Get("tree")
    ED = ROOT.EXOEventData()
    tree.SetBranchAddress("EventBranch",ED)
    tree.BuildIndex("fEventNumber")
    rng = GetEventRange(tree)
    for i in range(rng[0],rng[1]):
      tree.GetEntryWithIndex(i)
      eventcounts += 1
      for cis in ED.GetChargeInjectionSignalArray():
        try:
          channelcounts[cis.fChannel][0] += 1
          channelcounts[cis.fChannel][1] += cis.fMagnitude
          channelcounts[cis.fChannel][2] += cis.fMagnitude**2
          if lastsignal[cis.fChannel][0] == ED.fEventNumber:
            print("Found additional signal at event "+str(ED.fEventNumber)+", channel "+str(cis.fChannel)+" with amplitude "+str(cis.fMagnitude)+" at time "+str(cis.fTime/1000.))
            print("Previous signal at this event / channel had amplitude "+str(lastsignal[cis.fChannel][1])+" at time "+str(lastsignal[cis.fChannel][2]/1000.))
          lastsignal[cis.fChannel] = [ED.fEventNumber,cis.fMagnitude,cis.fTime]
        except KeyError:
          pass
  for chan,val in channelcounts.iteritems():
    print("Channel "+str(chan)+": "+str(float(val[0])/float(eventcounts)*100.)+"% efficiency, "+str(val[1]/float(val[0]))+" +- "+str(sqrt(val[2]/val[0]-(val[1]/val[0])**2))+" ADC")

def GetEventRange(tree):
  crl = tree.GetUserInfo().Last()
  cr = GetFirstBeginSegmentCalibrationRecord(crl)
  crend = GetNextEndSegmentCalibrationRecord(crl,cr)
  while cr:
    if cr.GetDac() == 41024:
      return cr.GetPreviousEventNumber()+3,crend.GetPreviousEventNumber()-1
    cr = GetNextBeginSegmentCalibrationRecord(crl,cr)
    crend = GetNextEndSegmentCalibrationRecord(crl,cr)
  return None

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
    print("usage: "+sys.argv[0]+" file[s]")
    sys.exit(1)
  ROOT.gSystem.Load("libEXOUtilities")
  main(sys.argv[1:])
