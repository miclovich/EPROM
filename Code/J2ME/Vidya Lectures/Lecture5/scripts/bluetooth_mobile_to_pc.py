import appuifw
import socket
import e32


def connect_to_PC():
    global sock
    sock=socket.socket(socket.AF_BT,socket.SOCK_STREAM)
    target=''
    if not target:
        address,services=socket.bt_discover()
        print "Discovered: %s, %s"%(address,services)
        if len(services)>1:
          #  import appuifw
            bt_choices=services.keys()
            bt_choices.sort()
            bt_choice=appuifw.popup_menu([unicode(services[x])+": "+x
                                        for x in bt_choices],u'Choose port:')
            pc_target=(address,services[bt_choices[bt_choice]])
        else:
            pc_target=(address,services.values()[0])
    print "Connecting to "+str(pc_target)
    sock.connect(pc_target)
    print "Connected."

    bt_msgtransfer()
        

def bt_msgtransfer():
    global sock
    msg = appuifw.query(u"Type text:", "text", u"")
    if msg == None:
        exit_key_handler()
    else:
        sock.send(msg + " ")
        bt_msgtransfer()

def exit_key_handler():
    script_lock.signal()
    appuifw.app.set_exit()

appuifw.app.title = u"Mobile to PC BT"

script_lock = e32.Ao_lock()

appuifw.app.exit_key_handler = exit_key_handler()

connect_to_PC()

script_lock.wait()


