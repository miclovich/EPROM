
import appuifw
import e32
import urllib

print "press options"

def download():
    url = "http://research.nokia.com/people/vidya_setlur/classes/MobileMultimedia/waterski.3gp"
    tempfile = "c:\\waterski.3gp"
    try:
        print "Retrieving information..."
        urllib.urlretrieve(url, tempfile)
        lock=e32.Ao_lock()
        content_handler = appuifw.Content_handler(lock.signal)
        content_handler.open(tempfile)
        # Wait for the user to exit the image viewer.
        lock.wait()
        print "Finished media playing."
        print "press options or exit."
    except IOError:
        print "Could not download the media."
    except:
        print "Could not open data received."


def main_menu_setup():
    appuifw.app.menu = [(u"Download media", download)]

def exit_key_handler():
    global script_lock
    script_lock.signal()
    appuifw.app.set_exit()
    
script_lock = e32.Ao_lock()

appuifw.app.title = u"Download media"
main_menu_setup()
appuifw.app.exit_key_handler = exit_key_handler
script_lock.wait()


 

