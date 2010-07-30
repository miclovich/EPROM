from osal import *
from dataprovider import *
from datastorage import *
from views import *
import sys

class ConsoleApplication(Application,AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()
        self.mapcount = 0

    def Init(self):
        Application.Init(self)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)
        self.showtime = False
        self.showposition = False
        self.storage = DataStorage.GetInstance()
        if len(self.storage.maps) > 0:
            self.map = self.storage.maps[0]
        else:
            self.map = None
        self.position = None

    def SelectMap(self,index):
        print "Select map %i" % index
        self.map = self.storage.maps[index]
        print self.map.name
        print self.map.refpoints
        print self.map.size
        if self.map.iscalibrated:
            print self.map.area
        else:
            print "not calibrated"

    def ShowPosition(self,point):
        #print "Position alarm: ", point
        p = self.map.PointOnMap(point)
        if p != None:
            x,y = p
            print "%f %f: On map %s: %i,%i" % (point.latitude, point.longitude, self.map.name, int(x), int(y))
        else:
            print "%f %f: Not on map %s" % (point.latitude, point.longitude, self.map.name)


    def AlarmTriggered(self,alarm):
        if alarm == self.timealarm:
            if self.showtime:
                print "Time alarm: ", alarm.time

        if alarm == self.positionalarm:
            self.position = alarm.point
            if self.showposition:
                self.ShowPosition(alarm.point)

    def HandleInput(self,input):
        if input == 'quit\n':
            print "Exiting"
            self.running = False
        elif input == 'start gps\n':
            print "Starting GPS"
            self.provider.StartGPS()
        elif input == 'stop gps\n':
            print "Stopping GPS"
            self.provider.StopGPS()
        elif input == 'show time\n':
            print "Showing time and signal"
            self.showtime = True
        elif input == 'hide time\n':
            print "Hiding time and signal"
            self.showtime = False
        elif input == 'show pos\n':
            print "Showing position and course"
            self.showposition = True
        elif input == 'hide pos\n':
            print "Hiding position and course"
            self.showposition = False
        elif input == 'map +\n':
            self.mapcount+= 1
            if self.mapcount >= len(self.storage.maps):
                self.mapcount = 0
            self.SelectMap(self.mapcount)
        elif input == 'map -\n':
            self.mapcount -= 1
            if self.mapcount < 0:
                self.mapcount = len(self.storage.maps)-1
            self.SelectMap(self.mapcount)
        elif input[:4] == "map ":
            self.SelectMap(int(input[4:]))
        elif input == 'maps\n':
            count = 0
            for map in self.storage.maps:
                print "Map %i:" % count
                count += 1
                map.PrintInfo()
        elif input == 'find map\n':
            if self.position != None:
                maps = self.storage.FindMaps(self.position)
                for map in maps:
                    print "Found: %s" % map.name
                if len(maps) > 0:
                    self.SelectMap(self.storage.maps.index(maps[0]))
        elif input == 'tracks\n':
            if len (self.storage.tracks) < 1:
                print "No tracks"
            else:
                for name in self.storage.tracks.keys():
                    self.storage.tracks[name].PrintInfo()
        elif input[:12] == "track start ":
            self.StartTrack(input[12:-1])
        elif input[:11] == "track show ":
            self.ShowTrack(input[11:-1])
        elif input == "track stop\n":
            self.StopTrack()
        elif input[:10] == "mappoints ":
            self.ShowTrackPointsOnMap(input[10:-1])

    def StartTrack(self,name):
        self.track = self.storage.RecordTrack(name)
        print "Recording track %s" % name

    def ShowTrack(self,name,number = 10):
        t = self.storage.tracks[name]
        t.Open()
        keys = t.data.keys()
        try:
            keys.remove("name")
        except:
            pass

        keys.sort()
        for k in keys:
            print "Lat: %f\tLon:\t%f Alt: %f" % eval(t.data[k])
            number -= 1
            if number < 0:
                break

    def ShowTrackPointsOnMap(self,name,number = 10):
        if self.map != None and self.map.iscalibrated:
            t = self.storage.tracks[name]
            t.Open()
            list = t.FindPointsOnMap(self.map.area)
            l = len(list)
            if l < 1:
                print "No points found"
            else:
                print "%i points found" % l

            for p in list:
                print "Lat: %f\tLon:\t%f Alt: %f" % (p.latitude,p.longitude,p.altitude)
                number -= 1
                if number < 0:
                    break

    def StopTrack(self):
        self.storage.StopRecording()
        self.track.Close()
        print "Stopped recording track %s" % self.track.name
        self.track = None

    def Run(self):
        self.running = True
        while self.running:
            self.HandleInput(sys.stdin.readline())

    def Exit(self):
        try:
            self.provider.StopGPS()
        except:
            pass
        Application.Exit(self)
