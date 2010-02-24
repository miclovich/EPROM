import appuifw
import e32

def exit_key_handler():
    app_lock.signal()

# create an instance of appuifw.Text()
msg = appuifw.Text()
# change the style of the text
msg.style = appuifw.STYLE_UNDERLINE
# set the text to 'hello world'
msg.set(u'hello world')

# put the screen size to full screen
appuifw.app.screen='full' 

# create an Active Object
app_lock = e32.Ao_lock()

# set the application body to the text
appuifw.app.body = msg

appuifw.app.exit_key_handler = exit_key_handler
app_lock.wait()