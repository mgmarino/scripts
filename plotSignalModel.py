import ROOT

def main():
  ROOT.gSystem.Load("libEXOROOT")
  tf = ROOT.EXOTransferFunction()
  tf.AddIntegStageWithTime(1500)
  tf.AddIntegStageWithTime(1500)
  tf.AddDiffStageWithTime(40000)
  tf.AddDiffStageWithTime(40000)
  tf.AddDiffStageWithTime(60000)
  smb = ROOT.EXOInductionSignalModelBuilder(tf,0.171*ROOT.CLHEP.cm/ROOT.CLHEP.microsecond,0.225*ROOT.CLHEP.cm/ROOT.CLHEP.microsecond)
  smm = ROOT.EXOSignalModelManager()
  smm.BuildSignalModelForChannelOrTag(0,smb)
  sm = smm.GetSignalModelForChannelOrTag(0)
  wf = sm.GetModelWaveform()
  wf.GimmeHist().Draw()
  raw_input("hit enter to quit")

if __name__ == "__main__":
  main()
