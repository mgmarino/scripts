import ROOT

class Pixelater:
  def __init__(self):
    self.eventData = ROOT.EXOEventData()
    self.pcds = []
    self.apdhits = []
    self.eventnumber = 1

  def AddPCD(self,x,y,z,time,energy):
    coord = ROOT.EXOCoordinates(ROOT.EXOMiscUtil.kXYCoordinates,x,y,z,time)
    self.AddPCDwithCoordinate(coord,energy)

  def AddPCDwithCoordinate(self,coord,energy):
    pcd = ROOT.EXOMCPixelatedChargeDeposit(coord)
    pcd.fTotalEnergy = energy*ROOT.CLHEP.keV
    pcd.fTotalIonizationEnergy = energy*ROOT.CLHEP.keV
    self.pcds.append(pcd)
    

  def AddAPDHit(self,gangNo,time,charge):
    apdhit = ROOT.EXOMCAPDHitInfo()
    apdhit.fGangNo = gangNo
    apdhit.fTime = time
    apdhit.fCharge = charge
    self.apdhits.append(apdhit)

  def GetEventData(self):
    self.eventData.Clear("C")
    mcdata = self.eventData.fMonteCarloData
    for pcd in self.pcds:
      newpcd = mcdata.FindOrCreatePixelatedChargeDeposit(pcd.GetPixelCenter())
      newpcd.fTotalEnergy = pcd.fTotalEnergy
      newpcd.fTotalIonizationEnergy = pcd.fTotalIonizationEnergy
    for apdhit in self.apdhits:
      mcdata.AddAPDHitInfo(apdhit)
    self.eventData.fEventNumber = self.eventnumber
    self.eventnumber += 1
    self.pcds = []
    self.apdhits = []
    return self.eventData
