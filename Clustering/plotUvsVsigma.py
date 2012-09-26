import ROOT,sys

def main(filename):
  f = ROOT.TFile(filename,"UPDATE")
  f.ls()
  hist = None
  while hist == None:
    key = raw_input("Key for histogram to calculate on: ")
    hist = f.Get(key)
  hSigma = hist.ProjectionX()
  hSigma.SetName("hSigma")
  for i in range(1,hist.GetNbinsX()+1):
    proj = hist.ProjectionY("proj",i,i)
    hSigma.SetBinContent(i,proj.GetRMS())
  hSigma.Draw()
  answer = ""
  while not contains(answer,["Y","y","N","n"]):
    answer = raw_input("Do you want to save the histogram? (Y/N): ")
  if contains(answer,["Y","y"]):
    key = raw_input("Please enter object key: ")
    hSigma.Write(key)
  f.Close()

def contains(str, set):
  for c in set:
    if c == str:
      return True
  return False

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " filename")
    sys.exit(1)
  main(sys.argv[1])
