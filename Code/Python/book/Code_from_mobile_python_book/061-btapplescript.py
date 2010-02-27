
import serial, os

ALLOWED_SCRIPTS = ["edit"]

ser = serial.Serial('/dev/tty.pybook') 

print "Waiting for message..."
while True:
        msg = serial.readline().strip()
        if msg == "exit":
                print >> serial, "bye!"
                break
        elif msg in ALLOWED_SCRIPTS:
                print "Running script: " + msg
                os.system("osascript %s.script" % msg)
                print >> serial, "Script ok!"
