from views import *
from graphics import *
from key_codes import *
import sysinfo
import e32
import appuifw
import time
import math
import datums
import sys
from osal import *
from datastorage import *
from trace import safe_call as XWrap
from trace import dump_exceptions as XSave
from trace import store_exception as XStore

Zoom =     [ 0.5, 0.75, 1.0, 1.5, 2.0 ]
Scroll =   [ 100,   20,  10,   5,   1 ]
Datums =   [ "Wgs84", "DMS", "RD", "UTM", "DM" ]

Color = {
          "black":0x000000,
          "white":0xffffff,
          "darkblue":0x0000ff,
          "darkgreen":0x00cf00,
          "darkred":0xff0000,
          "red":0xff0000,
          "cyan":0x00ffff,
          "magenta":0xff00ff,
          "yellow":0xffff00,
          "darkyellow":0xc0c000,

          "north":0x8080ff,
          "waypoint":0x40ff40,

          "dashbg":0xe0e0e0,
          "dashfg":0x000000,
          "gaugebg":0xc0c0c0,
          "gaugefg":0xffffff,

          "batsignal":0xf04040,
          "gsmsignal":0x404040,
          "satsignal":0x4040f0,
          "nosignal":0xe0e0e0,

          "bar_c1": 0x00cf00,
          "bar_c2": 0xff0000,
          "bar_c3": 0x000000,
          "bar_bg": 0x0000ff,
    }

def SetSystemApp(value):
    try:
        import envy
        envy.set_app_system(value)
    except:
        pass

def Vibrate(time,volume):
    try:
        import misty
        misty.vibrate(time,volume)
    except:
        pass

class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = ('normal',14)
        self.fgcolor = 0
        self.bgcolor = 0xf0f0f0
        self.Resize(size)

    def Resize(self,size=None):
        print "Widget.Resize(",size,")"
        self.size = size
        if self.size == None:
            return
        self.Draw()

    def Draw(self):
        if self.size == None:
            return

        self.image = Image.new(self.size)
        self.image.clear(self.bgcolor)
        self.mask = Image.new(self.size,'1')
        self.mask.clear(1)

    def GetTextSize(self,text):
        (bbox,advance,ichars) = self.image.measure_text(text,font=self.font)
        w,h = (bbox[2]-bbox[0],bbox[3]-bbox[1])
        return (w,h)

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def DrawText(self,coords,text):
        if self.size == None:
            return

        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        y += h
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        self.image.text((x,y),u'%s' % text,font=self.font,fill=self.fgcolor)
        return (w,h)

    def DrawDot(self,point,color=0,width=1):
        self.image.point(point,outline=color,width=width)

    def DrawLine(self,point1,point2,color,width=1):
        self.image.line((point1,point2),color,width=width)

    def DrawEllipse(self,rect,color,width=1,fill=None):
        self.image.ellipse(rect,outline=color,width=width,fill=fill)



class TextWidget(Widget):
    def __init__(self,text='',hpad=5,vpad=3,fgcolor=0,bgcolor=0xf0f0f0):
        Widget.__init__(self)
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.text = text
        self.hpad = hpad
        self.vpad = vpad
        self.Resize((1,1))
        self.UpdateText(text,hpad,vpad)

    def UpdateText(self,text,hpad=5,vpad=3):
        self.text = text
        self.hpad = hpad
        self.vpad = vpad
        w,h = self.GetTextSize(u'%s' % text)
        w += hpad*2
        h += vpad*2
        self.Resize((w,h))

    def Draw(self):
        Widget.Draw(self)
        self.DrawText( (self.hpad,self.vpad), u'%s' % self.text)



class _BarWidget(Widget):
    def __init__(self,size=None,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        Widget.__init__(self)
        self.bgcolor = Color["bar_bg"]
        self.v1=40
        self.v2=80
        self.SetParams(c1,c2,range,bars)
        self.Resize(size)

    def SetParams(self,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        self.c1=c1
        self.c2=c2
        self.bars = bars
        self.range = range
        self.Resize(self.size)

    def UpdateValues(self,v1,v2):
        self.v1 = v1
        self.v2 = v2
        self.Draw()

    def Resize(self,size):
        print "BarWidget.Resize(",size,")"
        if size == None:
            Widget.Resize(self,size)
            return

        w,h = size
        self.x = w / 2.0
        self.y = 2
        self.dy = (h-2*self.y)/float(self.bars)
        #self.y -= self.dy/2
        if self.dy > 4:
            self.width = (self.dy - 2)
        else:
            self.width = 2

        self.y += int(self.width/2.0+0.5)
        Widget.Resize(self,size)

    def Draw(self):
        if self.size == None:
            return

        Widget.Draw(self)

        if self.v1 == None:
            v1=0
        else:
            v1 = int(0.5 + float(self.v1) * float(self.bars) / float(self.range))
        if self.v2 == None:
            v2 = v1
        else:
            v2 = int(0.5 + float(self.v2) * float(self.bars) / float(self.range))
        if v2 < v1:
            v2=v1

        if v1 > self.bars:
            v1 = self.bars
        if v2 > self.bars:
            v2 = self.bars
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0

        #print 0,v2,v2,self.bars,self.x,self.y,self.dy
        for i in range (0,v1):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c1,self.width)
        for i in range (v1,v2):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c2,self.width)
        for i in range (v2,self.bars):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),Color["black"],self.width)


class BarWidget(Widget):

    def __init__(self,size=None,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        Widget.__init__(self)
        self.bgcolor = Color["bar_bg"]
        self.v1=40
        self.v2=80
        self.SetParams(c1,c2,range,bars)
        self.Resize(size)

    def SetParams(self,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        self.c1=c1
        self.c2=c2
        self.bars = bars
        self.range = range
        self.Resize(self.size)

    def UpdateValues(self,v1,v2):
        self.v1 = v1
        self.v2 = v2
        self.Draw()

    def Resize(self,size):
        print "BarWidget.Resize(",size,")"
        #if size == None:
        #    Widget.Resize(self,size)
        #    return
        Widget.Resize(self,size)

    def _Resize(self):
        self.x = w / 2.0
        self.y = 2
        self.dy = (h-2*self.y)/float(self.bars)
        #self.y -= self.dy/2
        if self.dy > 4:
            self.width = (self.dy - 2)
        else:
            self.width = 2

        self.y += int(self.width/2.0+0.5)
        Widget.Resize(self,size)

    def CalcValues(self):
        if self.v1 == None:
            v1=0
        else:
            v1 = int(0.5 + float(self.v1) * float(self.bars) / float(self.range))
        if self.v2 == None:
            v2 = v1
        else:
            v2 = int(0.5 + float(self.v2) * float(self.bars) / float(self.range))
        if v2 < v1:
            v2=v1

        if v1 > self.bars:
            v1 = self.bars
        if v2 > self.bars:
            v2 = self.bars
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0

        return v1,v2

    def Draw(self):
        if self.size == None:
            return

        Widget.Draw(self)

        w,h = self.size
        if w > h:
            self.bars = (w-3)/2
            x1,y1 = 2,2
            x2,y2 = 2,h-4
            dx = 2
            dy = 0
        else:
            self.bars = (h-3)/2
            x1,y1 = 2,h-2
            x2,y2 = w-4,h-2
            dx = 0
            dy = 2

        v1,v2 = self.CalcValues()

        for i in range (0,v1):
            self.DrawLine((x1,y1),(x2,y2),self.c1)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v1,v2):
            self.DrawLine((x1,y1),(x2,y2),self.c2)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v2,self.bars):
            self.DrawLine((x1,y1),(x2,y2),Color["black"])
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy


    def _Draw(self):
        if self.v1 == None:
            v1=0
        else:
            v1 = int(0.5 + float(self.v1) * float(self.bars) / float(self.range))
        if self.v2 == None:
            v2 = v1
        else:
            v2 = int(0.5 + float(self.v2) * float(self.bars) / float(self.range))
        if v2 < v1:
            v2=v1

        if v1 > self.bars:
            v1 = self.bars
        if v2 > self.bars:
            v2 = self.bars
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0

        #print 0,v2,v2,self.bars,self.x,self.y,self.dy
        for i in range (0,v1):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c1,self.width)
        for i in range (v1,v2):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c2,self.width)
        for i in range (v2,self.bars):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),Color["black"],self.width)


class PositionWidget(Widget):
    def __init__(self,size = None):
        s = DataStorage.GetInstance()
        self.point = s.GetValue("app_lastknownposition")
        self.funcs = {
                 "Wgs84" : self.GetWgs84Texts,
                 "RD"    : self.GetRDTexts,
                 "UTM"   : self.GetUTMTexts,
                 "DMS"   : self.GetDMSTexts,
                 "DM"    : self.GetDMTexts,
                 }
        Widget.__init__(self)
        self.font = ('normal',11)
        self.fontsize = 11
        self.fgcolor = 0x0
        self.bgcolor = 0xc0c0ff
        self.Resize(size)

    def UpdateDatum(self):
        self.Draw()

    def UpdatePosition(self,point):
        self.point = point
        self.Draw()

    def GetWgs84Texts(self,lat,lon):
        return u"Wgs84", u"N%8.5f" % lat, u"E%8.5f" % lon

    def GetDMSTexts(self,lat,lon):
        (nd,nm,ns),(ed,em,es) = datums.GetDMSFromWgs84(lat,lon)
        return u"Wgs84", u"N%2.0f %2.0f\'%5.2f\"" % (nd,nm,ns), u"E%2.0f %2.0f\'%5.2f\"" % (ed,em,es)

    def GetDMTexts(self,lat,lon):
        (nd,nm),(ed,em) = datums.GetDMFromWgs84(lat,lon)
        return u"Wgs84", u"N%2.0f %7.4f\'" % (nd,nm), u"E%2.0f %7.4f\'" % (ed,em)

    def GetUTMTexts(self,lat,lon):
        ellips = DataStorage.GetInstance().GetValue("app_ellips")
        z,x,y = datums.latlon_to_utm(ellips,lat,lon)
        return u"UTM", z, str(int(x))+"E", str(int(y))+"N",

    def GetRDTexts(self,lat,lon):
        x,y = datums.GetRdFromWgs84(lat,lon)
        return u"RD", u"%6.0f" % x, u"%6.0f" % y

    def GetPositionTexts(self):
        datum = DataStorage.GetInstance().GetValue("app_datum")
        if datum in self.funcs.keys():
            return self.funcs[datum](self.point.latitude,self.point.longitude)

    def Draw(self):
        Widget.Draw(self)
        s=self.image.size
        self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)
        if self.point:
            texts = self.GetPositionTexts()
            x,y = 5,5
            text = u""
            for t in texts:
                text = text + t + u" "
            #    w,h = self.DrawText((x,y),t)
            #    x = x+w+7

            self.DrawText( (5,1), text)
        else:
            self.DrawText( (5,1), u"Position unknown")

GPS = 0
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

class MapWidget(Widget):
    def __init__(self,size = None):
        Widget.__init__(self,None)
        self.storage = DataStorage.GetInstance()
        self.position = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        self.lastpos = None
        self.cursor = None
        self.amount = 4
        self.position = self.storage.GetValue("app_lastknownposition")
        self.heading = 0
        self.bearing = 0
        self.distance = 0
        self.track = None
        self.zoom = Zoom.index(1.0)
        self.UpdatePosition(self.position)
        self.Resize(size)

    def GetCursor(self):
        if self.cursor != None:
            return self.cursor
        if self.lastpos != None:
            return self.lastpos
        x,y = self.map.size
        x=x/2
        y=y/2
        return (x,y)

    def AddRefpoint(self,name,lat,lon):
        x,y = self.GetCursor()
        r = Refpoint(name,lat,lon,x,y)
        self.map.AddRefpoint(r)
        if self.map.iscalibrated:
            self.Draw()

    def ClearRefpoints(self):
        if self.map != None:
            self.map.ClearRefpoints()
            self.Draw()

    def SaveCalibrationData(self):
        file = MapFile(self.map.filename,"w")
        file.writeResolution(self.map.size)
        for r in self.map.refpoints:
            file.writeRefpoint(r)
        file.close()

    def GetPosition(self):
        if self.cursor:
            pos = self.map.XY2Wgs(self.cursor[0],self.cursor[1])
            if pos != None:
                lat,lon = pos
                return Point(0,lat,lon)
        return self.position

    def FollowGPS(self):
        self.cursor = None
        self.Draw()

    def Move(self,direction):
        if self.map == None:
            self.cursor = None
            print "Move: No map"
            return

        if self.cursor == None:
            if self.lastpos == None:
                x,y = self.map.size
                x=x/2
                y=y/2
            else:
                x,y = self.lastpos
        else:
            x,y = self.cursor


        amount = Scroll[self.zoom]
        if direction == UP:
            y -= amount
            if y<0:
                y=0
        elif direction == DOWN:
            y += amount
            if y>self.map.size[1]:
                y = self.map.size[1]
        elif direction == LEFT:
            x -= amount
            if x<0:
                x=0
        elif direction == RIGHT:
            x += amount
            if x>self.map.size[0]:
                x = self.map.size[0]
        else:
            raise "Unknown direction"

        self.cursor = (x,y)
        self.Draw()

    def ZoomOut(self):
        if self.zoom > 0:
            self.zoom -=1
            self.Draw()

    def ZoomIn(self):
        if self.zoom < (len(Zoom)-1):
            self.zoom += 1
            self.Draw()

    def SetMap(self,map):
        self.map = map
        self.mapimage = None
        self.LoadMap()

    def SetRecordingTrack(self,track):
        self.track = track

    def DrawTrackPoint(self,point,color):
        cur = self.map.PointOnMap(point)
        if cur != None:
            self.mapimage.point((cur[0],cur[1]),color,width=5)

    def DrawTrack(self,track,color=Color["darkblue"]):
        points = track.FindPointsOnMap(self.map)
        if points != None and len(points) > 0:
            for p in points:
                self.DrawTrackPoint(p, color)
        else:
            print "No points of track on current map"

    def DrawOpenTracks(self):
        for track in self.storage.opentracks:
            self.DrawTrack(self.storage.tracks[track],Color["darkblue"])
        self.Draw()

    def DrawRouteSection(self,p0,p1,color):
        c0 = self.map.PointOnMap(p0)
        c1 = self.map.PointOnMap(p1)
        if c0 != None and c1 != None:
            self.mapimage.line((c0,c1),color,width=5)

    def DrawRoute(self,route,color=Color["darkyellow"]):
        points = route.GetPoints()
        p0 = None
        if points != None and len(points) > 1:
            for p in points:
                if p0 != None:
                    self.DrawRouteSection(p0,p,color)
                p0 = p

        else:
            print "No route sections found"

    def DrawOpenRoutes(self):
        for route in self.storage.openroutes:
            self.DrawRoute(self.storage.routes[route],Color["darkyellow"])
        self.Draw()

    def LoadMap(self):
        if self.map == None:
            return

        self.mapimage = Image.open(u"%s" % self.map.filename)
        self.zoom = Zoom.index(1.0)
        self.map.SetSize(self.mapimage.size)
        self.UpdatePosition(self.position)
        self.lastarea = None
        self.DrawOpenTracks()
        if self.track != None:
            self.DrawTrack(self.track,Color["darkred"])

    def ClearMap(self):
        self.mapimage = None

    def UpdatePosition(self,point):
        self.position = point
        if self.map != None:
            self.onmap = self.map.PointOnMap(point)
        else:
            self.onmap = None

        if self.onmap !=None:
            self.lastpos = self.onmap

        self.Draw()

    def UpdateTrack(self,track=None,point=None):
        if self.map == None:
            return

        if track != None:
            self.DrawTrack(track)
        if point != None:
            self.DrawTrackPoint(point,Color["darkred"])
        self.Draw()

    def UpdateRoute(self,route=None):
        if self.map == None:
            return

        if route != None:
            self.DrawRoute(route)

        self.Draw()

    def UpdateWaypoints(self):
        self.Draw()

    def UpdateValues(self,heading,bearing,distance):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        self.Draw()

    def ScreenArea(self):
        w,h = self.size
        return (2,2,w-2,h-2)

    def MapArea(self,size,zoom=1.0,pos=None):
        w,h = size
        w = w/zoom
        h = h/zoom

        if pos == None:
            if self.lastpos == None:
                mw,mh = self.map.size
                x,y = (mw/2, mh/2)
            else:
                x,y = self.lastpos
        else:
            x,y = pos

        self.lastarea = (x-w/2,y-h/2,x+w/2,y+h/2)
        return self.lastarea

    def SaneAreas(self,target,source,zoom=1.0):
        x1,y1,x2,y2 = target
        x3,y3,x4,y4 = source

        mw,mh = self.map.size
        if x3 < 0:
            x1 -= (x3*zoom)
            x3 = 0
        if y3 < 0:
            y1 -= (y3*zoom)
            y3 = 0
        if x4 > mw:
            x2 -= ((x4 - mw)*zoom)
            x4 = mw
        if y4 > mh:
            y2 -= ((y4 - mh)*zoom)
            y4 = mh

        target = (int(x1),int(y1),int(x2),int(y2))
        source = (int(x3),int(y3),int(x4),int(y4))
        return target,source


    def CalculatePoint(self,heading,(x,y),length):
        _heading = heading * 3.14159265 / 180
        point =  ( x + length * math.sin(_heading),
                   y - length * math.cos(_heading) )
        return point

    def DrawArrow(self,image,coords,color=Color["black"]):
        r=10
        point1 = self.CalculatePoint(self.heading,   coords,r*4)
        point2 = self.CalculatePoint(self.heading+30,coords,r*1.5)
        point3 = self.CalculatePoint(self.heading,   coords,r*2)
        point4 = self.CalculatePoint(self.heading-30,coords,r*1.5)
        image.polygon((point1,point2,point3,point4),Color["white"],fill=color)


    def DrawCursor(self,image,coords,color=Color["black"]):
        x,y = coords
        w,h = image.size
        if x <0 or x>=w or y <0 or y>=h:
            return

        r = 10
        image.point((x,y),Color["white"],width=5)
        image.point((x,y),color,width=3)
        image.ellipse(((x-r,y-r),(x+r,y+r)),Color["white"],width=5)
        image.ellipse(((x-r,y-r),(x+r,y+r)),color,width=3)

    def DrawWaypoints(self,zoom=1.0):
        def isinrange(v,v1,v2):
            if v1>v2:
                if v < v1 and v > v2:
                    return True
            else:
                if v > v1 and v < v2:
                    return True
            return False

        waypoints = self.storage.GetWaypoints()
        for w in waypoints.values():
            onmap = self.map.PointOnMap(w)
            if onmap != None and self.lastarea != None:
                x,y = onmap
                x1,y1,x2,y2 = self.lastarea
                if isinrange(x,x1,x2) and isinrange(y,y1,y2):
                    self.DrawCursor(self.image,((x-x1)*zoom,(y-y1)*zoom),Color["darkgreen"])


    def Draw(self):
        Widget.Draw(self)
        if self.size != None:

            s=self.image.size
            w,h = s
            self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)

            if self.map != None:
                zoom = Zoom[self.zoom]
                screenarea = self.ScreenArea()
                size = (screenarea[2]-screenarea[0],screenarea[3]-screenarea[1])
                if self.cursor == None:
                    maparea = self.MapArea(size,zoom,self.onmap)
                else:
                    maparea = self.MapArea(size,zoom,self.cursor)

                t,s = self.SaneAreas(screenarea,maparea,zoom)

                if self.mapimage != None:
                    width,height = self.size
                    self.image.blit(
                        self.mapimage,
                        target=t,
                        source=s,
                        scale=1)

                self.DrawWaypoints(zoom)

            if self.onmap == None or self.cursor != None:
                c = Color["black"]
            else:
                c = Color["darkblue"]

            self.DrawCursor(self.image,(w/2,h/2),c)
            self.DrawArrow(self.image,(w/2,h/2),c)

class Gauge:
    def __init__(self,radius=None):
        self.Resize(radius)
        self.value = None

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return
        self.Draw()

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def Draw(self):
        if self.radius == None:
            return

        self.image = Image.new((self.radius*2,self.radius*2))
        self.image.ellipse(((0,0),(self.radius*2,self.radius*2)),0,width=1,fill=0xf0f0f0)
        self.mask = Image.new((self.radius*2,self.radius*2),'1')
        self.mask.clear(0)
        self.mask.ellipse(((0,0),(self.radius*2,self.radius*2)),width=1,outline=0xffffff,fill=0xffffff)


    def CalculatePoint(self,heading,radius,length):
        if self.radius == None:
            return

        _heading = heading * 3.14159265 / 180
        point =  ( radius + length * math.sin(_heading),
                   radius - length * math.cos(_heading) )
        return point


    def DrawText(self,coords,text,size=1.0):
        if self.radius == None:
            return

        f = ('normal',int(self.radius/5*size))
        box = self.image.measure_text(text,font=f)
        x,y = coords
        ((tlx,tly,brx,bry),newx,newy) = box
        x = x - (brx - tlx)/2
        y = y - (bry - tly)/2
        self.image.text((x,y),text,font=f)


    def DrawInnerCircle(self,radius,color=0,circlewidth=1):
        point1 = (self.radius - radius,self.radius - radius)
        point2 = (self.radius + radius,self.radius + radius)
        self.image.ellipse((point1,point2),color,width=circlewidth)


    def DrawInnerCross(self,color=0,crosswidth=1):
        point1 = (self.radius,0)
        point2 = (self.radius,self.radius*2)
        self.image.line((point1,point2),color,width=crosswidth)
        point1 = (0,self.radius)
        point2 = (self.radius*2,self.radius)
        self.image.line((point1,point2),color,width=crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                point = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.image.point((point),0,width=1)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                point1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                point2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.image.line((point1,point2),0,width=1)


    def DrawDotHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point = self.CalculatePoint(heading,self.radius,length)
        self.image.point((point),color,width=handwidth)


    def DrawLineHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point1 = (self.radius,self.radius)
        point2 = self.CalculatePoint(heading,self.radius,length)
        self.image.line((point1,point2),color,width=handwidth)


    def DrawTriangleHand(self,heading,length,color,handwitdh=5):
        if self.radius == None:
            return

        point1 = self.CalculatePoint(heading,   self.radius,length)
        point2 = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        point3 = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        self.image.polygon((point1,point2,point3),color,fill=color)



class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',format=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.format = format
        self.longdivider = divider[0]
        self.shortdivider = divider[1]
        self.factor = divider[1]/divider[0]
        self.scale = scale
        self.value = None

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name)
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.format % self.value, size=1.5)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, 0, 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, 0, 4)



class DistanceForm(object):
#        "distance_units":"\"km\"",
#        "distance_type":\"trip\",
#        "distance_tolerance":"25",
#        "distance_trip":"0",
#        "distance_total":"0",

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Total', u'Trip', u'Waypoint']
        self._ShortTypes = [u'total', u'trip', u'wpt']
        self._Units = [u'Kilometers', u'Miles']
        self._ShortUnits = [u'km',u'miles']
        self._Bool = [u'No',u'Yes']

        self.gauge.GetOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         #( u'Tolerance', 'combo', ( tolerance, itolerance ) ),
                         #( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
                         #( u'Min','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Distance Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.units = self.GetUnits()
            #self.gauge.tolerance = self.GetTolerance()
            #self.gauge.interval = self.GetInterval()
            #print "Saving: ", self.gauge.type, self.gauge.units, self.gauge.tolerance, self.gauge.interval
            self.gauge.SaveOptions()
            self.gauge.name = "%s (%s)" % (self.gauge.type,self.gauge.units)
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    #def GetTolerance( self ):
    #    field = self.GetField(u'Tolerance')
    #    if field != None:
    #        return self._ToleranceValues[field[2][1]]




class DistanceGauge(TwoHandGauge):

    def __init__(self,radius=None):
        self.GetOptions()
        TwoHandGauge.__init__(self,radius,"%s-%s" % (self.type,self.units),u'%6.2f')
        self.value = 0
        self.total = 0
        self.trip = 0
        self.distance = 0
        self.GetOptions()

    def Draw(self):
        if self.type == "total":
            distance = self.total
        if self.type == "trip":
            distance = self.trip
        if self.type == "wpt":
            distance = self.distance

        if self.units == "km":
            self.value = distance / 1000
        else: # self.units == "miles"
            self.value = distance / 1000 * 0.621371192

    	TwoHandGauge.Draw(self)

    def UpdateValues(self,total,trip,distance):
        self.total = total
        self.trip = trip
        self.distance = distance
        self.Draw()

    def GetOptions(self):
        s = DataStorage.GetInstance()
        self.units = s.GetValue("distance_units")
        self.type = s.GetValue("distance_type")
        self.tolerance = s.GetValue("distance_tolerance")

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("distance_units",self.units)
        s.SetValue("distance_type",self.type)
        s.SetValue("distance_tolerance",self.tolerance)

    def SelectOptions(self):
        form = DistanceForm(self)
        if form.Run():
            self.Draw()



class AltitudeForm(object):

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Altitude', u'Ascent', u'Descent', u'Average']
        self._ShortTypes = [u'alt', u'asc', u'desc', u'avg-alt']
        self._Units = [u'Meters', u'Feet']
        self._ShortUnits = [u'm',u'ft']
        self._ToleranceMeters = [u'5 meters', u'10 meters', u'25 meters', u'50 meters', u'100 meters', u'250 meters']
        self._ToleranceFeet = [u'15 feet', u'30 feet', u'75 feet', u'150 feet', u'300 feet', u'750 feet']
        self._Interval = [ u'5 seconds', u'15 seconds', u'30 seconds', u'1 minute', u'2 minutes', u'5 minutes',
                           u'15 minutes', u'30 minutes', u'1 hour', u'2 hours', u'5 hours' ]
        self._ToleranceValues = [ 5, 10, 25, 50, 100, 250 ]
        self._IntervalValues = [ 5, 15, 30, 60, 120, 300, 900, 1800, 3600, 7200, 18000 ]
        self._Bool = [u'No',u'Yes']

        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        if self.gauge.interval in self._IntervalValues:
            iinterval = self._IntervalValues.index(self.gauge.interval)
        else:
            iinterval = 0

        if self.gauge.tolerance in self._ToleranceValues:
            itolerance = self._ToleranceValues.index(self.gauge.tolerance)
        else:
            itolerance = 0

        if iunits == 0:
            tolerance = self._ToleranceMeters
        else:
            tolerance = self._ToleranceFeet

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         ( u'Tolerance', 'combo', ( tolerance, itolerance ) ),
                         ( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
                         #( u'Min','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Altitude Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.SetOptions(
                self.GetType(),
                self.GetUnits(),
                self.GetInterval(),
                self.GetTolerance(),
            )
            self.gauge.SaveOptions()

            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    def GetTolerance( self ):
        field = self.GetField(u'Tolerance')
        if field != None:
            return self._ToleranceValues[field[2][1]]

    def GetInterval( self ):
        field = self.GetField(u'Interval')
        if field != None:
            return self._IntervalValues[field[2][1]]

    def GetMax( self ):
        field = self.GetField(u'Show max')
        if field != None:
            return (field[2][1]==1)
        else:
            return False

    def GetMin( self ):
        field = self.GetField(u'Show min')
        if field != None:
            return (field[2][1]==1)
        else:
            return False



class AltitudeGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'altitude',u'%8.0f',(100,1000))
        self.value = 0
        self.altitude = 0
        self.ascent = 0
        self.descent = 0
        self.base = 0
        self.tolerance = 0
        self.interval = 0
        self.avglist = []
        self.avgbase = 0
        self.avgcount = 0
        self.step = None
        self.LoadOptions()

    def Draw(self):
    	TwoHandGauge.Draw(self)

    def SetOptions(self,type="alt",units="m",interval=300,tolerance=100,max=False,min=False):
        self.type = type
        self.units = units
        if self.interval != interval:
            self.interval = interval
            if interval >= 300:
                self.step = int(interval / 100)
            else:
                self.step = None
            self.avglist=[]
            self.avgcount = 0

        self.tolerance = tolerance
        self.showmax = max
        self.showmin = min
        self.name = "%s (%s)" % (self.type,self.units)

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("alt_type"),
            s.GetValue("alt_units"),
            s.GetValue("alt_interval"),
            s.GetValue("alt_tolerance"),
            s.GetValue("alt_showmax"),
            s.GetValue("alt_showmin")
        )

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("alt_type",self.type)
        s.SetValue("alt_interval",self.interval)
        s.SetValue("alt_tolerance",self.tolerance)
        s.SetValue("alt_units",self.units)
        s.SetValue("alt_showmax",self.showmax)
        s.SetValue("alt_showmin",self.showmin)

    def SelectOptions(self):
        form = AltitudeForm(self)
        if form.Run():
            self.Draw()

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        if self.type == "alt":
            value = self.altitude
        if self.type == "asc":
            value = self.ascent
        if self.type == "desc":
            value = self.descent
        if self.type == "avg-alt":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if self.units == "m":
            self.value = value
        else: # self.units == "ft"
            self.value = value * 3.2808398950131235

        TwoHandGauge.Draw(self)

    def UpdateValue(self,value):
        self.altitude = value

        delta = value -self.base
        if delta > self.tolerance:
            self.ascent += delta
            self.base = value
        if (-1 * delta) > self.tolerance:
            self.descent -= delta
            self.base = value

        if self.step == None:
            self.avglist.append(value)
            if len(self.avglist)>self.interval:
                del(self.avglist[0])
        else:
            self.avgbase += (value/self.step)
            self.avgcount += 1
            if self.avgcount == self.step:
                self.avglist.append(self.avgcount)
                if len(self.avglist) > 100:
                    del(self.avglist[0])
                self.avgbase = 0
                self.avgcount = 0

        self.Draw()



class SpeedForm(object):
#        units = [ u"km/h", u"mph" ]
#        types = [ u"speed", u"speed-avg" ]

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Actual', u'Average']
        self._ShortTypes = [u'speed', u'avg-speed']
        self._Units = [u'Km/h', u'Mph']
        self._ShortUnits = [u'km/h',u'mph']
        self._Interval = [ u'5 seconds', u'15 seconds', u'30 seconds', u'1 minute', u'2 minutes', u'5 minutes',
                           u'15 minutes', u'30 minutes', u'1 hour', u'2 hours', u'5 hours' ]
        self._IntervalValues = [ 5, 15, 30, 60, 120, 300, 900, 1800, 3600, 7200, 18000 ]
        self._Bool = [u'No',u'Yes']

        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        if self.gauge.interval in self._IntervalValues:
            iinterval = self._IntervalValues.index(self.gauge.interval)
        else:
            iinterval = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         ( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Speed Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.units = self.GetUnits()
            self.gauge.interval = self.GetInterval()
            #print "Saving: ", self.gauge.type, self.gauge.units, self.gauge.tolerance, self.gauge.interval
            self.gauge.SaveOptions()
            self.gauge.name = "%s (%s)" % (self.gauge.type,self.gauge.units)
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    def GetInterval( self ):
        field = self.GetField(u'Interval')
        if field != None:
            return self._IntervalValues[field[2][1]]

    def GetMax( self ):
        field = self.GetField(u'Show max')
        if field != None:
            return (field[2][1]==1)
        else:
            return False



class SpeedGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2f')
        self.value = 0
        self.speed = 0
        #self.GetOptions()
        self.interval = 0
        self.avglist = []
        self.avgbase = 0
        self.avgcount = 0
        self.step = None
        self.LoadOptions()

    def SetOptions(self,type="speed",units="m",interval=300,max=False):
        self.type = type
        self.units = units
        if self.interval != interval:
            self.interval = interval
            if interval >= 300:
                self.step = int(interval / 100)
            else:
                self.step = None
            self.avglist=[]
            self.avgcount = 0

        self.showmax = max
        self.showmin = min
        self.name = "%s (%s)" % (self.type,self.units)

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("speed_type"),
            s.GetValue("speed_units"),
            s.GetValue("speed_interval"),
            s.GetValue("speed_showmax")
        )


    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("speed_units",self.units)
        s.SetValue("speed_type",self.type)
        s.SetValue("speed_interval",self.interval)
        s.SetValue("speed_showmax",self.showmax)

    def SelectOptions(self):
        form = SpeedForm(self)
        if form.Run():
            self.Draw()

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        if self.type == "speed":
            value = self.speed
        if self.type == "avg-speed":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if self.units == u"km/h":
            self.value = value
        else: # self.units == "mph"
            self.value = value * 0.621371192237

        TwoHandGauge.Draw(self)

    def UpdateValue(self,value):
        if str(value) == "NaN":
            return

        if value < 0:
            value = 0
        if value > 9999:
            value = 9999

        self.speed = value

        if self.step == None:
            self.avglist.append(value)
            if len(self.avglist)>self.interval:
                del(self.avglist[0])
        else:
            self.avgbase += (value/self.step)
            self.avgcount += 1
            if self.avgcount == self.step:
                self.avglist.append(self.avgcount)
                if len(self.avglist) > 100:
                    del(self.avglist[0])
                self.avgbase = 0
                self.avgcount = 0

        self.Draw()


class SateliteGauge(Gauge):

    def __init__(self,radius=None):
        self.satlist = []
        Gauge.__init__(self,radius)

    def SelectOptions(self):
        appuifw.note(u"No options available.", "info")


    def UpdateSatInfo(self,satlist):
        self.satlist = satlist
        self.Draw()

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawText(((self.radius,0.6*self.radius)),u'satelites')
        self.DrawInnerCircle(self.radius*0.4)
        self.DrawInnerCross()

        if len(self.satlist) > 0:
            for info in self.satlist:
                angle = info['azimuth']
                pos = self.radius * ((90.0 - info['elevation'])/100)
                color = 0x40c040 * info['inuse']
                self.DrawDotHand(angle,pos,color,handwidth=self.radius/10)


class ClockGauge(Gauge):

    def __init__(self,radius=None):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.tag = "clock"
        Gauge.__init__(self,radius)

    def UpdateValue(self,value):
        y,m,d, self.hours, self.minutes, self.seconds, a,b,c = time.localtime(value)
        self.Draw()
        #print "Time: ",self.hours,self.minutes,self.seconds

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.tag)
        if ((self.radius != None) and
            (self.hours != None) and
            (self.minutes != None)):

                hourshand =    self.hours   * 360/12  + self.minutes * 360/12/60
                if self.seconds != None:
                    minuteshand =  self.minutes * 360/60  + self.seconds * 360/60/60
                    secondshand =  self.seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds),size=1.5)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)



class TimeForm(object):
#        "time_type":\"trip\",

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Clock', u'Trip', u'Remaining',u'ETA']
        self._ShortTypes = [u'clock', u'trip',u'remaining',u'eta']

        self.gauge.LoadOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Time Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.SaveOptions()
            self.gauge.tag = "%s" % self.gauge.type
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )


class TimeGauge(Gauge):

    def __init__(self,radius=None):
        self.time = 0
        self.trip = 0
        self.remaining = 0
        self.eta = 0
        self.type = "clock"
        Gauge.__init__(self,radius)
        self.LoadOptions()

    def SetOptions(self,type="clock"):
        self.type = type
        self.tag = "%s" % self.type

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("time_type")
        )


    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("time_type",self.type)

    def SelectOptions(self):
        form = TimeForm(self)
        if form.Run():
            self.Draw()

    def GetHMS(self,value):
        h = int(value/3600)
        m = int((value - h * 3600) / 60)
        s = int(value - h * 3600 - m * 60)
        return h,m,s

    def UpdateValues(self,time,trip,remaining,eta):
        self.time = time
        self.trip = trip
        self.remaining = remaining
        self.eta = eta
        self.Draw()

    def Draw(self):
        if self.type == "clock":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.time)
        if self.type == "eta":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.eta)
        if self.type == "trip":
            hours,minutes,seconds = self.GetHMS(self.trip)
        if self.type == "remaining":
            hours,minutes,seconds = self.GetHMS(self.remaining)

        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.tag)
        if ((self.radius != None) and
            (hours != None) and
            (minutes != None)):

                hourshand =    hours   * 360/12  + minutes * 360/12/60
                if seconds != None:
                    minuteshand =  minutes * 360/60  + seconds * 360/60/60
                    secondshand =  seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (hours,minutes,seconds),size=1.3)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (hours,minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)



class WaypointForm(object):

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        storage = DataStorage.GetInstance()
        self._Waypoints = storage.GetWaypoints().keys()
        self._Waypoints.sort()

        self._Types = [u'Heading', u'Waypoint']
        self._ShortTypes = [u'heading', u'waypoint']
        self._DistanceUnits = [u'Meters', u'Feet']
        self._ShortDistanceUnits = [u'm',u'ft']
        #self._BearingUnits = [u'Degrees', u'Radians']
        #self._ShortBearingUnits = [u'deg',u'rad']
        self._ToleranceMeters = [u'5 meters', u'10 meters', u'25 meters', u'50 meters', u'100 meters', u'250 meters' ]
        self._ToleranceFeet = [u'15 feet', u'30 feet', u'75 feet', u'150 feet', u'300 feet', u'750 feet' ]
        self._ToleranceValues = [ 5,10,25,50,100,250 ]
        #self._Bool = [u'No',u'Yes']

        self.gauge.GetOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.waypoint in self._Waypoints:
            iwaypoints = self._Waypoints.index(self.gauge.waypoint)
        else:
            iwaypoints = 0

        if self.gauge.distunits in self._ShortDistanceUnits:
            idunits = self._ShortDistanceUnits.index(self.gauge.distunits)
        else:
            idunits = 0

        if self.gauge.tolerance in self._ToleranceValues:
            itolerance = self._ToleranceValues.index(self.gauge.tolerance)
        else:
            itolerance = 0

        if idunits == 0:
            tolerance = self._ToleranceMeters
        else:
            tolerance = self._ToleranceFeet

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Monitor waypoint', 'combo', ( self._Waypoints, iwaypoints ) ),
                         ( u'Distance Units', 'combo', ( self._DistanceUnits, idunits ) ),
                         ( u'Distance Tolerance', 'combo', ( tolerance, itolerance ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
                         #( u'Min','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        app = S60Application.GetInstance()
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Waypoint Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.distunits = self.GetDistanceUnits()

            tolerance = self.GetDistanceTolerance()
            waypoint = self.GetWaypoint()
            app._MonitorWaypoint(waypoint,tolerance)

            self.gauge.tag = u"%s" % waypoint.name
            self.gauge.SaveOptions()
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetWaypoint( self ):
        storage = DataStorage.GetInstance()
        field = self.GetField(u'Monitor waypoint')
        if field != None:
            waypointname = self._Waypoints[field[2][1]].encode( "utf-8" )
            waypoints = storage.GetWaypoints()
            if waypointname in waypoints.keys():
                return waypoints[waypointname]

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetDistanceUnits( self ):
        field = self.GetField(u'Distance Units')
        if field != None:
            return self._ShortDistanceUnits[field[2][1]].encode( "utf-8" )

    def GetDistanceTolerance( self ):
        field = self.GetField(u'Distance Tolerance')
        if field != None:
            return self._ToleranceValues[field[2][1]]



class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None
        self.eta = 0
        self.GetOptions()

    def GetOptions(self):
        s = DataStorage.GetInstance()
        t = s.GetValue("wpt_monitor")
        if t == None:
            self.waypoint = "None"
            self.tolerance = 10
        else:
            self.waypoint, self.tolerance = t
        self.distunits = s.GetValue("wpt_distunits")
        self.type = s.GetValue("wpt_type")
        self.tag = u"%s" % self.waypoint

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        #s.SetValue("wpt_monitor",(self.waypoint,self.tolerance))
        s.SetValue("wpt_distunits",self.distunits)
        s.SetValue("wpt_type",self.type)

    def SelectOptions(self):
        form = WaypointForm(self)
        if form.Run():
            self.Draw()

    def UpdateValues(self,heading,bearing,distance,eta):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        if eta != None:
            if eta >= 360000:
                eta = 359999
            self.eta = int(eta/60)
        else:
            self.eta = 0
        self.Draw()

    def _sanevalues(self):
        if self.heading == None or str(self.heading) == 'NaN':
            self.heading = 0
        if self.bearing == None or str(self.bearing) == 'NaN':
            self.bearing = 0
        if self.distance == None or str(self.distance) =='NaN':
            self.distance = 0
        if self.eta == None or str(self.eta) == 'NaN':
            self.eta = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,0x0000ff,handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 180,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 270,self.radius-5,0x000000,handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, 0x00c040, 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, 0x000000, 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            #if self.type == "wpt-dist":
            #    self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0fm' % self.distance)
            #else:
            #    self.DrawText(((self.radius,1.5*self.radius   )),u'%02i:%02i' % (int(self.eta/60),self.eta % 60))
            if self.type == "waypoint":
                self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.bearing)
            else: # self.type == "heading"
                self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.heading)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)


class S60DashView(View):
    def __init__(self):
        DashView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        #self.signalgauge = SignalGauge(None)
        #self.clockgauge = ClockGauge(None)
        self.satgauge = SateliteGauge(None)
        self.waypointgauge = WaypointGauge(None)
        self.speedgauge = SpeedGauge(None)
        self.distancegauge = DistanceGauge(None)
        self.altitudegauge = AltitudeGauge(None)
        self.timegauge = TimeGauge(None)

        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)
        self.positionwidget = PositionWidget((200,15))
        #self.positionwidget = PositionWidget((156,45))
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.optionswidget = TextWidget("Options",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)

        self.gauges = [
                self.waypointgauge,
                self.timegauge,
                self.distancegauge,
                self.satgauge,
                self.altitudegauge,
                self.speedgauge,
            ]
        self.spots = [
                ((0,80),    (160,160)),
                ((0,0),     (80,80)),
                ((80,0),    (80,80)),
                ((160,0),   (80,80)),
                ((160,80),  (80,80)),
                ((160,160), (80,80)),
                ]
        self.zoomedgauge = self.storage.GetValue("dashview_zoom")

        #self.distance = 0
        self.dist_total = self.storage.GetValue("distance_total")
        self.dist_trip = self.storage.GetValue("distance_trip")
        self.wptdistance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.handledkeys = {
            EKeyUpArrow:self.MoveUp,
            EKeyDownArrow:self.MoveDown,
            EKeySelect:self.GaugeOptions,
            }
        self.norepaint = False

    def MoveUp(self,event):
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()

    def MoveDown(self,event):
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()

    def GaugeOptions(self,event):
        print "GaugeOptions: ", self.zoomedgauge
        #self.norepaint = True
        self.gauges[self.zoomedgauge].SelectOptions()
        #self.norepaint = False
        self.update = True
        self.Blit()

    def Resize(self,rect=None):
        size = appuifw.app.body.size
        print "S60MapView.Resize(",size,")"
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)

        if size == (320,240):
            self.spots = [
                    ((98,40),   (160,160)),
                    ((0,20),    (100,100)),
                    ((0,120),   (100,100)),
                    ((250,20),  (70,70)),
                    ((260,90),  (60,60)),
                    ((250,150), (70,70)),
                    ]
            self.satwidget.Resize((50,15))
            self.batwidget.Resize((50,15))
        else:
            self.spots = [
                    ((0,80),    (160,160)),
                    ((0,0),     (80,80)),
                    ((80,0),    (80,80)),
                    ((160,0),   (80,80)),
                    ((160,80),  (80,80)),
                    ((160,160), (80,80)),
                    ]
            self.satwidget.Resize((15,50))
            self.batwidget.Resize((15,50))

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))
            g = self.gauges[i]
            if g:
                p = self.spots[j][0]
                s = self.spots[j][1]
                r = s[0]/2 -2
                g.Resize(r)

        self.update = True
        self.Draw()

    def UpdateDatum(self):
        self.positionwidget.UpdateDatum()
        self.update = True

    def UpdateSignal(self,signal):
        #bat = sysinfo.battery()*7/100
        #gsm = sysinfo.signal_bars()
        #sat = signal.used
        #self.signalgauge.UpdateValues({'bat':bat, 'gsm':gsm, 'sat':sat})
        if signal.used < 4:
            self.satwidget.UpdateValues(signal.used,signal.found)
        else:
            self.satwidget.UpdateValues(signal.used,0)
        self.update = True

    def UpdateSatInfo(self,satlist):
        self.satgauge.UpdateSatInfo(satlist)

    def UpdateTime(self,time,eta):
        if self.time is None:
            self.time = time

        #self.clockgauge.UpdateValue(time)
        self.timegauge.UpdateValues(time,time-self.time,eta,time+eta)
        bat = sysinfo.battery()
        if bat <50:
            self.batwidget.UpdateValues(0,bat)
        else:
            self.batwidget.UpdateValues(bat,0)
        self.update = True

    def UpdatePosition(self,point):
        self.positionwidget.UpdatePosition(point)
        self.latitude = point.latitude
        self.longitude = point.longitude
        self.altitudegauge.UpdateValue(point.altitude)
        self.update = True

    def UpdateDistance(self,distance):
        if str(distance) != "NaN":
            self.dist_total += distance
            self.dist_trip += distance
            self.storage.SetValue("distance_total",self.dist_total)
            #self.storage.SetValue("distance_trip",self.dist_trip)

        self.distancegauge.UpdateValues(self.dist_total,self.dist_trip,self.wptdistance)
        self.update = True

    def UpdateWaypoint(self,heading,bearing,distance,eta):
        self.wptdistance = distance
        self.waypointgauge.UpdateValues(heading,bearing,distance,eta)
        self.update = True

    def UpdateSpeed(self,speed):
        self.speedgauge.UpdateValue(speed*3.6)
        self.update = True

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
    	self.update = False

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))

            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                self.image.blit(
                    image = g.GetImage(),
                    target = (x+2,y+2),
                    source = ((0,0),g.GetImage().size),
                    mask = g.GetMask(),
                    scale = 0 )

        size = appuifw.app.body.size
        if size == (320,240):
            self.image.rectangle((0,0,self.image.size[0],20),fill=0x0000ff)
            self.image.rectangle((0,220,self.image.size[0],self.image.size[1]),fill=0x0000ff)

            w = self.positionwidget
            #w.UpdatePosition(self.mapwidget.GetPosition())
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (70,222),
                source = ((0,0),s),
                scale = 0 )

            w = self.menuwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (320-s[0],240-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.exitwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (320-s[0],0),
                source = ((0,0),s),
                scale = 0 )

            w = self.satwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,4),
                source = ((0,0),s),
                scale = 0 )

            w = self.batwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,224),
                source = ((0,0),s),
                scale = 0 )

        else:
            self.image.rectangle((0,270,self.image.size[0],self.image.size[1]),fill=0x0000ff)

            w = self.positionwidget
            #w.UpdatePosition(self.mapwidget.GetPosition())
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (20,275),
                source = ((0,0),s),
                scale = 0 )

            w = self.menuwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (20,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.exitwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (220-s[0],320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.satwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (0,270),
                source = ((0,0),s),
                scale = 0 )

            w = self.batwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (225,270),
                source = ((0,0),s),
                scale = 0 )

        w = self.optionswidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (120-s[0]/2,320-s[1]),
            source = ((0,0),s),
            scale = 0 )

    def Blit(self,rect=None):
    	if self.update:
    	    self.Draw()
        if self.image != None and not self.norepaint:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            try:
                self.handledkeys[key](event)
            except:
                XStore()

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)


class S60MapView(View):
    def __init__(self):
        MapView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        self.mapwidget = MapWidget((230,260))
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.editwidget = TextWidget("Find map",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.positionwidget = PositionWidget((200,15))

        self.distance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.track = None
        self.position = self.storage.GetValue("app_lastknownposition")

        self.handledkeys = {
            EKeyUpArrow:self.ZoomIn,
            EKeySelect:self.FindMap,
            EKeyDownArrow:self.ZoomOut,
            EKey2:self.MoveUp,
            EKey4:self.MoveLeft,
            EKey5:self.FollowGPS,
            EKey6:self.MoveRight,
            EKey8:self.MoveDown,
            }

        name = self.storage.GetValue("mapview_lastmap")
        if name in self.storage.maps.keys():
            self.map = self.storage.maps[name]
            self.LoadMap(self.map)

        #for map in self.storage.maps:
        #    if map.name == name:
        #        self.map = map

        #self.LoadMap(map)

    def UpdateMenu(self):
        Application.GetInstance().UpdateMenu()

    def GetPosition(self):
        return self.mapwidget.GetPosition()

    def ClearRefpoints(self):
        self.mapwidget.ClearRefpoints()
        self.Draw()

    def AddRefpoint(self,name,lat,lon):
        self.mapwidget.AddRefpoint(name,lat,lon)

    def SaveCalibrationData(self):
        self.mapwidget.SaveCalibrationData()

    def MoveUp(self,event=None):
        self.mapwidget.Move(UP)
        self.followgps = True
        self.Draw()

    def MoveDown(self,event=None):
        self.mapwidget.Move(DOWN)
        self.Draw()

    def MoveLeft(self,event=None):
        self.mapwidget.Move(LEFT)
        self.Draw()

    def MoveRight(self,event=None):
        self.mapwidget.Move(RIGHT)
        self.Draw()

    def FollowGPS(self,event=None):
        self.mapwidget.FollowGPS()
        self.Draw()

    def SetRecordingTrack(self,track):
        self.mapwidget.SetRecordingTrack(track)

    def LoadMap(self,map):
        self.storage.SetValue("mapview_lastmap",map.name)
        self.mapwidget.SetMap(map)
        self.Draw()

    def OpenTrack(self,track):
        self.mapwidget.UpdateTrack(track=track)
        self.Draw()

    def CloseTrack(self):
        self.mapwidget.LoadMap()
        self.Draw()

    def OpenRoute(self,route):
        self.mapwidget.UpdateRoute(route=route)
        self.Draw()

    def CloseRoute(self):
        self.mapwidget.LoadMap()
        self.Draw()

    def UnloadMap(self):
        self.mapwidget.ClearMap()
        self.Draw()

    def FindMap(self,event):
        #print "Locating map..."
        if self.position != None:
            availablemaps = self.storage.FindMaps(self.position)
            count = len(availablemaps)
            if self.mapwidget.map == None:
                onmap = False
            else:
                onmap = (self.mapwidget.map.PointOnMap(self.position) != None)

            if count > 0:
                if count>1 and onmap:
                    id = 0

                    d = {}
                    for m in availablemaps:
                        d[m.name]=m

                        maps = d.keys()
                        maps.sort()

                    id = appuifw.selection_list(maps)
                    if id is not None:
                        #print "opening %s" % maps[id]
                        self.LoadMap(d[maps[id]])
                        self.mapwidget.FollowGPS()
                        appuifw.note(u"Map %s opened." % maps[id], "info")
                        self.UpdateMenu()
                    else:
                        print "no file selected for opening"

                if not onmap:
                    self.LoadMap(availablemaps[0])
                    appuifw.note(u"Map %s opened." % availablemaps[0].name, "info")
                    self.UpdateMenu()

            else:
                appuifw.note(u"No maps found.", "info")
                print "No map available"
        else:
            appuifw.note(u"No position.", "info")

    def ZoomIn(self,event):
        self.mapwidget.ZoomIn()
        self.update = True
        self.Draw()

    def ZoomOut(self,event):
        self.mapwidget.ZoomOut()
        self.update = True
        self.Draw()

    def Resize(self,rect=None):
        size = appuifw.app.body.size
        print "S60MapView.Resize(",size,")"
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)
        self.update = True

        if size==(240,320):
            self.mapwidget.Resize((230,260))
            self.satwidget.Resize((15,50))
            self.batwidget.Resize((15,50))
        if size==(320,240):
            self.mapwidget.Resize((310,190))
            self.satwidget.Resize((50,15))
            self.batwidget.Resize((50,15))

        self.Draw()

    def UpdateDatum(self):
        self.positionwidget.UpdateDatum()
        self.update = True

    def UpdateSignal(self,signal):
        if signal.used < 4:
            self.satwidget.UpdateValues(signal.used,signal.found)
        else:
            self.satwidget.UpdateValues(signal.used,0)
        self.update = True

    def UpdateTime(self,time,eta):
        bat = sysinfo.battery()
        if bat <50:
            self.batwidget.UpdateValues(0,bat)
        else:
            self.batwidget.UpdateValues(bat,0)
        self.update = True

    def UpdateWaypoints(self):
        self.mapwidget.UpdateWaypoints()
        self.update = True

    def UpdatePosition(self,point):
        #print point.latitude,point.longitude
        self.position = point
        self.mapwidget.UpdatePosition(point)
        self.update = True

    def UpdateDistance(self,distance):
        pass

    def UpdateWaypoint(self,heading,bearing,distance,eta):
        self.mapwidget.UpdateValues(heading,bearing,distance)
        self.update = True

    def UpdateSpeed(self,speed):
        pass

    def UpdateTrack(self,point):
        #self.mapwidget.DrawTrackPoint(point,Color["darkred"])
        self.mapwidget.UpdateTrack(point=point)

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
        if self.image !=None:
            self.update = False


            size = appuifw.app.body.size
            if size == (320,240):
                self.image.rectangle((0,0,self.image.size[0],20),fill=0x0000ff)
                self.image.rectangle((0,220,self.image.size[0],self.image.size[1]),fill=0x0000ff)
                w = self.mapwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,25),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.positionwidget
                w.UpdatePosition(self.mapwidget.GetPosition())
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (70,222),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.menuwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (320-s[0],240-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.exitwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (320-s[0],0),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.satwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,4),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.batwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,224),
                    source = ((0,0),s),
                    scale = 0 )

            else:
                self.image.rectangle((0,270,self.image.size[0],self.image.size[1]),fill=0x0000ff)
                w = self.mapwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,5),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.positionwidget
                w.UpdatePosition(self.mapwidget.GetPosition())
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (20,275),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.menuwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (20,320-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.exitwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (220-s[0],320-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.satwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (0,270),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.batwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (225,270),
                    source = ((0,0),s),
                    scale = 0 )

            w = self.editwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (120-s[0]/2,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

    def Blit(self,rect=None):
        if self.update:
            self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            try:
                self.handledkeys[key](event)
            except:
                XStore()

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)



class S60Application(Application, AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()
        self.storage = DataStorage.GetInstance()
        self.position = Point()
        self.osal = Osal.GetInstance()
        appuifw.app.screen='full'
        appuifw.app.title = u"Tracker v0.20a"
        canvas = appuifw.Canvas(
            event_callback=self.KeyboardEvent,
            redraw_callback=self.Redraw,
            resize_callback=self.Resize
            )
        appuifw.app.body = canvas
        appuifw.app.exit_key_handler=self.Exit

        self.handledkeys = {
            EKeyLeftArrow:self.SelectMapview,
            EKeyRightArrow:self.SelectDashview,
            }

        self.trackalarm = None
        self.track = None
        self.trackname = None

        self.running = True
        self.dashview = S60DashView()
        self.mapview = S60MapView()
        self.views = [ self.mapview, self.dashview ]
        id = self.storage.GetValue("app_lastview")
        self.SelectView(id)

        self.queryfuncs = {
                 "Wgs84" : self.QueryWgs84Position,
                 "RD"    : self.QueryRDPosition,
                 "UTM"   : self.QueryUTMPosition,
                 "DMS"   : self.QueryDMSPosition,
                 "DM"    : self.QueryDMPosition,
                 }
        self.position = self.storage.GetValue("app_lastknownposition")
        self.UpdateMenu()

    def UpdateMenu(self):
        storage = DataStorage.GetInstance()
        map = self.mapview.mapwidget.map

        def HasMaps():
            return len(storage.maps) > 0

        def HasOpenMap():
            return map != None

        def HasRefpoints():
            if HasOpenMap():
                return len(map.refpoints) > 0
            else:
                return False

        def HasWaypoints():
            return len(storage.GetWaypoints()) > 0

        def HasOpenMapAndWaypoints():
            return HasOpenMap() and HasWaypoints()

        def HasTracks():
            return len(storage.tracks) > 0

        def HasOpenTracks():
            return len(storage.GetOpenTracks()) > 0

        def HasRoutes():
            return len(storage.routes) > 0

        def HasOpenRoutes():
            return len(storage.GetOpenRoutes()) > 0

        def IsRecording():
            return self.track != None

        def IsNotRecording():
            return not IsRecording()

        def HasGPXItems():
            return HasWaypoints() or HasOpenTracks()

        def Always():
            return True

        def CreateMenu(items):
            menu = []
            for i in items:
                if i[0]():
                    menu.append((i[1],i[2]))
            if len(menu) > 0:
                return tuple(menu)
            else:
                return None

                # Precondition func       Text in menu               Function to call when selected
                # =================================================================================
        map_items = [
                ( HasMaps,                u'Open',                   self.OpenMap ),
                ( HasOpenMap,             u'Close',                  self.CloseMap ),
                ( HasOpenMap,             u'Add Refpoint',           self.AddRefpoint ),
                ( HasOpenMapAndWaypoints, u'Add Ref from Waypoint',  self.AddRefFromWaypoint ),
                ( HasRefpoints,           u'Save',                   self.SaveCalibrationData ),
                ( HasRefpoints,           u'Clear Refpoints',        self.ClearRefpoints ),
                #( Always,                 u'Options',                self.MapOptions ),
            ]
        wpt_items = [
                ( HasWaypoints,           u'Monitor',                self.MonitorWaypoint ),
                ( Always,                 u'Add',                    self.AddWaypoint ),
                ( HasWaypoints,           u'Delete',                 self.DeleteWaypoint ),
                #( Always,                 u'Options',                self.WaypointOptions ),
            ]
        rte_items = [
                ( HasRoutes,              u'Open',                   self.OpenRoute ),
                ( HasOpenRoutes,          u'Close',                  self.CloseRoute ),
                ( HasRoutes,              u'Delete',                 self.DeleteRoute ),
                #( Always,                 u'Options',                self.RouteOptions ),
            ]
        trk_items = [
                ( IsNotRecording,         u'Start',                  self.StartRecording ),
                ( IsRecording,            u'Stop',                   self.StopRecording ),
                ( HasTracks,              u'Open',                   self.OpenTrack ),
                ( HasOpenTracks,          u'Close',                  self.CloseTrack ),
                ( HasTracks,              u'Delete',                 self.DeleteTrack ),
                #( Always,                 u'Options',                self.TrackOptions ),
            ]
        gpx_items = [
                ( Always,                 u'Import GPX File',        self.GPXImport ),
                ( HasGPXItems,            u'Export GPX File',        self.GPXExport ),
                #( Always,                 u'Options',                self.GPXOptions ),
            ]

        if self.storage.GetValue("app_screensaver"):
           togglescreensaver=(u"Disable Screensaver", self.ToggleScreenSaver)
        else:
           togglescreensaver=(u"Enable Screensaver", self.ToggleScreenSaver)

        menu = [
            togglescreensaver,
            (u'About',                          self.About),
            (u'Datum',
                (
                    (u'Wgs84 (dd.dddddd)',      self.DatumWgs84),
                    (u'Wgs84 (dd mm\'ss.ss\")', self.DatumDMS),
                    (u'Wgs84 (dd mm.mmmm\')',   self.DatumDM),
                    (u'UTM',                    self.DatumUTM),
                    (u'RD',                     self.DatumRD),
                )
            ) ]

        map_menu = CreateMenu(map_items)
        if map_menu != None:
            menu.append( (u'Map', map_menu) )
        wpt_menu = CreateMenu(wpt_items)
        if wpt_menu != None:
            menu.append( (u'Waypoint', wpt_menu) )
        trk_menu = CreateMenu(trk_items)
        if trk_menu != None:
            menu.append( (u'Track', trk_menu) )
        rte_menu = CreateMenu(rte_items)
        if rte_menu != None:
            menu.append( (u'Route', rte_menu) )
        gpx_menu = CreateMenu(gpx_items)
        if gpx_menu != None:
            menu.append( (u'Im/Export', gpx_menu) )

        appuifw.app.menu = menu

    def QueryAndStore(self,msg,type,key):
        value = self.storage.GetValue(key)
        result = appuifw.query(u"%s" % msg, type, value)
        if result != None:
            self.storage.SetValue(key,result)

        return result

    def QueryListAndStore(self,list,key):
        list.sort()
        l = []
        for i in list:
            l.append(u"%s" % i)
        l.sort()

        value = u"%s" % self.storage.GetValue(key)
        if value in l:
            index = l.index(value)
            del(l[index])
            l.insert(0,value)
        else:
            print "Could not find %s in list:" % value, l
        #    index = 0

        result = appuifw.selection_list(l,1)

        if result != None:
            self.storage.SetValue(key,l[result])

        return l[result]

    def DatumWgs84(self):
        self.storage.SetValue("app_datum","Wgs84")
        for view in self.views:
            view.UpdateDatum()

    def DatumDMS(self):
        self.storage.SetValue("app_datum","DMS")
        for view in self.views:
            view.UpdateDatum()

    def DatumDM(self):
        self.storage.SetValue("app_datum","DM")
        for view in self.views:
            view.UpdateDatum()

    def DatumUTM(self):
        self.storage.SetValue("app_datum","UTM")
        ellips = self.QueryListAndStore(datums.Ellipsoid.keys(),"app_ellips")
        appuifw.note(u"Selected UTM with ellips %s" % ellips, "info")
        for view in self.views:
            view.UpdateDatum()

    def DatumRD(self):
        self.storage.SetValue("app_datum","RD")
        for view in self.views:
            view.UpdateDatum()

    def SelectView(self,id):
        if id < 0 or id > 1:
            return

        self.storage.SetValue("app_lastview",id)
        self.view = self.views[id]

        self.view.Resize()

    def SelectMapview(self,event=None):
        self.SelectView(0)

    def SelectDashview(self,event=None):
        self.SelectView(1)

    def Init(self):
        Application.Init(self)
        SetSystemApp(1)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.proximityalarm = None
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)

        self.monitorwaypoint = None
        wpt = self.storage.GetValue("wpt_monitor")
        self.eta = 0
        self.eta_data = None
        if wpt != None:
            name, distance = wpt
            waypoints = self.storage.GetWaypoints()
            if name in waypoints.keys():
                self.proximityalarm=ProximityAlarm(waypoints[name],distance,self)
                self.provider.SetAlarm(self.proximityalarm)
                self.monitorwaypoint = waypoints[name]

        self.provider.StartGPS()
        self.view.Show()

    def UpdateTime(self,time):
        self.time = time

    def UpdateETA(self,heading,bearing,distance):
        if self.eta_data == None:
            self.eta_data = { "start_time": self.time, "max_time": self.time, "start_distance": distance, "max_distance": distance, "eta" : None }
            self.eta = 0
        else:
            if distance > self.eta_data["max_distance"]:
                self.eta_data["max_distance"] = distance
                self.eta_data["max_time"] = self.time
                delta_dist = float(abs(distance - self.eta_data["start_distance"]))
                delta_time = self.time - self.eta_data["start_time"]
                self.eta = delta_time / delta_dist * distance
            else:
                delta_dist = float(self.eta_data["max_distance"] - distance)
                delta_time = self.time - self.eta_data["max_time"]
                self.eta = delta_time / delta_dist * distance

            if self.eta > 360000:
                self.eta = 360000

    def AlarmTriggered(self,alarm):
        if alarm == self.timealarm:
            for view in self.views:
                view.UpdateSignal(alarm.signal)
                view.UpdateTime(alarm.time,self.eta)
                self.UpdateTime(alarm.time)

        if alarm == self.positionalarm:
            self.position = alarm.point
            self.storage.SetValue("app_lastknownposition",self.position )

            if self.proximityalarm != None:
                bearing = self.proximityalarm.bearing
                distance = self.proximityalarm.distance
                self.UpdateETA(alarm.avgheading,bearing,distance)
            else:
                bearing = 0
                distance = 0
                self.eta = 0
                self.eta_data = None

            for view in self.views:
                view.UpdatePosition(alarm.point)
                view.UpdateDistance(alarm.distance)
                view.UpdateWaypoint(alarm.avgheading,bearing,distance,self.eta)
                view.UpdateSpeed(alarm.avgspeed)

        if alarm == self.proximityalarm:
            if alarm.action != None:
                osal = S60Osal.GetInstance()
                try:
                    lat = alarm.point.latitude
                    lon = alarm.point.longitude
                    alt = alarm.point.altitude
                    osal.ExecuteScript(alarm.action,{},{
                        "position":"(%f,%f,%f)" % (lat,lon,alt),
                        })
                except:
                    XStore()

            self.proximityalarm = None
            self.storage.SetValue("wpt_monitor",None)

        if alarm == self.trackalarm:
            if self.track is not None:
                self.track.AddPoint(alarm.point)
                self.mapview.UpdateTrack(alarm.point)

        self.view.Show()

    def IsScreensaverActive(self):
        return self.storage.GetValue("app_screensaver")

    def Run(self):
        osal = Osal.GetInstance()
        while self.running:
            if not self.IsScreensaverActive():
                e32.reset_inactivity()
            osal.Sleep(0.2)

    def Exit(self):
        self.StopRecording()
        self.view.Hide()
        appuifw.note(u"Exiting...", "info")
        self.provider.StopGPS()
        self.running = False
        self.provider.DeleteAlarm(self.timealarm)
        self.provider.DeleteAlarm(self.positionalarm)
        self.storage.CloseAll()
        SetSystemApp(0)
        Application.Exit(self)
        #appuifw.app.set_exit()



    def SelectWaypoint(self,waypoints):
        items = waypoints.keys()
        items.sort()
        index = appuifw.selection_list(items)
        if index != None:
            return waypoints[items[index]]
        else:
            return None

    def QueryWgs84Position(self,lat,lon):
        latitude = appuifw.query(u"Waypoint Latitude:","float",lat)
        if latitude is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        longitude = appuifw.query(u"Waypoint Longitude:","float",lon)
        if longitude is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        return latitude,longitude

    def QueryDMSPosition(self,lat,lon):
        (nd,nm,ns),(ed,em,es) = datums.GetDMSFromWgs84(lat,lon)
        dmslat = appuifw.query(u"Latitude (dd/mm/ss.ss):","text",(u"%i/%i/%f" % (nd,nm,ns)).strip("0"))
        if dmslat is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        nd,nm,ns = map(float, dmslat.split("/"))

        dmslon = appuifw.query(u"Longitude (dd/mm/ss.ss):","text",(u"%i/%i/%f" % (ed,em,es)).strip("0"))
        if dmslon is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        ed,em,es = map(float, dmslon.split("/"))

        lat,lon = datums.GetWgs84FromDMS((nd,nm,ns),(ed,em,es))
        return lat,lon

    def QueryDMPosition(self,lat,lon):
        (nd,nm),(ed,em) = datums.GetDMFromWgs84(lat,lon)
        dmlat = appuifw.query(u"Latitude (dd/mm.mmmm):","text",(u"%i/%f" % (nd,nm)).strip("0"))
        if dmlat is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        nd,nm = map(float, dmlat.split("/"))

        dmlon = appuifw.query(u"Longitude (dd/mm.mmmm):","text",(u"%i/%f" % (ed,em)).strip("0"))
        if dmlon is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        ed,em = map(float, dmlon.split("/"))

        return datums.GetWgs84FromDM((nd,nm),(ed,em))

    def QueryUTMPosition(self,lat,lon):
        ellips = self.storage.GetValue("app_ellips")
        zone,x,y = datums.latlon_to_utm(ellips,lat,lon)
        zone = appuifw.query(u"UTM Zone:","text",zone)
        if zone is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        x = appuifw.query(u"UTM X:","float",x)
        if x == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        y = appuifw.query(u"UTM Y:","float",y)
        if y == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        lat,lon = datums.utm_to_latlon(ellips,zone,x,y)
        return lat,lon

    def QueryRDPosition(self,lat,lon):
        x,y = datums.GetRDFromWgs84(lat,lon)
        x = appuifw.query(u"RD X:","float",x)
        if x == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        y = appuifw.query(u"RD Y:","float",y)
        if y == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        lat,lon = datums.GetWgs84FromRD(x,y)
        return lat,lon

    def QueryPosition(self,lat,lon):
        datum = self.storage.GetValue("app_datum")
        return self.queryfuncs[datum](lat,lon)

    def AddWaypoint(self):
        position = self.view.GetPosition()
        if position == None:
            position = self.position

        pos = self.QueryPosition(position.latitude,position.longitude)
        if pos == None:
            return

        latitude,longitude = pos

        try:
            prevname = self.storage.config["wpt_name"]
        except:
            prevname = ""

        name = appuifw.query(u"Waypoint name:","text",prevname)
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.SaveWaypoint(self.storage.CreateWaypoint(name,latitude,longitude))
            self.storage.config["wpt_name"]=name
            self.mapview.UpdateWaypoints()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create waypoint %s." % name, "error")


    def ClearRefpoints(self):
        self.mapview.ClearRefpoints()
        self.UpdateMenu()

    def AddRefpoint(self):
        pos = self.QueryPosition(self.position.latitude,self.position.longitude)
        if pos == None:
            return

        latitude,longitude = pos

        try:
            prevname = self.storage.config["map_refname"]
        except:
            prevname = ""

        name = appuifw.query(u"Reference name:","text",prevname)
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.AddRefpoint(name,latitude,longitude)
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create refpoint %s." % name, "error")

    def AddRefFromWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.AddRefpoint(waypoint.name,waypoint.latitude,waypoint.longitude)
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create refpoint %s." % waypoint.name, "error")

    def SaveCalibrationData(self):
        self.mapview.SaveCalibrationData()

    def DeleteWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint == None:
            appuifw.note(u"Cancelled.", "info")
            return

        name = waypoint.name
        try:
            self.storage.DeleteWaypoint(waypoint)
            appuifw.note(u"Waypoint %s deleted." % name, "info")
            self.mapview.UpdateWaypoints()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete waypoint %s." % name, "error")

    def QueryAndStore(self,msg,type,key):
        value = self.storage.GetValue(key)
        result = appuifw.query(u"%s" % msg, type, value)
        if result != None:
            self.storage.SetValue(key,result)

        return result

    def _MonitorWaypoint(self,waypoint,tolerance):
        print "_MonitorWaypoint"
        if waypoint != self.monitorwaypoint:
            self.monitorwaypoint = waypoint
            self.eta = 0
            self.eta_data = None

        self.proximityalarm = ProximityAlarm(self.monitorwaypoint,tolerance,self)
        self.provider.SetAlarm(self.proximityalarm)
        self.storage.SetValue("wpt_monitor",(waypoint.name,tolerance))

    def MonitorWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint is not None:
            distance = self.QueryAndStore(u"Notify distance in meters:","float","wpt_tolerance")
            if distance is not None:
                self._MonitorWaypoint(waypoint,distance)
                appuifw.note(u"Monitoring waypoint %s, notify when within %8.0f meters." % (waypoint.name, distance), "info")

    def WaypointOptions(self):
        appuifw.note(u"Not yet implemented.", "info")

    def StartRecording(self):
        trackname = self.QueryAndStore(u"Trackname:","text","trk_name")
        if trackname == None:
            appuifw.note(u"Cancelled.", "info")
            return

        interval = self.QueryAndStore(u"Interval (m):","float","trk_interval")
        if interval is not None:

            try:
                if trackname in self.storage.tracks.keys():
                    track = self.storage.tracks[trackname]
                else:
                    track = Track(self.storage.GetTrackFilename(trackname))
                    self.storage.tracks[trackname]=track

                track.Open()

                self.track = track
                self.trackname = trackname
                self.trackalarm = PositionAlarm(None,interval,self)
                DataProvider.GetInstance().SetAlarm(self.trackalarm)
                self.mapview.SetRecordingTrack(self.track)
                self.UpdateMenu()
            except:
                XStore()
                appuifw.note(u"Unable to start record track %s." % trackname, "error")


    def StopRecording(self):
        if self.track == None:
            return

        DataProvider.GetInstance().DeleteAlarm(self.trackalarm)
        self.trackalarm = None
        self.track = None
        self.trackname = None
        self.mapview.SetRecordingTrack(None)
        appuifw.note(u"Recording stopped.")
        self.UpdateMenu()

    def OpenTrack(self):
        tracks = self.storage.GetTrackNames()
        id = appuifw.selection_list(tracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.OpenTrack(name=tracks[id])
            appuifw.note(u"Track %s opened." % tracks[id], "info")
            self.mapview.OpenTrack(self.storage.tracks[tracks[id]])
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open track %s." % tracks[id], "error")

    def CloseTrack(self):
        opentracks = self.storage.GetOpenTracks()
        id = appuifw.selection_list(opentracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        trackname = opentracks[id]
        try:
            self.storage.CloseTrack(name=trackname)
            appuifw.note(u"Track %s closed." % trackname, "info")
            self.mapview.CloseTrack()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to close track %s." % trackname, "error")

    def DeleteTrack(self):
        tracks = self.storage.GetTrackNames()
        id = appuifw.selection_list(tracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.DeleteTrack(name=tracks[id])
            appuifw.note(u"Track %s deleted." % tracks[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete track %s." % tracks[id], "error")

    def TrackOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def OpenRoute(self):
        routes = self.storage.GetRouteNames()
        id = appuifw.selection_list(routes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.OpenRoute(name=routes[id])
            appuifw.note(u"Route %s opened." % routes[id], "info")
            self.mapview.OpenRoute(self.storage.routes[routes[id]])
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open route %s." % routes[id], "error")

    def CloseRoute(self):
        openroutes = self.storage.GetOpenRoutes()
        id = appuifw.selection_list(openroutes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        routename = openroutes[id]
        try:
            self.storage.CloseRoute(name=routename)
            appuifw.note(u"Route %s closed." % routename, "info")
            self.mapview.CloseRoute()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to close route %s." % trackname, "error")

    def DeleteRoute(self):
        routes = self.storage.GetRouteNames()
        id = appuifw.selection_list(routes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.DeleteRoute(name=routes[id])
            appuifw.note(u"Route %s deleted." % routes[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete route %s." % tracks[id], "error")

    def RouteOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def OpenMap(self):
        d = self.storage.maps

        maps = d.keys()
        maps.sort()

        id = appuifw.selection_list(maps)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.LoadMap(d[maps[id]])
            appuifw.note(u"Map %s opened." % maps[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open map %s." % maps[id], "error")

    def CloseMap(self):
        self.mapview.UnloadMap()
        appuifw.note(u"Map closed.", "info")
        self.UpdateMenu()

    def MapOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def GPXExport(self):
        name = self.QueryAndStore(u"GPX Filename:","text",u"gpx_name")
        if name == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.GPXExport(name)
            appuifw.note(u"Exported waypoints and tracks to %s." % name, "info")
        except:
            XStore()
            appuifw.note(u"Unable to export gpx file %s." % name, "error")

    def GPXImport(self):
        files = FileSelector(self.storage.GetDefaultDrive()+self.storage.GetValue("gpx_dir"),".gpx").files
        keys = files.keys()
        keys.sort()
        id = appuifw.selection_list(keys)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.storage.GPXImport(files[keys[id]])
        appuifw.note(u"GPX file %s imported." % files[keys[id]], "info")
        self.UpdateMenu()
        try:
            self.storage.GPXImport(files[keys[id]])
            appuifw.note(u"GPX file %s imported." % files[keys[id]], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to import gpx file %s." % keys[id], "error")

    def GPXOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def KeyboardEvent(self,event):
        key = event['keycode']
        try:
            if key in self.handledkeys.keys():
                self.handledkeys[key](event)
            else:
                self.view.KeyboardEvent(event)
        except AttributeError:
            pass # view not yet available
        except:
            XStore()


    def Redraw(self,rect=None):
        try:
            if self.view:
                self.view.Show()
        except AttributeError:
            pass # view not yet available
        except:
            XStore()

    def Resize(self,rect=None):
        try:
            if self.view:
                self.view.Resize(rect)
        except AttributeError:
            pass # view not yet available
        except:
            XStore()

    def ToggleScreenSaver(self):
        value = self.storage.GetValue("app_screensaver")
        self.storage.SetValue("app_screensaver",not value)
        self.UpdateMenu()

    def About(self):
        appuifw.note(u"Tracker v0.20.x\n(c) 2007,2008 by Mark Hurenkamp\nThis program is licensed under GPLv2.", "info")

    def Dummy(self):
        appuifw.note(u"Not yet implemented.", "info")
