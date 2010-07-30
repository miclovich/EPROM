import traceback
import sys

exceptions = []
exit_lock = None

def set_lock(lock):
    global exit_lock
    exit_lock = lock

def store_exception():
    exceptions.append(sys.exc_info())

def safe_call(function):
    global exceptions

    def call_function(*args, **kwds):
        try:
            return function(*args, **kwds)
        except:
            store_exception()

    return call_function

def dump_exceptions(file):
    global exceptions
    print "Exception list (%i):" % len (exceptions)
    #print exceptions
    for exception in exceptions:
        #print exception
        for l in traceback.format_exception(*exception):
            print l.strip()

    f = open(file,"w")
    f.write("\n\nTracker exception list (%i):\n" % len (exceptions))
    for exception in exceptions:
        for l in traceback.format_exception(*exception):
            f.write(l)
    f.close()

    exceptions = []
