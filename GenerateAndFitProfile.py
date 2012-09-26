import ROOT,sys

def main(filename):
  f = ROOT.TFile(filename)
  f.ls()
  key = raw_input("Please enter histogram key: ")
  hist = f.Get(key)
  prof = hist.ProfileX()
  c1 = ROOT.TCanvas()
  prof.Draw()
  low = input("enter fit range lower boundary: ")
  high = input("enter fit range upper boundary: ")
  prof.Fit("pol1","","",low,high)
  prof.GetListOfFunctions().Print()
  scale = 1./prof.GetListOfFunctions().At(1).GetParameter(1)
  scaleError = scale * prof.GetListOfFunctions().At(1).GetParError(1)
  print("Scale = " + str(scale) + " +- " + str(scaleError))
  c1.Update()
  answer = ""
  while not contains(answer,["Y","y","N","n"]):
    answer = raw_input("Do you want to save the profile? (Y/N): ")
  if contains(answer,["Y","y"]):
    Open = False
    while(not Open):
      out = raw_input("Please enter filename: ")
      outfile = ROOT.TFile(out,"UPDATE")
      Open = not outfile.IsZombie()
    key = raw_input("Please enter object key: ")
    prof.Write(key)

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
