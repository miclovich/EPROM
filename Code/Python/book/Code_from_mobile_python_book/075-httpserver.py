
import BaseHTTPServer, SimpleHTTPServer, cgi, traceback, json

class Server(BaseHTTPServer.HTTPServer):
        allow_reuse_address = True

class Handler(SimpleHTTPServer. SimpleHTTPRequestHandler):

    def do_POST(self):
        try:
            size = int(self.headers["Content-length"])
            msg = json.read(self.rfile.read(size))
            reply = process_json(msg)
        except:
            self.send_response(500)
            self.end_headers()
            print "Function process_json failed:"
            traceback.print_exc()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.write(reply))

    def do_GET(self):

        if '?' in self.path:
            path, query_str = self.path.split("?", 1)
            query = cgi.parse_qs(query_str)
        else:
            path = self.path
            query = {}

        try:
            mime, reply = process_get(path, query)
        except:
            self.send_response(500)
            self.end_headers()
            print >> self.wfile, "Function process_query failed:\n"
            traceback.print_exc(file=self.wfile)
            return

        self.send_response(200)
        self.send_header("mime-type", mime)
        self.end_headers()
        self.wfile.write(reply)


def process_json(msg):
    return msg

def process_get(path, query):
    return "text/plain", "Echo: path '%s' and query '%s'" %\
               (path, query)

def init_server():
    print "Server starts"

init_server()
httpd = Server(('', 9000), Handler)
httpd.serve_forever()

