'''
Nixie Watch - Nixie Tube clock look-a-like inspired by Steve Wozniak
Email jouni dot miettunen at gmail dot com

Copyright (c) 2009 Jouni Miettunen

python -OO
import py_compile
py_compile.compile("nixie.py")

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

1.20 2009-08-09
     New: Support touch-only screen
     New: Support PyS60 1.9.7
1.10 2009-05-05
     New: Support landscape mode and screen rotation
     New: Green and Blue nixie tubes
     New: Remember selected tube color at next startup
1.00 2009-04-23 First release, inspired by Steve "Woz" Wozniak
     http://www.lifehacker.com.au/2009/04/how-apple-co-founder-steve-wozniak-gets-things-done/
     http://en.wikipedia.org/wiki/File:Nixie_Wozniak.jpg
'''

VERSION = u'1.20'

import e32
import appuifw
import graphics
import key_codes
import time

# Find "current directory"
FILE_PATH = None
import sys, os
try:
    raise Exception
except Exception:
    FILE_PATH = os.path.dirname(sys.exc_info()[2].tb_frame.f_code.co_filename)
if not FILE_PATH:
    FILE_PATH = os.getcwd()
FILE_PATH = FILE_PATH + "\\"

# Settings file
FILE_SET = FILE_PATH + u"nixie.set"

# Hardcoded image resolution
XX = YY = 100

RGB_RED = (255, 0, 0)
RGB_BLACK = (0, 0, 0)

# Global variables
canvas = None
img = None
m = None

# Create timers
t_timer = e32.Ao_timer()
t_screen = e32.Ao_timer()

#############################################################
def cb_focus(fg):
    ''' System callback when focus is lost/regained '''
    if fg:
        # Got focus
        t_screen.cancel()
        t_timer.cancel()
        handle_screensaver()
        draw_time()
    else:
        # Lost focus
        t_timer.cancel()
        t_screen.cancel()

def handle_screensaver():
    ''' Reset inactivity timer to disable screen saver '''
    e32.reset_inactivity()
    t_screen.after(4, handle_screensaver)

def cb_redraw(aRect=(0,0,0,0)):
    ''' Overwrite default screen redraw event handler '''
    if img:
        canvas.blit(img)

def cb_resize(aSize=(0,0,0,0)):
    ''' Overwrite default screen resize event handler '''
    if not m:
        return

    global img
    img = graphics.Image.new(canvas.size)
    img.clear(RGB_BLACK)

    x, y = canvas.size
    if x < y:
        # Portrait
        m.dx = (x - 200) / 2
        m.dy = (y - 300) / 4
        m.loc = [\
            (m.dx, m.dy), (m.dx+100, m.dy),
            (0, 0),
            (m.dx, 2*m.dy+100), (m.dx+100, 2*m.dy+100),
            (0, 0),
            (m.dx, 3*m.dy+200), (m.dx+100, 3*m.dy+200)
            ]
    else:
        # Landscape
        m.dx = (x - 300) / 4
        m.dy = (y - 200) / 2
        m.loc = [\
            (m.dx, m.dy), (m.dx, m.dy+100),
            (0, 0),
            (2*m.dx+100, m.dy), (2*m.dx+100, m.dy+100),
            (0, 0),
            (3*m.dx+200, m.dy), (3*m.dx+200, m.dy+100)
            ]

    # Redraw full screen
    m.my_time = "hh:mm:ss"
    draw_time()

def draw_time():
    ''' Draw current time on-screen, using GN-4 Nixie tube pics '''
    if not img:
        return

    t_timer.cancel()

    s = time.ctime()[11:19]
    #if DEBUG: img.text((120, 20), unicode(s), RGB_RED, 'normal')

    # Digit hh:mm:ss
    for i in ([0,1,3,4,6,7]):
        if m.my_time[i] != s[i]:
            d = int(s[i])
            img.blit(m.digit[d], target=m.loc[i], mask=m.mask)

    canvas.blit(img)
    m.my_time = s

    # Next number in about one second
    t_timer.after(1, draw_time)

#############################################################
class MySettings(object):
    def __init__(self, a_file):
        ''' Init by reading data '''
        self.reset()
        f = None
        try:
            f = open(a_file, "r")
            s = f.readline()
            if s:
                self._color = s[0]
            else:
                raise Exception
        except:
            self.reset()
        if f:
            f.close()

    def reset(self):
        ''' Set default data '''
        self._color = 'r'

    def color(self, a_value = None):
        ''' Handle color setting '''
        # r - red
        # g - green
        # b - blue
        if a_value:
            self._color = a_value
        return self._color

    def save(self, a_file):
        ''' Save current data into file '''
        f = open(a_file, "w")
        s = str("%c" % self._color)
        f.write(s)
        f.close()

#############################################################
class Main(object):
    ''' Application related things '''

    def __init__(self):
        ''' Default values '''
        self.my_time = "hh:mm:ss"
        self.user_set = MySettings(FILE_SET)
        #self.t_timer = e32.Ao_timer()

        # Helper variables to position digits on-screen
        self.dx = 0
        self.dy = 0
        self.loc = []

        # Graphics mask by JOM, derivate work from original graphics
        tmp = graphics.Image.open(FILE_PATH + u"nix_mask100.jpg")
        self.mask = graphics.Image.new((XX,YY), mode='L')
        self.mask.blit(tmp)

        # Digit graphics
        self.digit = [None, None, None, None, None, None, None, None, None, None]
        for i in range(10):
            self.digit[i] = graphics.Image.new((XX, YY))
        self.change_color(self.user_set.color())

        #appuifw.app.orientation = 'portrait'
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Nixie Watch'
        appuifw.app.exit_key_handler = self.cb_quit
        appuifw.app.focus = cb_focus
        appuifw.app.menu = [
            (u"Change Color", self.menu_settings),
            (u"About", self.menu_about),
            (u"Exit", self.cb_quit)
        ]

        if e32.pys60_version_info > (1,9):
            # Hide annoying virtual keypad
            # HOX: seems like must be before creating canvas
            appuifw.app.directional_pad = False

        global canvas
        canvas = appuifw.Canvas(
            resize_callback = cb_resize,
            redraw_callback = cb_redraw)
        appuifw.app.body = canvas

        if e32.pys60_version_info > (1,9):
            if appuifw.touch_enabled():
                # Full screen, even when rotated
                a = max(canvas.size)
                canvas.bind(key_codes.EButton1Down, self.cb_touch, ((0,0), (a, a)))

        # Disable screensaver
        handle_screensaver()

    def cb_touch(self, pos=(0, 0)):
        ''' Event handler for touch area '''
        self.pop_options()

    def pop_options(self):
        ''' Query popup with touch screen '''
        i = appuifw.popup_menu([u"Change Color", u"About", u"Exit"], u"Options menu:")
        # Handle selection
        if i == 0:
            self.menu_settings()
        elif i == 1:
            self.menu_about()
        elif i == 2:
            self.cb_quit()

    def change_color(self, a_color):
        # Graphics by Hellbus: http://en.wikipedia.org/wiki/File:Nixie2.gif
        # This file is licensed under the Creative Commons Attribution ShareAlike 3.0
        # License. In short: you are free to share and make derivative works of the
        # file under the conditions that you appropriately attribute it, and that you
        # distribute it only under a license identical to this one.

        # Graphics numbers by JOM, derivate work from original graphics
        if a_color == 'g':
            FILE_PIC = FILE_PATH + u"nixies_green.jpg"
        elif a_color == 'b':
            FILE_PIC = FILE_PATH + u"nixies_blue.jpg"
        else:
            FILE_PIC = FILE_PATH + u"nixies_red.jpg"

        pic = graphics.Image.open(FILE_PIC)
        for i in range(10):
            self.digit[i].blit(pic, source=((i*XX,0)))

        # Redraw full screen
        self.my_time = "hh:mm:ss"
        draw_time()

#     def draw_time(self):
#         ''' Draw current time on-screen, using GN-4 Nixie tube pics '''
#
#         # D*MN !!! Just one call with timer causes memory leak
#         # Was not able to find out reason, help anyone ???
#         # Fix: had to move draw_time outside of the class :(
#
#         self.t_timer.cancel()
#         self.t_timer.after(1, self.draw_time)

    def menu_settings(self):
        ''' Callback for menu item Settings '''
        c = self.user_set.color()
        i = appuifw.popup_menu([u"Red", u"Green", u"Blue"], u"Select Nixie Tube Color:")
        if i == 0:
            color = 'r'
        elif i == 1:
            color = 'g'
        elif i == 2:
            color = 'b'
        else:
            color = c
        if c != color:
            self.user_set.color(color)
            self.change_color(color)

    def menu_about(self):
        ''' Callback for menu item About '''
        appuifw.note(u'Nixie Watch v' + VERSION + u'\n' +\
            u'jouni.miettunen.googlepages.com\n\u00a92009 Jouni Miettunen')

    def cb_quit(self):
        ''' Clean up before exit '''
        t_timer.cancel()
        t_screen.cancel()
        self.user_set.save(FILE_SET)
        app_lock.signal()

#############################################################
m = Main()
cb_resize()

app_lock = e32.Ao_lock()
app_lock.wait()
