import sys, os, re
from gpxtools import *

def findLargeTracks(filename, maxLen=500):
  try:
      tree0 = etree.parse(filename)
  except Exception as e:
      print "Could not parse GPX: %s" % e
      return False

  root = tree0.getroot()

  print "Number of tracks   : %d" % get_numtrk(root)
  print "Number of routes   : %d" % get_numrte(root)
  print "Number of waypoints: %d" % get_numwpt(root)
  print ''

  for trk in root.iterchildren(ns + 'trk'):
    name = get_name(trk)
    pts = get_numpts(trk)
    if pts > maxLen:
      print "Track name  : %s " % name
      n = 0
      trkd = 0
      for trkseg in trk.iterchildren(ns + 'trkseg'):
          numpts = len(list(trkseg))
          oldlat = None
          d = 0
          for trkpt in trkseg.iterchildren(ns + 'trkpt'):
              lat = float(trkpt.get('lat'))
              lon = float(trkpt.get('lon'))
              if oldlat != None:
                  d += distance(oldlat, oldlon, lat, lon)
              oldlat = lat
              oldlon = lon
          print "Segment %3d : %4d track points, distance: %d meter" % (n, numpts, d)
          n += 1
          trkd += d
      print ''

def splitLargeTracks(filename, maxLen=500):
  try:
      tree0 = etree.parse(filename)
  except Exception as e:
      print "Could not parse GPX: %s" % e
      return False

  root = tree0.getroot()
  treeOut = copy.deepcopy(tree0)
  rootOut = treeOut.getroot()

  print "Number of tracks   : %d" % get_numtrk(root)
  print "Number of routes   : %d" % get_numrte(root)
  print "Number of waypoints: %d" % get_numwpt(root)
  print ''

  for trk in root.iterchildren(ns + 'trk'):
    name = get_name(trk)
    pts = get_numpts(trk)
    if pts > maxLen:
      for trkOut in rootOut.iterchildren(ns + 'trk'):
        if pts == get_numpts(trkOut) and name == get_name(trk):
          rootOut.remove(trkOut)
          print " removed long track {}: {}".format(name, pts)
          break
      print "Track name  : %s " % name
      newNumTracks = pts/maxLen + 1
      print "# new Tracks: %d " % newNumTracks
      for nTrack in range(newNumTracks):
        treeC = copy.deepcopy(tree0)
        rootC = treeC.getroot()
        for trkC in rootC.iterchildren(ns + 'trk'):
          if not get_numpts(trkC) == pts:
            continue
          trkd = 0
          for n,trksegC in enumerate(trkC.iterchildren(ns + 'trkseg')):
              print " --- {} {} ---".format(n,nTrack)
              numpts = len(list(trksegC))
              oldlat = None
              d = 0
              numPts = 0
              for i,trkptC in enumerate(trksegC.iterchildren(ns + 'trkpt')):
                if nTrack*maxLen <= i and i < (nTrack+1)*maxLen:
                  lat = float(trkptC.get('lat'))
                  lon = float(trkptC.get('lon'))
                  if oldlat != None:
                      d += distance(oldlat, oldlon, lat, lon)
                  oldlat = lat
                  oldlon = lon
                else:
                  trksegC.remove(trkptC)
              print "  %4d track points, distance: %d meter" % (numpts, d)
              trkd += d
          set_name(trkC, get_name(trkC)+" - {}/{}".format(
            nTrack+1, newNumTracks))
          rootOut.append(copy.deepcopy(trkC))
        print ''
#        fname = filename+"_{}.gpx".format(nTrack)
#        treeC.write(fname, xml_declaration = True, encoding='utf-8')
#        info(fname)
      fname = filename[:-4]+"_splitIntoMax{}PtTracks.gpx".format(maxLen)
      treeOut.write(fname, xml_declaration = True, encoding='utf-8')
      info(fname)

#if filename is None:
#  try:
#      filename = sys.argv[1]
#  except Exception:
#      print "Usage: gpx-info <filename>"
#      print "Show info about the contents of <filename>"
#      sys.exit(1)
PCT=False
AT=True

# AT
if AT:
  for sections in ["/home/jstraub/Downloads/AT/"]:
    for root, dirs, files in os.walk(sections):
      for filename in files:
        print filename
        if filename.endswith("gpx"):
          splitLargeTracks(os.path.join(root,filename))

# PCT
if PCT:
  filename = "../ca_section_a_gps/CA_Sec_A_tracks.gpx"
  filename = "../ca_state_gps/CA_Sec_A_tracks.gpx"
  
  for sections in ["../ca_state_gps","../or_state_gps","../wa_state_gps"]:
    for root, dirs, files in os.walk(sections):
      for filename in files:
        if re.search("tracks.gpx", filename):
          splitLargeTracks(os.path.join(root,filename))
  
  
