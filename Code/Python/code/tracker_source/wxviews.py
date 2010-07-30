from views import *
from datastorage import *
from dataprovider import *
import wx
import math
import time
from osal import *

ID_MAP_OPEN=201
ID_MAP_CLOSE=202
ID_MAP_IMPORT=203
ID_MAP_ADDREF=204
ID_MAP_DELREF=205
ID_MAP_CLEAR=206

ID_WP_ADD=304
ID_WP_DEL=305
ID_WP_CLEAR=306

ID_TRACK_OPEN=401
ID_TRACK_CLOSE=402
ID_TRACK_DEL=405
ID_TRACK_CLEAR=406
ID_TRACK_START=407
ID_TRACK_STOP=408

ID_GPX_EXPORT=501
ID_GPX_IMPORT=502

Color = {
          "black":'#000000',
          "white":'#ffffff',
          "darkblue":'#0000ff',
          "darkgreen":'#00ff00',
          "darkred":'#ff0000',
          "cyan":'#00ffff',

          "north":'#8080ff',
          "waypoint":'#40ff40',

          "dashbg":'#e0e0e0',
          "dashfg":'#000000',
          "gaugebg":'#c0c0c0',
          "gaugefg":'#ffffff',

          "batsignal":'#f04040',
          "gsmsignal":'#404040',
          "satsignal":'#4040f0',
          "nosignal":'#e0e0e0'
    }

class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = wx.Font(22, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.fgcolor = Color["black"]
        self.bgcolor = Color["white"]
        self.dc = None
        self.Resize(size)

    def Resize(self,size=None):
        self.size = size
        if self.size == None:
            return

        self.bitmap = wx.EmptyBitmap(size[0],size[1])
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.Draw()

    def GetImage(self):
        return self.dc

    def GetMask(self):
        pass
        #return self.mask

    def Draw(self):
        if self.dc != None:
            self.dc.Clear()
            self.dc.SetPen(wx.Pen(self.bgcolor,1))
            self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
            self.dc.DrawRectangleRect((0,0,self.size[0],self.size[1]))
            self.dc.SetPen(wx.Pen(self.fgcolor,1))


    def GetSize(self):
        return self.size

    def GetTextSize(self,text):
        w,h = self.dc.GetTextExtent(u"%s" % text)
        return (w,h)

    def GetImage(self):
        return self.dc

    def GetMask(self):
        return self.mask

    def DrawText(self,coords,text):
        if self.size == None:
            return

        self.dc.SetFont(self.font)
        self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
        self.dc.SetTextForeground(self.fgcolor)
        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        #y += h
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        self.dc.DrawText(u"%s" % text,x,y)
        return (w,h)

    def DrawRectangle(self,(x,y,w,h),linecolor,fillcolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        if fillcolor is not None:
            dc.SetBrush(wx.Brush(fillcolor,wx.SOLID))
        dc.DrawRectangleRect((0,0,self.size[0],self.size[1]))

    def DrawPoint(self,x,y,linecolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        dc.DrawPoint(x,y)

    def DrawLine(self,x1,y1,x2,y2,linecolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        dc.DrawLine(x1,y1,x2,y2)

    def Blit(self,dc,target,source,scale):
        x1,y1,x2,y2 = target
        x3,y3,x4,y4 = source
        w = x2-x1
        h = y2-y1

        if x3 < 0:
            x1 -= x3
            x3 -= x3
        if y3 < 0:
            y1 -= y3
            y3 -= y3
        print x1,y1,w,h,x3,y3

        self.dc.Blit(x1,y1,w,h,dc,x3,y3)
        #self.dc.Blit(0,0,w,h,dc,0,0)


class TextWidget(Widget):
    def __init__(self,text='',hpad=5,vpad=3,fgcolor=Color["black"],bgcolor=Color["white"]):
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
        self.DrawText( (self.vpad,self.hpad ), u'%s' % self.text)


class PositionWidget(Widget):
    def __init__(self,size = None):
        self.point = None
        Widget.__init__(self,size)

    def UpdatePosition(self,point):
        self.point = point
        self.Draw()

    def Draw(self):
        Widget.Draw(self)
        s=self.GetSize()
        self.DrawRectangle((0,0,s[0],s[1]),Color["black"])
        if self.point:
            w,h = self.DrawText( (5,5),     u"Lat: %8.5f" % self.point.latitude)
            w,h = self.DrawText( (5,5+h+2), u"Lon: %8.5f" % self.point.longitude)
        else:
            w,h = self.DrawText( (5,5),     u"Position")
            w,h = self.DrawText( (5,5+h+2), u"Unknown")


class MapWidget(Widget):
    def __init__(self,size = None):
        Widget.__init__(self,None)
        self.storage = DataStorage.GetInstance()
        self.position = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        self.position = self.storage.GetValue("app_lastknownposition")
        self.UpdatePosition(self.position)
        self.Resize(size)

    def SetRecordingTrack(self,track):
        self.track = track

    def SetMap(self,map):
        self.map = map
        self.mapimage = None
        self.LoadMap()

    def DrawTrackPoint(self,point,color):
        cur = self.map.PointOnMap(point)
        if cur != None:
            self.DrawPoint(cur[0],cur[1],color,width=5,dc=self.mapimage)

    def DrawTrack(self,points,color=Color["darkblue"]):
        for p in points:
            self.DrawTrackPoint(p, color)

    def DrawOpenTracks(self):
        for track in self.storage.tracks.values():
            if track.isopen:
                if track.isrecording:
                    color=Color["red"]
                else:
                    color=Color["darkblue"]

                points = track.FindPointsOnMap(self.map)
                if points != None and len(points) > 1:
                    self.DrawTrack(points,color)
                else:
                    print "No trackpoints"

    def LoadMap(self):
        print "loading map %s " % self.map.filename
        image = wx.Image(u"%s" % self.map.filename,wx.BITMAP_TYPE_JPEG)
        #image.LoadFile(u"%s" % self.map.filename)
        bitmap = wx.BitmapFromImage(image)
        self.mapimage = wx.MemoryDC()
        self.mapimage.SelectObject(bitmap)

        if self.map != None:
            self.map.SetSize(self.mapimage.GetSize().Get())
        self.UpdatePosition(self.position)
        self.lastarea = None
        self.DrawOpenTracks()

    def ClearMap(self):
        self.mapimage = None

    def ScreenArea(self):
        w,h = self.size
        return (2,2,w-2,h-2)

    def UpdatePosition(self,point):
        self.position = point
        if self.map != None:
            self.onmap = self.map.PointOnMap(self.position)
        else:
            self.onmap = None

        self.Draw()

    def MapArea(self):
        p = self.onmap
        if p == None:
            print "not on map"
            if self.lastarea != None:
                return self.lastarea
            return self.ScreenArea()

        x,y = p
        w,h = self.size
        w -= 4
        h -= 4
        self.lastarea = (int(x-w/2),int(y-h/2),int(x+w/2),int(y+h/2))
        print p,self.lastarea
        return self.lastarea

    def DrawCursor(self,coords,color=Color["black"]):
        x,y = coords
        w,h = self.size
        if x <0 or x>=w or y <0 or y>=h:
            return

        self.DrawPoint(x,y,linecolor=color,width=3)
        self.DrawLine(x-10,y,x-5,y,linecolor=color,width=3)
        self.DrawLine(x+10,y,x+5,y,linecolor=color,width=3)
        self.DrawLine(x,y-10,x,y-5,linecolor=color,width=3)
        self.DrawLine(x,y+10,x,y+5,linecolor=color,width=3)

    def Draw(self):
        Widget.Draw(self)
        if self.size != None:
            w,h = self.size
            self.DrawRectangle((0,0,w,h),linecolor=Color["black"],fillcolor=None)
            if self.mapimage != None:
                self.Blit(self.mapimage,target=self.ScreenArea(),source=self.MapArea(),scale=1)

            if self.onmap == None:
                c = Color["black"]
            else:
                c = Color["darkblue"]

            self.DrawCursor((w/2,h/2),c)



class Gauge:
    def __init__(self,radius=None):
        self.Resize(radius)
        self.value = None

    def DrawPoint(self,x,y,color=Color["black"],width=1):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.DrawPoint(x,y)

    def DrawEllipse(self,x1,y1,x2,y2,color=Color['black'],width=1,style=wx.TRANSPARENT,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawEllipse(x1,y1,x2,y2)

    def DrawArc(self,x1,y1,x2,y2,start,end,color=Color['black'],width=1):
        w = x2-x1
        h = y2-y1
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(Color['white'],wx.TRANSPARENT))
        self.dc.DrawEllipticArc(x1,y1,w,h,start,end)

    def DrawPolygon(self,points,color=Color['black'],width=1,style=wx.SOLID,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawPolygon(points)

    def DrawLine(self,x1,y1,x2,y2,color=Color['black'],width=1):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.DrawLine(x1,y1,x2,y2)

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return

        maskbitmap = wx.EmptyBitmap(self.radius*2,self.radius*2)
        maskdc = wx.MemoryDC()
        maskdc.SelectObject(maskbitmap)
        maskdc.SetPen(wx.Pen(Color['black'],1))
        maskdc.SetBrush(wx.Brush(Color['black'],wx.SOLID))
        maskdc.DrawRectangleRect((0,0,self.radius*2,self.radius*2))
        maskdc.SetPen(wx.Pen(Color['white'],1))
        maskdc.SetBrush(wx.Brush(Color['white'],wx.SOLID))
        maskdc.DrawEllipse(0,0,self.radius*2,self.radius*2)
        maskdc.SelectObject(wx.NullBitmap)
        self.mask = wx.Mask(maskbitmap,Color['black'])

        self.bitmap = wx.EmptyBitmap(self.radius*2,self.radius*2)
        self.bitmap.SetMask(self.mask)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.Draw()

    def GetImage(self):
        return self.dc

    def GetMask(self):
        return self.mask

    def Draw(self):
        self.dc.Clear()
        self.DrawEllipse(0,0,self.radius*2,self.radius*2,Color['black'],1,wx.SOLID,Color['white'])


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

        self.dc.SetFont(wx.Font(int(self.radius/5*size), wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.dc.SetTextForeground(Color['black'])
        w,h = self.dc.GetTextExtent(u"%s" % text)
        x,y = coords
        self.dc.DrawText(u"%s" % text,x-w/2,y-h/2)
        return w,h

    def DrawInnerCircle(self,radius,color=Color['black'],circlewidth=1):
        self.DrawEllipse(
            self.radius - radius,
            self.radius - radius,
            self.radius + radius,
            self.radius + radius,
            color, circlewidth )


    def DrawInnerCross(self,color=Color['black'],crosswidth=1):
        self.DrawLine(self.radius, 0, self.radius, self.radius*2,color,crosswidth)
        self.DrawLine(0, self.radius, self.radius*2, self.radius,color,crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                x,y = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.DrawPoint(x,y)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                x1,y1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                x2,y2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.DrawLine(x1,y1,x2,y2)


    def DrawDotHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x,y = self.CalculatePoint(heading,self.radius,length)
        self.DrawPoint(x,y,color,handwidth)


    def DrawLineHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x1,y1 = (self.radius,self.radius)
        x2,y2 = self.CalculatePoint(heading,self.radius,length)
        self.DrawLine(x1,y1,x2,y2,color,handwidth)


    def DrawTriangleHand(self,heading,length,color=Color['black'],handwitdh=5):
        if self.radius == None:
            return

        x,y = self.CalculatePoint(heading,   self.radius,length)
        p1 = wx.Point(x,y)
        x,y = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        p2 = wx.Point(x,y)
        x,y = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        p3 = wx.Point(x,y)
        self.DrawPolygon((p1,p2,p3),color,1,wx.SOLID,color)


class SignalGauge(Gauge):

    def __init__(self,radius=None,items=None):
        Gauge.__init__(self,radius)
        if items is not None:
            self.items = items
        else:
            self.items = {
                'bat':[7,2,5,Color['batsignal']],
                'gsm':[7,2,6,Color['gsmsignal']],
                'sat':[7,2,2,Color['satsignal']],
                }

    def UpdateValues(self,values):
        for key in values.keys():
            self.items[key][2] = values[key]

        self.Draw()

    def DrawSignalArc(self,radius,start,end,width=1,color=Color['black']):
        x1,y1 = (int(self.radius - radius),int(self.radius - radius))
        x2,y2 = (int(self.radius + radius),int(self.radius + radius))
        self.DrawArc(x1,y1,x2,y2, start, end,color,width=width)

    def DrawSignalTag(self,name,pos,color,size=1.0):
        self.dc.SetFont(wx.Font(int(self.radius/5*size), wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.dc.SetTextForeground(color)
        w,h = self.dc.GetTextExtent(u"%s" % name)
        x = self.radius * 1.35
        pos = pos + h
        self.dc.DrawText(u"%s" % name,int(x),int(pos))
        return pos

    def DrawSignal(self,item,start,end):
        w = int(self.radius / item[0] * 0.4)
        if w < 1:
           w = 1

        if item[2] > item[0]:
           v=item[0]
        else:
           v=item[2]

        for i in range (0,v):
            r = self.radius * 0.9 * (i+1)/item[0]
            self.DrawSignalArc(r,start,end,w,item[3])
        for i in range (v,item[0]):
            r = self.radius * 0.9 * (i+1)/item[0]
            self.DrawSignalArc(r,start,end,w,Color['nosignal'])

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        angle = 60
        pos = self.radius/2
        increment = 240 / len(self.items)
        for key in self.items.keys():
            pos = self.DrawSignalTag(key,pos,self.items[key][3])
            self.DrawSignal(self.items[key],angle+10,angle+increment-10)
            angle += increment


class CompasGauge(Gauge):

    def __init__(self,radius=None,tag="heading"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.value = 0

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if (self.radius >= 30):
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' %self.tag)
        if (self.value != None) and (self.radius >= 10):
            if (self.radius >=30):
                self.DrawText(((self.radius,1.6*self.radius)),u'%05.1f' % self.value,size=1.5)
            self.DrawTriangleHand(0-self.value,   self.radius-10, Color['darkblue'], 8)
            self.DrawTriangleHand(180-self.value, self.radius-10, Color['black'], 8)


class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',units=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.units = units
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
            self.DrawText(((self.radius,1.6*self.radius)), self.units % self.value, size=1.5)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, Color['black'], 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, Color['black'], 4)


class DistanceGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'distance',u'%6.2f')
        self.value = 0

    def Draw(self):
        TwoHandGauge.Draw(self)


class AltitudeGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'altitude',u'%8.0f',(100,1000))
        self.value = 0

    def Draw(self):
        TwoHandGauge.Draw(self)

class SpeedGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2f')
        self.value = 0

    def Draw(self):
        TwoHandGauge.Draw(self)

class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None

    def UpdateValues(self,heading,bearing,distance):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        self.Draw()

    def _sanevalues(self):
        if self.heading is None or str(self.heading) is 'NaN':
            self.heading = 0
        if self.bearing is None or str(self.bearing) is 'NaN':
            self.bearing = 0
        if self.distance is None or str(self.distance) is'NaN':
            self.distance = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,Color['north'],handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 180,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 270,self.radius-5,Color['black'],handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, Color['waypoint'], 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, Color['black'], 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0f' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+30)),u'%05.1f' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)


class ClockGauge(Gauge):

    def __init__(self,radius=None,tag="clock"):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.tag = tag
        Gauge.__init__(self,radius)

    def UpdateValue(self,value):
        y,m,d, self.hours, self.minutes, self.seconds, a,b,c = time.localtime(value)
        self.Draw()

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
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds),size=1.3)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, Color['black'], 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)

class WXAppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY, "Tracker v0.20a", size = (488,706))

        # A Statusbar in the bottom of the window
        self.CreateStatusBar()

        # Setting up the map menu.
        mapmenu= wx.Menu()
        mapmenu.Append(ID_MAP_IMPORT,"Import","Import a map (from jpg)")
        mapmenu.Append(ID_MAP_ADDREF,"Calibrate","Add a reference point for the current map")
        mapmenu.Append(ID_MAP_DELREF,"Clear","Remove reference points from the current map")

        # Setting up the waypoint menu.
        wpmenu= wx.Menu()
        wpmenu.Append(ID_WP_ADD,"Add","Define a new waypoint")
        wpmenu.Append(ID_WP_DEL,"Delete","Delete a waypoint")
        wpmenu.Append(ID_WP_CLEAR,"Clear","Delete all waypoints")

        # Setting up the track menu.
        trackmenu= wx.Menu()
        trackmenu.Append(ID_TRACK_START,"Start","Start recording a new track")
        trackmenu.Append(ID_TRACK_STOP,"Stop","Stop recording")
        trackmenu.Append(ID_TRACK_OPEN,"Open","Load a track")
        trackmenu.Append(ID_TRACK_CLOSE,"Close","Load a track")
        trackmenu.Append(ID_TRACK_DEL,"Delete","Delete a track")

        # Setting up the track menu.
        gpxmenu= wx.Menu()
        gpxmenu.Append(ID_GPX_EXPORT,"Export","Export open waypoints and tracks to a gpx file")
        gpxmenu.Append(ID_GPX_IMPORT,"Import","Import waypoints and tracks from a gpx file")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(mapmenu,"Map") # Adding the "filemenu" to the MenuBar
        menuBar.Append(wpmenu,"Waypoint") # Adding the "filemenu" to the MenuBar
        menuBar.Append(trackmenu,"Track") # Adding the "filemenu" to the MenuBar
        menuBar.Append(gpxmenu,"GPX") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

class WXDashView(wx.PyControl,DashView):
    def __init__(self,frame):
        wx.PyControl.__init__(self,frame)
        DashView.__init__(self)
        self.storage = DataStorage.GetInstance()
        self.frame = frame

        #self.clockgauge = ClockGauge(None)
        self.signalgauge = SignalGauge(None)
        self.waypointgauge = WaypointGauge(None)
        #self.headinggauge = CompasGauge(None)
        self.speedgauge = SpeedGauge(None)
        self.distancegauge = DistanceGauge(None)
        self.altitudegauge = AltitudeGauge(None)
        self.timegauge = ClockGauge(None,"time")
        self.positionwidget = PositionWidget((312,90))
        self.menuwidget = TextWidget("Menu",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        self.editwidget = TextWidget("Edit",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        self.exitwidget = TextWidget("Exit",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        #self.menuwidget.Draw()
        self.track = None

        self.gauges = [
                self.signalgauge,
                self.timegauge,
                self.distancegauge,
                self.speedgauge,
                self.altitudegauge,
                self.waypointgauge
            ]
        self.spots = [
                ((0,0),     (160,160)),
                ((160,0),   (160,160)),
                ((320,0),   (160,160)),
                ((320,160), (160,160)),
                ((320,320), (160,160)),
                ((0,160),   (320,320)),
                ]
        self.zoomedgauge = self.storage.GetValue("dashview_zoom")

        self.distance = 0
        self.time = None
        self.update = True

        self.Resize()
        self.handledkeys = {
            wx.WXK_UP:self.MoveUp,
            wx.WXK_DOWN:self.MoveDown,
            wx.WXK_NUMPAD8:self.MoveUp,
            wx.WXK_NUMPAD2:self.MoveDown
            }

        wx.EVT_PAINT (self.frame, self.OnPaint)
        wx.EVT_KEY_DOWN (self.frame, self.OnKeyDown)

        wx.EVT_MENU(self.frame, ID_TRACK_START, self.OnTrackStart)
        wx.EVT_MENU(self.frame, ID_TRACK_STOP, self.OnTrackStop)
        wx.EVT_MENU(self.frame, ID_TRACK_OPEN, self.OnTrackOpen)
        wx.EVT_MENU(self.frame, ID_TRACK_CLOSE, self.OnTrackClose)
        wx.EVT_MENU(self.frame, ID_TRACK_DEL, self.OnTrackDelete)

        wx.EVT_MENU(self.frame, ID_GPX_EXPORT, self.OnGPXExport)
        wx.EVT_MENU(self.frame, ID_GPX_IMPORT, self.OnGPXImport)

    def MoveUp(self,event):
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        print self.zoomedgauge
        self.storage.config["zoomedgauge"]=str(self.zoomedgauge)
        self.Resize()

    def MoveDown(self,event):
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        print self.zoomedgauge
        self.storage.config["zoomedgauge"]=str(self.zoomedgauge)
        self.Resize()

    def UpdateSignal(self,signal):
        bat = 7
        gsm = 0
        sat = signal.used
        self.signalgauge.UpdateValues({'bat':bat, 'gsm':gsm, 'sat':sat})

    def UpdateTime(self,time):
        if self.time is None:
            self.time = time

        #self.clockgauge.UpdateValue(time)
        self.timegauge.UpdateValue(time-self.time)
        self.update = True

    def UpdatePosition(self,point):
        self.positionwidget.UpdatePosition(point)
        self.latitude = point.latitude
        self.longitude = point.longitude
        self.altitudegauge.UpdateValue(point.altitude)
        self.update = True

    def UpdateDistance(self,distance):
        if str(distance) != "NaN":
            self.distance += distance
        self.distancegauge.UpdateValue(self.distance/1000)
        self.update = True

    def UpdateWaypoint(self,heading,bearing,distance):
        self.waypointgauge.UpdateValues(heading,bearing,distance)
        self.update = True

    def UpdateHeading(self,heading):
        self.headinggauge.UpdateValue(heading)
        self.update = True

    def UpdateSpeed(self,speed):
        self.speedgauge.UpdateValue(speed*3.6)
        self.update = True

    def Resize(self,rect=None):
        self.panel=wx.Panel(self.frame,size=(480,640))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(480,640)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        for i in range(0,len(self.spots)):
            j = (self.zoomedgauge+i) % (len(self.spots))
            g = self.gauges[i]
            if g:
                p = self.spots[j][0]
                s = self.spots[j][1]
                r = s[0]/2 -2
                g.Resize(r)

        self.update = True

    def OnPaint(self,event):
        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def OnUpdate(self,event):
        self.Draw()
        dc = wx.ClientDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def OnKeyDown(self,event):
        print "OnKeyDown"
        key = event.KeyCode
        if key in self.handledkeys:
            print "->Handlekey"
            self.handledkeys[key](event)
        else:
            event.Skip()

    def OnTrackStart(self,event):
        print "Starting track"
        self.track = DataStorage.GetInstance().OpenTrack('newtrack',True,25)

    def OnTrackStop(self,event):
        print "Stopping track"
        DataStorage.GetInstance().StopRecording()

    def OnTrackOpen(self,event):
        trackname = "newtrack"
        self.storage.tracks[trackname].Open()
        self.mapwidget.UpdateTrack(track=self.storage.tracks[trackname])
        self.Draw()


    def OnTrackClose(self,event):
        print "Closing track"
        DataStorage.GetInstance().CloseTrack(self.track)

    def OnTrackDelete(self,event):
        print "Deleting track"
        DataStorage.GetInstance().DeleteTrack('newtrack')

    def OnGPXExport(self,event):
        print "Export to GPX"
        DataStorage.GetInstance().GPXExport('newtrack')

    def OnGPXImport(self,event):
        print "Import from GPX"
        DataStorage.GetInstance().GPXImport('newtrack')

    def Draw(self,rect=None):
        self.update = False
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,480,640))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        for i in range(0,len(self.spots)):
            j = (self.zoomedgauge+i) % (len(self.spots))
            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                w,h = g.dc.GetSize()
                self.dc.Blit(
                    x+2,y+2,w,h,
                    g.dc,0,0,useMask=True )

        w,h = self.positionwidget.GetSize()
        self.dc.Blit(
            6,500,w,h,
            self.positionwidget.GetImage(),0,0 )

        w,h = self.menuwidget.GetSize()
        self.dc.Blit(
            10,640-h,w,h,
            self.menuwidget.GetImage(),0,0 )

        w,h = self.editwidget.GetSize()
        self.dc.Blit(
            240-w/2,640-h,w,h,
            self.editwidget.GetImage(),0,0 )

        w,h = self.exitwidget.GetSize()
        self.dc.Blit(
            470-w,640-h,w,h,
            self.exitwidget.GetImage(),0,0 )


class WXMapView(wx.PyControl,MapView):
    def __init__(self):
        MapView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        self.mapwidget = MapWidget((460,590))
        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Find map",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])

        self.distance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.position = self.storage.GetValue("app_lastknownposition")

        self.handledkeys = {
            EKeyUpArrow:self.MoveUp,
            EKeySelect:self.FindMap,
            EKeyDownArrow:self.MoveDown
            }

        self.Resize()

    def __init__(self,frame):
        wx.PyControl.__init__(self,frame)
        MapView.__init__(self)
        self.storage = DataStorage.GetInstance()
        self.frame = frame

        self.mapwidget = MapWidget((460,590))
        self.menuwidget = TextWidget("Menu",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        self.editwidget = TextWidget("Find map",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        self.exitwidget = TextWidget("Exit",fgcolor=Color['white'],bgcolor=Color['darkblue'])
        #self.menuwidget.Draw()
        self.track = None

        self.distance = 0
        self.time = None
        self.update = True

        self.Resize()
        self.handledkeys = {
            wx.WXK_UP:self.MoveUp,
            wx.WXK_DOWN:self.MoveDown,
            wx.WXK_NUMPAD8:self.MoveUp,
            wx.WXK_NUMPAD2:self.MoveDown
            }

        wx.EVT_PAINT (self.frame, self.OnPaint)
        wx.EVT_KEY_DOWN (self.frame, self.OnKeyDown)

        wx.EVT_MENU(self.frame, ID_TRACK_START, self.OnTrackStart)
        wx.EVT_MENU(self.frame, ID_TRACK_STOP, self.OnTrackStop)
        wx.EVT_MENU(self.frame, ID_TRACK_OPEN, self.OnTrackOpen)
        wx.EVT_MENU(self.frame, ID_TRACK_CLOSE, self.OnTrackClose)
        wx.EVT_MENU(self.frame, ID_TRACK_DEL, self.OnTrackDelete)

        wx.EVT_MENU(self.frame, ID_GPX_EXPORT, self.OnGPXExport)
        wx.EVT_MENU(self.frame, ID_GPX_IMPORT, self.OnGPXImport)

        self.position = self.storage.GetValue("app_lastknownposition")
        self.FindMap()


    def LoadMap(self,map):
        self.storage.SetValue("mapview_lastmap",map.name)
        self.mapwidget.SetMap(map)
        self.Draw()

    def UnloadMap(self):
        self.mapwidget.ClearMap()
        self.Draw()

    def FindMap(self,event=None):
        print "Locating map..."
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
                        print "opening %s" % maps[id]
                        self.LoadMap(d[maps[id]])
                        print "Map %s opened." % maps[id]
                        #appuifw.note(u"Map %s opened." % maps[id], "info")
                    else:
                        print "no file selected for opening"

                if not onmap:
                    self.LoadMap(availablemaps[0])
                    #appuifw.note(u"Map %s opened." % availablemaps[0].name, "info")
                    print "Map %s opened. " % availablemaps[0].name
            else:
                #appuifw.note(u"No maps found.", "info")
                print "No map available"
        else:
            #appuifw.note(u"No position.", "info")
            print "No position"

    def MoveUp(self,event):
        pass

    def MoveDown(self,event):
        pass

    def Resize(self,rect=None):
        self.panel=wx.Panel(self.frame,size=(480,640))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(480,640)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)
        self.update = True


    def UpdateSignal(self,signal):
        pass

    def UpdateTime(self,time):
        pass

    def UpdatePosition(self,point):
        #print point.latitude,point.longitude
        self.position = point
        self.mapwidget.UpdatePosition(point)
        if not self.mapwidget.onmap:
            self.FindMap()
        self.update = True
        if self.track != None:
            k = self.track.data.keys()
            k.remove("name")
            k.sort()
            if len(k)>1:
                p = eval(self.track.data[k[-1]])
                self.mapwidget.DrawTrackPoint(Point(k[-1],p[0],p[1],p[2]),Color["darkred"])

    def UpdateDistance(self,distance):
        pass

    def UpdateWaypoint(self,heading,bearing,distance):
        pass

    def UpdateSpeed(self,speed):
        pass

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):

        self.update = False
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,480,640))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        w,h = self.mapwidget.GetSize()
        self.dc.Blit(
            6,6,w,h,
            self.mapwidget.GetImage(),0,0 )

        w,h = self.menuwidget.GetSize()
        self.dc.Blit(
            10,640-h,w,h,
            self.menuwidget.GetImage(),0,0 )

        w,h = self.editwidget.GetSize()
        self.dc.Blit(
            240-w/2,640-h,w,h,
            self.editwidget.GetImage(),0,0 )

        w,h = self.exitwidget.GetSize()
        self.dc.Blit(
            470-w,640-h,w,h,
            self.exitwidget.GetImage(),0,0 )

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            self.handledkeys[key](event)

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)

    def OnPaint(self,event):
        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def OnUpdate(self,event):
        self.Draw()
        dc = wx.ClientDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def OnKeyDown(self,event):
        print "OnKeyDown"
        key = event.KeyCode
        if key in self.handledkeys:
            print "->Handlekey"
            self.handledkeys[key](event)
        else:
            event.Skip()

    def OnTrackStart(self,event):
        track = Track(self.storage.GetTrackFilename('newtrack'))
        track.Open()
        self.track = track
        self.trackname = 'newtrack'
        self.trackalarm = PositionAlarm(None,10,self)
        DataProvider.GetInstance().SetAlarm(self.trackalarm)
        self.mapwidget.SetRecordingTrack(self.track)

    def OnTrackStop(self,event):
        self.storage.tracks[self.trackname]=self.track
        DataProvider.GetInstance().DeleteAlarm(self.trackalarm)
        self.trackalarm = None
        self.track = None
        self.trackname = None
        self.mapwidget.SetRecordingTrack(None)

    def OnTrackOpen(self,event):
        print "Opening track"
        print DataStorage.GetInstance().tracks.keys()
        self.track = DataStorage.GetInstance().tracks['newtrack']
        self.track.Open()
        self.mapwidget.DrawOpenTracks()

    def OnTrackClose(self,event):
        print "Closing track"
        self.track.Close()
        self.mapwidget.LoadMap()

    def OnTrackDelete(self,event):
        print "Deleting track"
        DataStorage.GetInstance().DeleteTrack(name='newtrack')

    def OnGPXExport(self,event):
        print "Export to GPX"
        DataStorage.GetInstance().GPXExport('newtrack')

    def OnGPXImport(self,event):
        print "Import from GPX"
        DataStorage.GetInstance().GPXImport('newtrack')


class WXApplication(Application,AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()
        self.storage = DataStorage.GetInstance()
        self.app = wx.PySimpleApp()
        self.frame = WXAppFrame()
        self.view = WXMapView(self.frame)
        #self.view = WXDashView(self.frame)

    def Init(self):
        Application.Init(self)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.proximityalarm = None
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)
        self.provider.StartGPS()

    def AlarmTriggered(self,alarm):
        if not self.view:
            return

        if alarm == self.timealarm:
            self.view.UpdateSignal(alarm.signal)
            self.view.UpdateTime(alarm.time)

        if alarm == self.positionalarm:
            self.position = alarm.point

            self.view.UpdatePosition(alarm.point)
            self.view.UpdateDistance(alarm.distance)
            if self.proximityalarm is not None:
                bearing = self.proximityalarm.bearing
                distance = self.proximityalarm.distance
            else:
                bearing = 0
                distance = 0
            self.view.UpdateWaypoint(alarm.avgheading,bearing,distance)
            self.view.UpdateSpeed(alarm.avgspeed)

        self.view.Refresh(True,wx.Rect(0,0,480,640))
        self.view.Update()
        self.view.OnUpdate(None)

    def Run(self):
        self.view.Show()
        self.app.MainLoop()

    def Exit(self):
        self.provider.StopGPS()
        self.storage.CloseAll()
        Application.Exit(self)
