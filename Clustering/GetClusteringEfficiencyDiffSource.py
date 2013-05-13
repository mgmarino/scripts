import ROOT,sys,array

lowerLimit = 705.
upperLimit = 2705.
step = 10.

def main(dataF,mcF):
  ssRateData = dataF.Get("rateSSZcut")
  ssRateMC = mcF.Get("rateSSZcut")
  msRateData = dataF.Get("rateMStotalZcut")
  msRateMC = mcF.Get("rateMStotalZcut")
  ssSpectrumData = dataF.Get("hSSfullZcut")
  msSpectrumData = dataF.Get("hMSTotalfullZcut")
  ssSpectrumMC = mcF.Get("hSSfullZcut")
  msSpectrumMC = mcF.Get("hMSTotalfullZcut")

  IntSSdata = WeightedIntegral(ssRateData,ssSpectrumData)
  IntSSmc = WeightedIntegral(ssRateMC,ssSpectrumMC)
  IntMSdata = WeightedIntegral(msRateData,msSpectrumData)
  IntMSmc = WeightedIntegral(msRateMC,msSpectrumMC)

  print("Data SS 2D efficiency between 700 and 2710 keV: " + str(IntSSdata/(upperLimit - lowerLimit)))
  print("MC SS 2D efficiency between 700 and 2710 keV: " + str(IntSSmc/(upperLimit - lowerLimit)))
  print("Data MS 2D efficiency between 700 and 2710 keV: " + str(IntMSdata/(upperLimit - lowerLimit)))
  print("MC MS 2D efficiency between 700 and 2710 keV: " + str(IntMSmc/(upperLimit - lowerLimit)))

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
  if len(sys.argv) != 3:
    print("usage: "+sys.argv[0]+" DataFile MCFile")
    sys.exit(1)
  dataF = ROOT.TFile(sys.argv[1])
  mcF = ROOT.TFile(sys.argv[2])
  main(dataF,mcF)
