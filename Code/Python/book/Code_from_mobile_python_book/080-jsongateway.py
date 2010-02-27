
import SocketServer, threading, json

conn = {}
conn_lock = threading.Lock()

class ThreadingServer(SocketServer.ThreadingMixIn,\
                      SocketServer.TCPServer):
    allow_reuse_address = True

class Handler(SocketServer.StreamRequestHandler):
    def handle(self):
        print "A new client connected", self.client_address
        msg = json.read_stream(self.rfile)
        if "!name" in msg:
            name = msg["!name"]
            wlock = threading.Lock()
            conn_lock.acquire()
            conn[name] = (wlock, self.wfile)
            conn_lock.release()
            print "Client registered (%s)" % name
            reply = {"ok": u"registered"}
            self.wfile.write(json.write(reply))
            self.wfile.flush()
        else: 
            reply = {"err": u"invalid name"}
            self.wfile.write(json.write(reply))
            return
        self.handle_connection(name)




    def handle_connection(self, name):
            
        while True:
            try:
                msg = json.read_stream(self.rfile)
            except:
                msg = {"!close": True}

            if "!close" in msg:
                print "Client exits (%s): %s" %\
                      (name, self.client_address)
                conn_lock.acquire()
                if name in conn:
                        del conn[name]
                conn_lock.release()
                break
            elif "!dst" in msg:
                wfile = None
                conn_lock.acquire()
                if msg["!dst"] in conn:
                    wlock, wfile = conn[msg["!dst"]]
                conn_lock.release()
                if wfile:   
                    wlock.acquire()
                    try:
                        wfile.write(json.write(msg))
                        wfile.flush()
                    finally:
                        wlock.release()

server = ThreadingServer(('', 9000), Handler)
print "JSON gateway is running!"
print "Waiting for new clients..."
server.serve_forever()
