
import e32, json, camera, graphics, sysinfo, urllib

URL = "http://192.168.0.2:9000"
imei = sysinfo.imei()

def json_request(req):
    enc = json.write(req)
    return json.read(urllib.urlopen(URL, enc).read())

def RSC_screenshot_jpg():
    img = graphics.screenshot()
    img.save("c:\\python\\temp.jpg")
    data = file("c:\\python\\temp.jpg").read()
    return ("image/jpeg", data)

def RSC_battery():
    txt = "Current battery level is %d" %\
                    sysinfo.battery()
    return ("text/plain", txt)

def RSC_exit():
    global go_on
    go_on = False

go_on = True
msg = {}
while go_on:
    ret = {}
    for path in json_request(msg):
        rsc = "RSC_%s" % path[1:].replace(".", "_")
        if rsc in globals():
            ret[path] = globals()[rsc]()
        else:
            ret[path] = ("text/plain",\
                         "Unknown resource")
    msg = ret
    e32.ao_sleep(5)
