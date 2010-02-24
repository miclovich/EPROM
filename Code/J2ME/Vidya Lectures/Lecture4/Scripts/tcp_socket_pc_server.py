# this file is the PC server 



import socket

HOST = ''                 # Symbolic name meaning the local host
PORT = 12008              # Arbitrary non-privileged port
print "defining the socket"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "binding the socket"
s.bind((HOST, PORT))
s.listen(1)
print "waiting for the client to connect..."
conn, addr = s.accept()
print 'Connected by', addr
while 1:
    data = conn.recv(1024)
    if not data: break
    conn.send(data)
conn.close()