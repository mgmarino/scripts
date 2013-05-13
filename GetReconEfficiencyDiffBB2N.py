import ROOT,sys

lowerLimit = 705.
upperLimit = 2195.
step = 10.

def main(dataF,mcF,spectrumF):
  rateVZcutData = dataF.Get("rateVZcut")
  rateVZcutMC = mcF.Get("rateVZcut")
  rateScintNorthData = dataF.Get("rateScintNorth")
  rateScintNorthMC = mcF.Get("rateScintNorth")
  rateScintSouthData = dataF.Get("rateScintSouth")
  rateScintSouthMC = mcF.Get("rateScintSouth")

  spectrumV = spectrumF.Get("hVallZcut")
  spectrumNorth = spectrumF.Get("hScintallNorth")
  spectrumSouth = spectrumF.Get("hScintallSouth")

  IntVZcutData = WeightedIntegral(rateVZcutData,spectrumV)
  IntVZcutMC = WeightedIntegral(rateVZcutMC,spectrumV)
  IntScintNorthData = WeightedIntegral(rateScintNorthData,spectrumNorth)
  IntScintNorthMC = WeightedIntegral(rateScintNorthMC,spectrumNorth)
  IntScintSouthData = WeightedIntegral(rateScintSouthData,spectrumSouth)
  IntScintSouthMC = WeightedIntegral(rateScintSouthMC,spectrumSouth)

  print("Data V reconstruction efficiency between 700 and 2200 keV: " + str(IntVZcutData/(upperLimit-lowerLimit)))
  print("MC V reconstruction efficiency between 700 and 2200 keV: " + str(IntVZcutMC/(upperLimit-lowerLimit)))
  print("Data TPC1 scintillation reconstruction efficiency between 700 and 2200 keV: " + str(IntScintNorthData/(upperLimit-lowerLimit)))
  print("MC TPC1 scintillation reconstruction efficiency between 700 and 2200 keV: " + str(IntScintNorthMC/(upperLimit-lowerLimit)))
  print("Data TPC2 scintillation reconstruction efficiency between 700 and 2200 keV: " + str(IntScintSouthData/(upperLimit-lowerLimit)))
  print("MC TPC2 scintillation reconstruction efficiency between 700 and 2200 keV: " + str(IntScintSouthMC/(upperLimit-lowerLimit)))

def WeightedIntegral(graph,weightHist):
  sum = 0.0
  j = 0
  x1 = lowerLimit
  while x1 < upperLimit-1.:
    x2 = x1+step
    y1 = graph.Eval(x1)
    y2 = graph.Eval(x2)
    weight = (weightHist.GetBinContent(j+70)+weightHist.GetBinContent(j+70+1))/2.
    sum += step * (y1+y2)/2 * weight
    j += 1
    x1 = x2
  weightIntegral = WeightSum(weightHist,j)
  print("Sum = "+str(sum)+", weightIntegral = "+str(weightIntegral))
  return sum*j/weightIntegral

def WeightSum(hist,nBins):
  sum = 0.0
  for i in range(70,70+nBins):
    sum += (hist.GetBinContent(i) + hist.GetBinContent(i+1))/2.
  return sum

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("usage: "+sys.argv[0]+" DataFile MCFile BB2NMCFile")
    sys.exit(1)
  dataF = ROOT.TFile(sys.argv[1])
  mcF = ROOT.TFile(sys.argv[2])
  spectrumF = ROOT.TFile(sys.argv[3])
  main(dataF,mcF,spectrumF)
