import appuifw, e32, camera
 



img = None
 
def __exit__( ):
  stop( )

  # stops scheduler
  script_lock.signal( )
 
def start( ):
    camera.start_finder( vfCallback )
    appuifw.app.menu = [(u'Capture', capture), (u'Stop', stop), (u'Exit', __exit__)]
 
def stop( ):
    camera.stop_finder( )
    cnvCallback( )
    appuifw.app.menu = [(u'Start', start), (u'Save', capture), (u'Exit', __exit__)]
 
def vfCallback( aIm ):
    global img
    appuifw.app.body.blit( aIm )
    img = aIm
 
def cnvCallback( aRect=None ):
    if img != None:
        appuifw.app.body.clear( )
        appuifw.app.body.blit(img)
 
def capture( ):
    camera.stop_finder( )
    cnvCallback( )
    appuifw.app.menu = [(u'Start', start), (u'Exit', __exit__)]
    img.save(u'E:\\Images\\viewfinder.png')
    appuifw.note(u'Saved', 'info')
 
# Main script starts here...


# start AO scheduler
script_lock = e32.Ao_lock( )
 
appuifw.app.exit_key_handler = __exit__

appuifw.app.title= u'Camera ViewFinder App'

appuifw.app.body = appuifw.Canvas( redraw_callback = cnvCallback)

start( )
 
script_lock.wait( )