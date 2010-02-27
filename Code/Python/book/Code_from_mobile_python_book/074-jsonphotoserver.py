
import SocketServer, json

class Server(SocketServer.TCPServer):
    allow_reuse_address = True

class Handler(SocketServer.StreamRequestHandler):
    def handle(self):
        msg = json.read(self.rfile.read())
        fname = msg["name"] + ".jpg"
        f = file(fname, "w")
        f.write(msg["jpeg"])
        f.close()
        print "Received photo %s (%d bytes)" %\
                (fname, len(msg["jpeg"]))

server = Server(('', 9000), Handler)
print "WAITING FOR NEW CONNECTIONS.."
server.serve_forever() 
