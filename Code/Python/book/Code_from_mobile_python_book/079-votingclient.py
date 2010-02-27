
import sysinfo, urllib, json, appuifw

URL = "http://192.168.0.2:9000"
imei = sysinfo.imei()

def json_request(req):
    enc = json.write(req)
    return json.read(urllib.urlopen(URL, enc).read())

def poll_server():
    global voted_already
    res = json_request({"voter":imei})
    votes, winner = res["winner"]

    if "closed" in res:
        appuifw.note(u"Winner is %s with %d votes" %\
                        (winner, votes))
        lock.signal()
        return False
    
    elif not voted_already and "title" in res:
        appuifw.app.title = u"Vote: %s" % res["title"]
        names = []
        for name in res["choices"]:
                names.append(unicode(name))
        idx = appuifw.selection_list(names)
        if idx == None:
                lock.signal()
                return False
        else:
                res = json_request({"voter":imei, "choice":names[idx]})
                appuifw.note(unicode(res["msg"]))
                voted_already = True
                print "Waiting for final results..."
    else:
        print "%s has most votes (%d) currently" % (winner, votes)

    e32.ao_sleep(5, poll_server)
    return True

voted_already = False
lock = e32.Ao_lock()
print "Contacting server..."
if poll_server():
        lock.wait()
print "Bye!"
