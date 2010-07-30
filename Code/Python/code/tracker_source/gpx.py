from datatypes import *
from XmlParser import *
import os
from osal import *

class GPXFile(file):
    def __init__(self,name,mode):
        if mode == "w":
            file.__init__(self,name,mode)
            self.parser=None
            self.write("<gpx\n")
            self.write("  version=\"1.0\"\n")
            self.write("  creator=\"Tracker.py 0.20 - http://tracker-py.googlecode.com\"\n")
            self.write("  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
            self.write("  xmlns=\"http://www.topografix.com/GPX/1/0\"\n")
            self.write("  xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http:/www.topografix.com/GPX/1/0/gpx.xsd\">\n")
            print "Opening gpx file %s for writing" % name
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(name)
            print "Opening gpx file %s for reading" % name
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</gpx>")
            file.close(self)

    def __writeTrackpoint__(self,point,time=None):
        lat,lon,alt = eval(point)
        self.write("        <trkpt lat=\"%f\" lon=\"%f\"><ele>%f</ele>" % (lat,lon,alt))
        if time != None:
            self.write("<time>%s</time>" % time)
        self.write("</trkpt>\n")

    def writeWaypoint(self,waypoint):
        self.write("<wpt lat=\"%f\" lon=\"%f\"><ele>%f</ele><name>%s</name></wpt>\n" %
                   (waypoint.latitude, waypoint.longitude, waypoint.altitude, waypoint.name) )

    def writeTrack(self,track):
        self.write("<trk><name>%s</name>\n" % track.name)
        self.write("    <trkseg>\n")

        keys = track.data.keys()
        if "name" in keys:
            keys.remove("name")

        keys.sort()
        for key in keys:
            self.__writeTrackpoint__(track.data[key],key)
        self.write("    </trkseg>\n")
        self.write("</trk>\n")

    def __writeRoutepoint__(self,point,time=None):
        lat,lon,alt = eval(point)
        self.write("    <rtept lat=\"%f\" lon=\"%f\"><ele>%f</ele>" % (lat,lon,alt))
        if time != None:
            self.write("<time>%s</time>" % time)
        self.write("</rtept>\n")

    def writeRoute(self,route):
        self.write("<rte><name>%s</name>\n" % route.name)
        keys = route.data.keys()
        keys.remove("name")
        keys.sort()
        for key in keys:
            self.__writeRoutepoint__(route.data[key])
        self.write("</rte>\n")



    def GetWaypointNodes(self):
        if self.parser.root == None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'wpt' not in keys:
            print "no waypoints found"
            return

        return self.parser.root.childnodes['wpt']

    def GetWaypoint(self,node):

        lat = eval(node.properties['lat'])
        lon = eval(node.properties['lon'])
        keys = node.childnodes.keys()
        if 'name' in keys:
            name = node.childnodes['name'][0].content
            #print "importing waypoint %s" % name
        else:
            name = ''
            print "name tag not found"

        if 'ele' in keys:
            alt = eval(node.childnodes['ele'][0].content)
            w=Waypoint(name,lat,lon,alt)
        else:
            w=Waypoint(name,lat,lon)

        return w


    def GetRouteNodes(self):
        if self.parser.root == None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'rte' not in keys:
            print "no routes found"
            return

        return self.parser.root.childnodes['rte']


    def GetRouteName(self,node):
        keys = node.childnodes.keys()
        if 'name' in keys:
            return node.childnodes['name'][0].content


    def GetRoutePoints(self,route,node):
        osal = Osal.GetInstance()
        reftime = osal.GetTime()
        for rtept in node.childnodes['rtept']:

            lat = rtept.properties['lat']
            lon = rtept.properties['lon']
            keys = rtept.childnodes.keys()
            if 'time' in keys:
                time = rtept.childnodes['time'][0].content
            else:
                time = osal.GetIsoTime(reftime)
                reftime += 1

            keys = rtept.childnodes.keys()
            if 'ele' in keys:
                alt = eval(rtept.childnodes['ele'][0].content)
                route.AddPoint(Point(time,lat,lon,alt))
            else:
                route.AddPoint(Point(time,lat,lon))


    def GetTrackNodes(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'trk' not in keys:
            print "no tracks found"
            return

        return self.parser.root.childnodes['trk']


    def GetTrackName(self,node):
        keys = node.childnodes.keys()
        if 'name' in keys:
            return node.childnodes['name'][0].content


    def GetTrackPoints(self,track,node):
        osal = Osal.GetInstance()
        reftime = osal.GetTime()
        for trkseg in node.childnodes['trkseg']:
            for trkpt in trkseg.childnodes['trkpt']:

                lat = trkpt.properties['lat']
                lon = trkpt.properties['lon']

                keys = trkpt.childnodes.keys()
                if 'time' in keys:
                    time = trkpt.childnodes['time'][0].content
                else:
                    time = osal.GetIsoTime(reftime)
                    reftime += 1

                if 'ele' in keys:
                    alt = eval(trkpt.childnodes['ele'][0].content)
                    track.AddPoint(Point(time,lat,lon,alt))
                else:
                    track.AddPoint(Point(time,lat,lon))
