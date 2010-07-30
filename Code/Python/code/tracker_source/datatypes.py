import datums
import os
import math
from osal import *

class AlarmResponder:
    def AlarmTriggered(self,alarm,point,course,signal,time):
        pass

class Alarm:
    def __init__(self,caller):
        self.caller = caller
        self.id = None
        self.repeat = False

    def Update(self,point,course,signal,time):
        pass

    def Condition(self):
        pass

    def Trigger(self):
        if self.caller:
             self.caller.AlarmTriggered(self)

    def SingleShot(self):
        return not self.repeat

class ProximityAlarm(Alarm):
    def __init__(self,point,tolerance,caller):
        Alarm.__init__(self,caller)
        self.point = point
        self.tolerance = tolerance
        self.bearing = 0
        self.distance = 0
        self.action = "e:\\data\\tracker\\events\\proximityalarm.py"

    def Update(self,point,course,signal,time):
        self.distance, self.bearing = point.DistanceAndBearing(self.point)

    def Condition(self):
        return self.distance < self.tolerance

class DistanceAlarm(Alarm):
    def __init__(self,point,distance,caller):
        Alarm.__init__(self,caller)
        self.point = point
        self.requested = distance
        self.current = 0

    def Update(self,point,course,signal,time):
        self.current, b = self.point.DistanceAndBearing(point)

    def Condition(self):
        return self.current > self.requested

class PositionAlarm(Alarm):
    def __init__(self,point,interval,caller):
        Alarm.__init__(self,caller)
        self.refpoint = point
        self.interval = interval
        self.repeat = True
        self.avgheading = 0
        self.avgspeed = 0
        self.avgcount = 0

    def Update(self,point,course,signal,time):
        self.point = point
        self.course = course
        self.distance = 0

        if signal.used < 3:
            return

        if self.refpoint is None:
            self.refpoint = point
            self.avgspeed = course.speed
            self.avgheading = course.heading
            self.avgcount = 0
            return

        self.avgcount += 1
        self.avgspeed = self.avgspeed/self.avgcount * (self.avgcount-1) + course.speed/self.avgcount
        self.avgheading = self.avgheading/self.avgcount * (self.avgcount-1) + course.heading/self.avgcount

        self.distance,b = self.refpoint.DistanceAndBearing(point)

    def Reset(self,point=None):
        self.refpoint = self.point
        self.avgcount = 0

    def Condition(self):
        if self.distance > self.interval:
            self.Reset()
            return True
        return False

class TimeAlarm(Alarm):
    def __init__(self,time,interval,caller):
        Alarm.__init__(self,caller)
        self.reftime = time
        self.interval = interval
        if self.interval is None:
            self.repeat = False
        else:
            self.repeat = True

    def Update(self,point,course,signal,time):
        self.time = time
        self.signal = signal

        if self.reftime is None:
            self.reftime = time

    def Reset(self):
        self.reftime += self.interval

    def Condition(self):
        if (self.time - self.reftime) > self.interval:
            self.Reset()
            return True
        return False

class Point:
    def __init__(self,time=0,lat=0,lon=0,alt=0):
        self.time = time
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

    def __repr__(self):
        return "Point(\"%s\",%f,%f,%f)" % (self.time,self.latitude, self.longitude, self.altitude)

    def DistanceAndBearing(self,point):
        return datums.CalculateDistanceAndBearing(
            (self.latitude,self.longitude),
            (point.latitude,point.longitude)
            )

    def AltLatitude(self):
        l = self.latitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

    def AltLongitude(self):
        l = self.longitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

class Course:
    def __init__(head,speed,dist):
        self.heading = head
        self.speed = speed
        self.distance = dist

    def __repr__(self):
        return "Course(%f,%f,%f)" % (self.heading, self.speed, self.distance)

class Signal:
    def __init__(self,used,found):
        self.total = 24
        self.found = found
        self.used = used

    def __repr__(self):
        return "Signal(%d,%d,%d)" % (self.used, self.found, self.total)

class Waypoint(Point):
    def __init__(self,name='',lat=0,lon=0,alt=0):
        Point.__init__(self,0,lat,lon,alt)
        self.name = name

    def __repr__(self):
        return u"Waypoint(\"%s\",%f,%f,%f)" % (self.name,self.latitude,self.longitude,self.altitude)


class Refpoint(Point):
    def __init__(self,name=None,lat=0,lon=0,x=0,y=0):
        Point.__init__(self,0,lat,lon)
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return u"Refpoint(%s,%f,%f,%f,%f)" % (self.name, self.latitude, self.longitude, self.x, self.y)


class Map:
    def __init__(self,name=None,filename=None,refpoints=[],size=(2582,1944)):
    # Size defaults to 5M, this is the max resolution of an N95 camera
    # larger values are not likely since the app would run out of RAM
        self.refpoints = refpoints
        self.size=size
        self.name=name
        self.filename=filename
        self.iscalibrated = False
        self.Calibrate()

    def PrintInfo(self):
        if self.size != None:
            print "Map %s (%i x %i)" % (self.name, self.size[0], self.size[1])
        else:
            print "Map %s (? x ?)" % self.name

        if self.iscalibrated:
            lat1,lon1,lat2,lon2 = self.area
            print "x2lon:%f y2lat:%f lon2x:%f lat2y:%f" % (self.x2lon, self.y2lat, self.lon2x, self.lat2y)
            print "Wgs84 topleft:     %f, %f" % (lat1,lon1)
            print "Wgs84 bottomright: %f, %f" % (lat2,lon2)

    def AddRefpoint(self,ref):
        self.refpoints.append(ref)
        self.Calibrate()

    def ClearRefpoints(self):
        self.refpoints = []
        self.iscalibrated = False

    def Calibrate(self):
        if self.refpoints != None and len(self.refpoints) > 1:

            #if self.size == None:
            #    print "Calibrating map %s (? x ?)" % self.name
            #else:
            #    print "Calibrating map %s (%i x %i)" % (self.name, self.size[0],self.size[1])
            #count = 0
            #for r in self.refpoints:
            #    print "refpoints[%i] lat:%f lon:%f x:%f y:%f" %(count,r.latitude,r.longitude,r.x,r.y)
            #    count+=1

            r = self.refpoints
            found = False
            for i in range(0,len(r)):
                for j in range(0,len(r)):
                    if r[i].x != r[j].x and r[i].y != r[j].y \
                        and r[i].latitude != r[j].latitude and r[i].longitude != r[j].longitude:

                            r1 = r[i]
                            r2 = r[j]
                            found = True
                            break

            if not found:
                print "Refpoints available, but either dx or dy is 0"
                return

            dx = r2.x - r1.x
            dy = r2.y - r1.y
            dlon = r2.longitude - r1.longitude
            dlat = r2.latitude - r1.latitude

            theta = (math.atan2(dy,dx) * 180 / math.pi) + 90
            if theta > 180:
                theta -= 360
            d,b = r1.DistanceAndBearing(r2)
            dtheta = b - theta
            if dtheta > 180:
                dtheta -= 360
            #print "dTheta: %7.3f  (map: %s)" % (dtheta, self.name)

            self.x = r1.x
            self.y = r1.y
            self.lat = r1.latitude
            self.lon = r1.longitude
            try:
                self.x2lon = dlon/dx
                self.y2lat = dlat/dy
                self.lon2x = dx/dlon
                self.lat2y = dy/dlat
            except:
                print "Calibration failed for map ",self.name
                print "Refpoints: ",self.refpoints
                return

            self.iscalibrated = True
            self.area = self.WgsArea()
            #self.PrintInfo()
        #else:
        #    print "Calibration failed, not enough refpoints"

    def WgsArea(self):
        if self.iscalibrated:
            lat1,lon1 = self.XY2Wgs(0,0)
            lat2,lon2 = self.XY2Wgs(self.size[0],self.size[1])
            return (lat1,lon1,lat2,lon2)

    def XY2Wgs(self,x,y):
        if self.iscalibrated:
            lon = (x - self.x)*self.x2lon + self.lon
            lat = (y - self.y)*self.y2lat + self.lat
            return lat,lon
        else:
            #print "Not calibrated"
            return None

    def Wgs2XY(self,lat,lon):
        if self.iscalibrated:
            x = (lon - self.lon)*self.lon2x + self.x
            y = (lat - self.lat)*self.lat2y + self.y
            return x,y
        else:
            #print "Not calibrated"
            return None

    def SetSize(self,size):
        self.size=size
        self.area = self.WgsArea()

    def PointOnMap(self,point):
        if self.size == None:
            return None

        if not self.iscalibrated:
            return None

        lat = point.latitude
        lon = point.longitude
        lat1,lon1,lat2,lon2 = self.area
        if lat > lat1 or lat < lat2 or lon < lon1 or lon > lon2:
            return None

        return self.Wgs2XY(point.latitude,point.longitude)


class Track:
    def __init__(self,filename,open=True):
        self.isopen = False
        self.filename = filename
        b,e = os.path.splitext(filename)
        self.name = os.path.basename(b)
        self.osal = Osal.GetInstance()
        self.isrecording = False
        if open:
            self.Open()
            self.data["name"]="%s" % self.name

    def Open(self):
        if self.isopen:
            return

        try:
            self.data = self.osal.OpenDbmFile(self.filename,"w")
        except:
            self.data = self.osal.OpenDbmFile(self.filename,"n")
        self.isopen = True

    def AddPoint(self,point):
        self.data[str(point.time)] = u"(%s,%s,%s)" % (point.latitude,point.longitude,point.altitude)

    def Dump(self):
        for key in self.data.keys():
            print key, self.data[key]

    def Close(self):
        if self.isopen:
            self.data.close()
        self.isopen = False

    def FindPointsOnMap(self,map):
        def isinrange(v,v1,v2):
            if v1>v2:
                if v < v1 and v > v2:
                    return True
            else:
                if v > v1 and v < v2:
                    return True
            return False

        if not self.isopen:
            print "track not open"
            return []

        if not map.iscalibrated:
            print "map not calibrated"
            return []

        keys =  self.data.keys()
        try:
            keys.remove("name")
        except:
            pass

        lat1,lon1,lat2,lon2 = map.WgsArea()
        list = []
        keys.sort()
        for k in keys:
            lat,lon,alt = eval(self.data[k])
            if isinrange(lat,lat1,lat2) and isinrange(lon,lon1,lon2):
                list.append(Point(k,lat,lon,alt))

        return list


    def PrintInfo(self,area=None):
        print "Track %s" % self.name



class Route:
    def __init__(self,filename,open=True):
        self.isopen = False
        self.filename = filename
        b,e = os.path.splitext(filename)
        self.name = os.path.basename(b)
        self.osal = Osal.GetInstance()
        self.isrecording = False
        if open:
            self.Open()
            self.data["name"]="%s" % self.name

    def Open(self):
        if self.isopen:
            return

        try:
            self.data = self.osal.OpenDbmFile(self.filename,"w")
        except:
            self.data = self.osal.OpenDbmFile(self.filename,"n")
        self.isopen = True

    def AddPoint(self,point):
        self.data[str(point.time)] = u"(%s,%s,%s)" % (point.latitude,point.longitude,point.altitude)

    def Dump(self):
        for key in self.data.keys():
            print key, self.data[key]

    def Close(self):
        if self.isopen:
            self.data.close()
        self.isopen = False

    def FindPointsOnMap(self,map):
        def isinrange(v,v1,v2):
            if v1>v2:
                if v < v1 and v > v2:
                    return True
            else:
                if v > v1 and v < v2:
                    return True
            return False

        if not self.isopen:
            print "track not open"
            return []

        if not map.iscalibrated:
            print "map not calibrated"
            return []

        keys =  self.data.keys()
        try:
            keys.remove("name")
        except:
            pass

        lat1,lon1,lat2,lon2 = map.WgsArea()
        list = []
        keys.sort()
        for k in keys:
            lat,lon,alt = eval(self.data[k])
            if isinrange(lat,lat1,lat2) and isinrange(lon,lon1,lon2):
                list.append(Point(k,lat,lon,alt))

        return list


    def GetPoints(self):
        if not self.isopen:
            print "route not open"
            return []

        keys =  self.data.keys()
        try:
            keys.remove("name")
        except:
            pass

        list = []
        keys.sort()
        for k in keys:
            lat,lon,alt = eval(self.data[k])
            list.append(Point(k,lat,lon,alt))

        return list


    def PrintInfo(self,area=None):
        print "Track %s" % self.name




class FileSelector:
    def __init__(self,dir=".",ext='.jpg'):
        self.dir = dir
        self.ext = ext
        self.files = {}

        def iter(fileselector,dir,files):
            for file in files:
                b,e = os.path.splitext(file)
                if e == fileselector.ext:
                    fileselector.files[u'%s' % b] = os.path.join(dir,file)

        os.path.walk(self.dir,iter,self)
