import appuifw
import e32

def exit_key_handler():
    app_lock.signal()

msg = appuifw.Text()
msg.set(u'testing screen sizes...')

L = [u'full', u'normal', u'large']

testscreen = appuifw.popup_menu(L, u"Select Screen Size + press OK:")

if testscreen == 0 :
	appuifw.app.screen='full' #(a full screen)
if testscreen == 1 :
	appuifw.app.screen='normal' #(a normal screen with title pane and softkeys)
if testscreen == 2 :
	appuifw.app.screen='large' #(only softkeys visible)






app_lock = e32.Ao_lock()

appuifw.app.body = msg

appuifw.app.exit_key_handler = exit_key_handler
app_lock.wait()