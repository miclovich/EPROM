# this file lets 2 phones exchange data via RFCOMM
# this file is the server side
# the corresponding client side file is called rfcomm_client.py

from socket import *
import appuifw
import e32

server_socket = socket(AF_BT, SOCK_STREAM)
channel = bt_rfcomm_get_available_server_channel(server_socket)
server_socket.bind(("", channel))
print "binding done."
server_socket.listen(1)
bt_advertise_service( u"sjsuserver", server_socket, True, RFCOMM)
set_security(server_socket, AUTH)
print "listening..."

# Note: Don't call .send or .recv on the server_socket!
# Use the sock object returned by server_socket.accept().

(sock,peer_addr) = server_socket.accept()
print "Connection from %s"%peer_addr
msg = appuifw.query(u"Type a message", "text", u"")
sock.send(msg +'\n')
print "message sent."


# Allow time for data to be sent to work around a bug in the socket
# module.
e32.ao_sleep(1)
sock.close()
