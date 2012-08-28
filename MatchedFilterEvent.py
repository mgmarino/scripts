# this script shows the matched filter output of a specific waveform
import ROOT,sys

def main(filename):
  ROOT.gSystem.Load("libEXOUtilities")
  ROOT.gStyle.SetOptStat(0)

  uTransfer = ROOT.EXOTransferFunction()
  uTransfer.AddDiffStageWithTime(40e3)
  uTransfer.AddDiffStageWithTime(40e3)
  uTransfer.AddDiffStageWithTime(77.29e3)
  uTransfer.AddIntegStageWithTime(1.5e3)
  uTransfer.AddIntegStageWithTime(1.5e3)
  uSigModBuilder = ROOT.EXOUWireSignalModelBuilder(uTransfer)
  uSigModel = ROOT.EXOSignalModel()
  uSigModBuilder.InitializeSignalModelIfNeeded(uSigModel,0)
  modelWaveform = uSigModel.GetModelWaveform()
  modelWaveform.SetLength(350)

  c1 = ROOT.TCanvas("c1","c1")
  hist = modelWaveform.GimmeHist()
  hist.SetTitle("Matched filter model")
  hist.Draw()
  c1.Update()
  raw_input("hit enter to continue")

  matchedFilter = ROOT.EXOMatchedFilter()
  matchedFilter.SetTemplateToMatch(modelWaveform,2048,50)
  f = ROOT.TFile(filename)
  t = f.Get("tree")
  events = [(6708,3),(263,82),(812,106)]
  t.BuildIndex("fEventNumber")
  eventvalue = ""
  while (eventvalue != "q" and eventvalue != "Q"):
    eventvalue = raw_input("Enter Event ('q' to quit): ")
    event,channel = 0,0
    try:
      event = int(eventvalue)
    except ValueError, TypeError:
      continue
    channelvalue = raw_input("Enter Channel: ")
    try:
      channel = int(channelvalue)
    except ValueError, TypeError:
      continue

    t.GetEntryWithIndex(event)
    print("Displaying Event " + str(t.EventBranch.fEventNumber) + ", Channel " + str(channel))
    t.EventBranch.GetWaveformData().Decompress()
    intwf = t.EventBranch.GetWaveformData().GetWaveformWithChannel(channel)
    wf = ROOT.EXODoubleWaveform(intwf)
    hist = wf.GimmeHist()
    hist.SetTitle("raw waveform run " + str(t.EventBranch.fRunNumber) + ", event " + str(event) + ", channel " + str(channel))
    hist.Draw()
    c1.Update()
    raw_input("hit enter to continue")
    mfwf = ROOT.EXODoubleWaveform()
    matchedFilter.Transform(wf,mfwf)
    hist = mfwf.GimmeHist()
    hist.SetTitle("matched filter run " + str(t.EventBranch.fRunNumber) + ", event " + str(event) + ", channel " + str(channel))
    hist.Draw()
    c1.Update()
    raw_input("hit enter to continue")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
