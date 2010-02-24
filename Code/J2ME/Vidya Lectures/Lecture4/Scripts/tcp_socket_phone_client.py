# this file is the phone client 


import socket

HOST = '10.186.251.56'    # The remote host
PORT = 12008              # The same port as used by the server
print "define socket"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "trying to connect to socket"
s.connect((HOST, PORT))
print "connected!"
s.send('Hello, world')
print "data sent"
data = s.recv(1024)
s.close()
print 'Received', `data`