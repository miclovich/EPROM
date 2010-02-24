import appuifw
import e32 
import audio
filename = 'c:\\example.wav' 

def recording(): 
	global S 
	S=audio.Sound.open(filename)
	S.record()
	print "Recording sound."

def playing():
	global S 
	try:
		S=audio.Sound.open(filename) 
		S.play()
		print "Playing sound." 
	except:
		print "File not found. First record."


def closing():
	 global S 
	 S.stop()
	 S.close() 
         print "Stopped sound." 

def exit_key_handler():
	 script_lock.signal() 
	 appuifw.app.set_exit()

script_lock = e32.Ao_lock() 
appuifw.app.title = u"Sound application"
appuifw.app.menu = [(u"play", playing), (u"record", recording), (u"stop", closing)]
appuifw.app.exit_key_handler = exit_key_handler
script_lock.wait() 

