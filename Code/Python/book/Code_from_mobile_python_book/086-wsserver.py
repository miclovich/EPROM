
import e32, json, camera, graphics, sysinfo, urllib

URL = "http://192.168.0.2:9000"

def json_request(req):
    enc = json.write(req)
    return json.read(urllib.urlopen(URL, enc).read())

def take_photo():
    img = camera.take_photo(size = (640, 480))
    img.save("E:\\Images\\temp.jpg")
    return file("E:\\Images\\temp.jpg").read()

def screenshot():
    img = graphics.screenshot()
    img.save("E:\\Images\\temp.jpg")
    return file("E:\\Images\\temp.jpg").read()

go_on = True
msg = {}
print "Web service starts..."
while go_on:
    ret = {}
    for path in json_request(msg):
        print "Requesting", path
        if path == "/camera.jpg":
            ret[path] = ("image/jpeg", take_photo())
        elif path == "/screenshot.jpg":
            ret[path] = ("image/jpeg", screenshot())
        elif path == "/battery":
            ret[path] = ("text/plain",\
                "Current battery level is %d" %\
                    sysinfo.battery())
        elif path == "/exit":
             go_on = False
        else:
            ret[path] = ("text/plain",\
                         "Unknown resource")
    msg = ret
    e32.ao_sleep(5)
print "Bye!"
