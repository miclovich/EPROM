
import appuifw, e32, camera, thread, socket, json, graphics
SERVER = ("192.168.0.2", 9000)

def send_message(msg):
    global to_server
    try:
        to_server.write(json.write(msg))
        to_server.flush()
        thread_handle_message({"note": u"Message sent!"})
    except Exception, ex:
        print "Connection error", ex
        to_server = None

def read_message():
    global to_server
    try:
        msg = json.read_stream(to_server)
        thread_handle_message(msg)
    except Exception:
        print "Broken connection"
        to_server = None
    
def connect():
    global to_server, keep_talking, conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(SERVER)
    to_server = conn.makefile("rw", 8192)
    send_message({"!name": me})
    ret = json.read_stream(to_server)
    if "err" in ret:
        thread_handle_message({"note": u"Login failed"})
        thread_show_note(u"Login failed: %s" % ret["err"], "error")
        keep_talking = False
        raise "Login failed"
    else:
        thread_handle_message({"note": u"Login ok"})
        
def communicate():
    global to_server, keep_talking, thread_send_message, app_lock
    thread_send_message = e32.ao_callgate(send_message)
    to_server = None
    while keep_talking:
        if to_server:
            read_message()
        else:
            try:
                connect()            
                thread_handle_message(\
                        {"note": u"Waiting for messages..."})
            except:
                print "Could not connect to server"
                to_server = None
                if keep_talking:
                        e32.ao_sleep(10)
    if conn: conn.close()
    if to_server: to_server.close()


def show_photo(jpeg_data):
    global img
    f = file("E:\\Images\\msg.jpg", "w")
    f.write(jpeg_data)
    f.close()
    img = graphics.Image.open("E:\\Images\\msg.jpg")
    
def handle_message(msg):
    global text, note
    if "photo" in msg:
        show_photo(msg["photo"])
        text = {"from": msg["from"], "txt": ""}
    elif "txt" in msg:
        text = msg
    elif "note" in msg:
        note = msg["note"]
    redraw(None)

def send_photo():
    handle_message({"note": u"Taking photo..."})
    dst = appuifw.query(u"To", "text")
    img = camera.take_photo(size = (640, 480))
    img = img.resize((320, 240))
    img.save("E:\\Images\\temp.jpg")
    jpeg = file("E:\\Images\\temp.jpg").read()
    handle_message({"note": u"Sending photo..."})
    thread_send_message({"!dst": dst, "photo": jpeg, "from": me})

def send_text():
    resp = appuifw.multi_query(u"To", u"Message")
    if resp:
            dst, txt = resp
            thread_send_message({"!dst": dst, "txt": txt, "from": me})




def quit():
    global keep_talking, to_server, conn
    keep_talking = False
    thread_send_message({"!close": True})
    app_lock.signal()

def redraw(rect):
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)

        canvas.clear((255, 255, 255))
        if img:
                canvas.blit(img, scale = 1)
        if note:
                canvas.text((10, canvas.size[1] - 30), note,\
                        fill = RED, font = "title")
        if text:
                canvas.text((10, 80), u"From: %s" % text["from"],\
                        fill = GREEN, font = "title")
                canvas.text((10, 110), unicode(text["txt"]),\
                        fill = BLUE, font = "title")

img = text = note = None
keep_talking = True
thread_handle_message = e32.ao_callgate(handle_message)
appuifw.app.exit_key_handler = quit
appuifw.app.title = u"Instant Messenger"
appuifw.app.menu = [(u"Send Photo", send_photo),\
                    (u"Send Text", send_text)]

canvas = appuifw.Canvas(redraw_callback = redraw)
appuifw.app.body = canvas

me = appuifw.query(u"Login name", "text")
handle_message({"note": u"Contacting server..."})
if me:
        app_lock = e32.Ao_lock()
        thread.start_new_thread(communicate, ())
        if keep_talking:
                app_lock.wait()
