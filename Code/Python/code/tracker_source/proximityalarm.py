from appuifw import note
from e32 import ao_sleep as sleep
try:
    from misty import vibrate
except:
    def vibrate(time,volume):
        pass

note(u"Waypoint reached!", "info")
for i in range(0,5):
    vibrate(500,100)
    sleep(0.5)

print "ProximityAlarm!"
