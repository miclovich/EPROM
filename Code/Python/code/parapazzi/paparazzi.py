'''
Paparazzi Attack - Simple Sensor game

python -OO
import py_compile
py_compile.compile("paparazzi.py")

Copyright (c) 2008, 2009 Jouni Miettunen
http://jouni.miettunen.googlepages.com/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

1.10 2009-01-28 New: graphics from Silk Icons http://www.famfamfam.com
                New: packaged as SIS, custom icon
1.00 2008-09-05 First release
0.10 2008-09-02 First version at Tapiola swimming hall lobby
'''

import e32
import sys
import os
import appuifw
import graphics
import random
import time
import key_codes

VERSION = u'1.10'

# SENSOR: if exception, it's not available in this device
SENSOR_ACC = False
sensor_acc = None
try:
    import sensor
    from sensor import orientation
    SENSOR = True                # Sensor interface available
except ImportError:
    SENSOR = False               # Sensor interface not available

# Find "current directory"
FILE_PATH = None
if e32.in_emulator():
    # Use this with emulator
    # BUG: Use this with Application Shell in device
    try:
        raise Exception
    except Exception:
        fr = sys.exc_info()[2].tb_frame
        fpath = fr.f_code.co_filename
    fdir, fname = os.path.split(fpath)
    FILE_PATH = fdir
else: #if __name__ == "__main__":
    # Use this with standalone SIS files
    FILE_PATH = os.getcwd()

# Try to load graphics
try:
    s = os.path.join(FILE_PATH, "papa.png")
    pic = graphics.Image.open(s)
    pic_mask = graphics.Image.new((16, 16), mode='L')
    pic_mask.blit(pic, source=(32,0,47,15))

except:
    pic = None
    pic_mask = None

# Global variables
canvas = None
img = None
screen_x = screen_y = 0
star_x = star_y = 0
g_papa_count = 0
g_papa = []

# Timer variables
timer_papa = e32.Ao_timer()
timer_interval = e32.Ao_timer()
g_time = 0
my_interval = 0

# Global color definitions
RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)
RGB_RED = (255, 0, 0)
RGB_YELLOW = (255, 255, 0)

def cb_handle_redraw(dummy=(0, 0, 0, 0)):
    ''' Overwrite default screen redraw event handler '''
    if img:
        canvas.blit(img)

def handle_sensor_data(a_data):
    ''' Raw data as absolute location '''
    d1 = a_data['data_1']   # x-axis
    d2 = a_data['data_2']   # y-axis
    global star_x, star_y
    d1 = max(-100, d1)
    d1 = min(100, d1)
    d2 = max(-100, d2)
    d2 = min(100, d2)
    star_x = screen_x - ((d2 + 100) * screen_x) / 200
    star_y = screen_y - ((d1 + 100) * screen_y) / 200
    draw_frame()

def update_papa():
    ''' Move paparazzis closer '''
    for i in range(g_papa_count):
        x, y = g_papa[i]
        dx = max(5, abs(star_x - x))
        dy = max(5, abs(star_y - y))
        if x < star_x:
            x = int(x + dx/5)
        elif x > star_x:
            x = int(x - dx/5)
        if y < star_y:
            y = int(y + dy/5)
        elif y > star_y:
            y = int(y - dy/5)
        g_papa[i] = (x, y)

def update_interval():
    ''' More paparazzis and faster '''
    timer_papa.cancel()
    # Add new paparazzis
    global my_interval
    if my_interval > 0.05:
        my_interval -= 0.05

    # BUG: should verify star and (x,y) are not overlapping
    x = random.choice(range(screen_x))
    y = random.choice(range(screen_y))
    g_papa.append((x, y))
    x = random.choice(range(screen_x))
    y = random.choice(range(screen_y))
    g_papa.append((x, y))
    global g_papa_count
    g_papa_count += 2

    timer_papa.after(my_interval, update_papa)
    timer_interval.after(1, update_interval)
    e32.reset_inactivity()

def draw_frame():
    ''' Draw everything on-screen '''
    img.clear(RGB_BLACK)
    global star_x, star_y

    # Paparazzis
    done = False
    if pic:
        limit = 8
    else:
        limit = 5
    for i in range(g_papa_count):
        x, y = g_papa[i]
        if pic:
            img.blit(pic, target=(x, y), source=(0,2,15,13))
        else:
            img.point((x, y), width=limit, outline=RGB_RED)
        if abs(star_x-x) < limit and abs(star_y-y) < limit:
            done = True

    # Movie star (on top)
    if pic:
        star_x = min(screen_x-16, star_x)
        star_y = min(screen_y-16, star_y)
        if done:
            img.point((star_x+7, star_y+7), width=20, outline=RGB_RED)
        img.blit(pic, target=(star_x, star_y), source=(16,0,31,15), mask=pic_mask)
    else:
        if done:
            img.point((star_x, star_y), width=20, outline=RGB_RED)
        img.point((star_x, star_y), width=9, outline=RGB_YELLOW)

    # Running time
    img.text((10, 25), unicode(str("%4.2f" % (time.clock() - g_time))), RGB_WHITE, 'normal')

    cb_handle_redraw()
    if done:
        if SENSOR_ACC:
            sensor_acc.disconnect()
        timer_interval.cancel()
        timer_papa.cancel()
        appuifw.note(u'Flash! Paparazzis got you! Flash! Smile! Zap! Comments? Ping!')

def game_init():
    ''' Init new game '''
    global g_papa_count, star_x, star_y, g_papa

    timer_interval.cancel()
    timer_papa.cancel()

    star_x = random.choice(range(screen_x))
    star_y = random.choice(range(screen_y))
    # BUG: should verify star and ab are not overlapping
    x = random.choice(range(screen_x))
    y = random.choice(range(screen_y))
    g_papa_count = 1
    g_papa = []
    g_papa.append((x, y))

    global g_time, my_interval
    g_time = time.clock()
    my_interval = 0.5
    if SENSOR_ACC:
        sensor_acc.connect(handle_sensor_data)
    timer_interval.after(1, update_interval)
    timer_papa.after(my_interval, update_papa)
    draw_frame()

def menu_about():
    ''' Callback for menu item About '''
    appuifw.note(u'Paparazzi v'+VERSION+u'\n'+\
        u'jouni.miettunen.googlepages.com\n\u00a9 2008-2009 Jouni Miettunen')

def cb_quit():
    ''' Clean-up before exit '''
    if SENSOR_ACC:
        sensor_acc.disconnect()
    timer_papa.cancel()
    timer_interval.cancel()
    app_lock.signal()

#############################################################

appuifw.app.orientation = 'portrait'
appuifw.app.screen = 'full'
appuifw.app.title = u'Paparazzi'
appuifw.app.exit_key_handler = cb_quit
appuifw.app.menu = [
    (u"New", game_init),
    (u"About", menu_about),
    (u"Exit", cb_quit)
    ]

canvas = appuifw.Canvas(redraw_callback = cb_handle_redraw)
appuifw.app.body = canvas
img = graphics.Image.new(canvas.size)
screen_x, screen_y = canvas.size

# SENSOR start init after everything else
if SENSOR:
    x, y = screen_x, screen_y
    # returns the dictionary of available sensors
    sensors = sensor.sensors()

    # Does this device have Accelerator Sensor
    if sensors.has_key('AccSensor'):
        SENSOR_ACC = True
        sensor_data = sensors['AccSensor']
        sensor_acc = sensor.Sensor(sensor_data['id'], sensor_data['category'])
        sensor_acc.connect(handle_sensor_data)
# SENSOR finish init after everything else

canvas.bind(key_codes.EKeyEnter, game_init)
canvas.bind(key_codes.EKeySelect, game_init)

game_init()

app_lock = e32.Ao_lock()
app_lock.wait()
