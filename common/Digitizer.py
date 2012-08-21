import ROOT

class Digitizer:
  def __init__(self,wiredifftimes=[],wireinttimes=[],apddifftimes=[],apdinttimes=[]):
    self.electronics = ROOT.EXOElectronics()
    self.energysmearer = ROOT.EXOSmearMCIonizationEnergy()
    for channel in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE):
      transfer = ROOT.EXOTransferFunction()
      for time in wiredifftimes:
        transfer.AddDiffStageWithTime(time*ROOT.CLHEP.microsecond)
      for time in wireinttimes:
        transfer.AddIntStageWithTime(time*ROOT.CLHEP.microsecond)
      self.electronics.SetTransferFunctionForChannel(channel,transfer)
    for channel in range(ROOT.NCHANNEL_PER_WIREPLANE*ROOT.NWIREPLANE , ROOT.NUMBER_READOUT_CHANNELS):
      transfer = ROOT.EXOTransferFunction()
      for time in apddifftimes:
        transfer.AddDiffStageWithTime(time*ROOT.CLHEP.microsecond)
      for time in apdinttimes:
        transfer.AddIntStageWithTime(time*ROOT.CLHEP.microsecond)
      self.electronics.SetTransferFunctionForChannel(channel,transfer)
    self.electronics.SetNoiseAmplitudeForWires(0.0)
    self.electronics.SetNoiseAmplitudeForAPDs(0.0)
    self.digi = ROOT.EXODigitizer()
    self.digi.SetElectronics(self.electronics)
    self.digi.set_nsample(2048)
    self.digi.set_digitize_apds(True)
    self.digi.set_digitize_induction(True)
    self.digi.set_digitize_wires(True)
    self.digi.set_electron_lifetime(1e6*ROOT.CLHEP.microsecond)
    self.digi.set_drift_velocity(0.28*ROOT.CLHEP.cm/ROOT.CLHEP.microsecond)
    self.digi.set_collection_drift_velocity(0.0)
    self.digi.set_trigger_time(ROOT.TRIGGER_TIME)
    self.energysmearer.SetLXeEnergyResolution(0.02)

  def ProcessEvent(self,ED):
    ED.GetWaveformData().Clear( "C" )
    self.energysmearer.ApplySmear(ED.fMonteCarloData)
    self.digi.Digitize(ED.GetWaveformData(),ED.fMonteCarloData)
