
import json, socket, camera, appuifw

PHOTO_FILE = u"E:\\Images\\temp.jpg"

def send_photo(name, jpeg):
    msg = {"jpeg": jpeg, "name": name}

    sock = socket.socket(socket.AF_INET,\
                         socket.SOCK_STREAM)
    sock.connect(("192.168.0.2", 9000))
    out = sock.makefile("w")
    out.write(json.write(msg))
    out.close()

while True:
        name = appuifw.query(u"Photo name", "text")
        if not name:
                break
        print "Taking photo.."
        img = camera.take_photo(size = (640, 480))
        img.save(PHOTO_FILE)
        jpeg = file(PHOTO_FILE).read()
        print "Sending photo.."
        send_photo(name, jpeg)
        print "Photo sent ok"
print "Bye!"
