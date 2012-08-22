import ROOT
from numpy import array
from math import sqrt

class Cluster:
  def __init__(self):
    self.clusters = [[]]
    self.driftVelocity = 0.00171
    self.clusterDist = 15.

  def setClusterRadius(self,dist):
    self.clusterDist = dist

  def reset(self):
    self.clusters = []

  def  doit(self,ED):
    self.reset()
    mcd = ED.fMonteCarloData
    for i in range(mcd.GetNumPixelatedChargeDeposits()):
      pcd = mcd.GetPixelatedChargeDeposit(i)
      coordinate = pcd.GetPixelCenter()
      pos = array([coordinate.GetU(),coordinate.GetV(),coordinate.GetT()])
      self.pickBestFriend(pos)

  def GetNumClusters(self):
    return len(self.clusters)

  def pickBestFriend(self,pos):
    mindist = 1000000.
    min = 0
    for i,cluster in enumerate(self.clusters):
      if cluster == []:
        continue
      clusterpos = self.AveragePos(cluster)
      dist = sqrt((clusterpos[0]-pos[0])**2 + (clusterpos[1]-pos[1])**2 + self.driftVelocity**2 * (clusterpos[2]-pos[2])**2)
      #xydist = sqrt((clusterpos[0]-pos[0])**2 + (clusterpos[1]-pos[1])**2)
      #zdist = sqrt(self.driftVelocity**2 * (clusterpos[2]-pos[2])**2)
      #print("xydist = " + str(xydist) + ", zdist = " + str(zdist))
      if dist < mindist:
        mindist = dist
        min = i
    print("mindist = " + str(mindist))
    if mindist < self.clusterDist:
      self.clusters[i].append(pos)
    else:
      self.clusters.append([pos])

  def AveragePos(self,cluster):
    pos = array([0,0,0])
    for coordinate in cluster:
      pos += coordinate
    size = float(len(cluster))
    return pos/size
