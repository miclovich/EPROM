import time
import os

class Osal:
    instance = None

    def GetInstance():
        return Osal.instance

    def ShowInfo(self,text):
        pass

    def ShowError(self,text):
        pass

    def Sleep(self,s):
        pass

    def GetTime(self):
        pass

    def GetIsoTime(self,ts):
        pass

    def OpenDbmFile(self,file,mode):
        pass

    def GetDbmExt(self):
        pass

    def ExecuteScript(self,script,globals={},locals={}):
        pass

    GetInstance = staticmethod(GetInstance)



class PosixOsal(Osal):
    def __init__(self):
        global db
        import dbm as db
        Osal.instance = self

    def ShowInfo(self,text):
        print "Info: %s" % text

    def ShowError(self,text):
        print "Error: %s" % text

    def Sleep(self,s):
        time.sleep(s)

    def GetTime(self):
        return time.time()

    def GetIsoTime(self,ts):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))

    def OpenDbmFile(self,file,mode):
        b,e = os.path.splitext(os.path.expanduser(file))
        print "Opening dbm file %s in mode %s " % (b,mode)
        return db.open(b,mode)

    def GetDbmExt(self):
        return ".db"



class NTOsal(Osal):
    def __init__(self):
        global db
        import dbhash as db
        Osal.instance = self

    def ShowInfo(self,text):
        print "Info: %s" % text

    def ShowError(self,text):
        print "Error: %s" % text

    def Sleep(self,s):
        time.sleep(s)

    def GetTime(self):
        return time.time()

    def OpenDbmFile(self,file,mode):
        print "Opening dbm file %s in mode %s " % (file,mode)
        return db.open(file,mode)

    def GetDbmExt(self):
        return ".db"




class S60Osal(Osal):
    def __init__(self):
        global appuifw
        global e32
        global db
        global sys
        import appuifw
        import e32
        import e32dbm as db
        import sys
        Osal.instance = self

    def ShowInfo(self,text):
        appuifw.note(u"%s" % text, "info")

    def ShowError(self,text):
        appuifw.note(u"%s" % text, "error")

    def Sleep(self,s):
        e32.ao_sleep(s)

    def GetTime(self):
        return time.time()

    def GetIsoTime(self,ts):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))

    def OpenDbmFile(self,file,mode):
        b,e = os.path.splitext(file)
        print "Opening dbm file %s in mode %s " % (b,mode)
        return db.open(b,"%sf" % mode)

    def GetDbmExt(self):
        return ".e32dbm"

    def ExecuteScript(self,script,globals={},locals={}):
        modules = sys.modules.keys()
        try:
            execfile(script, globals, locals)
        finally:
            for m in sys.modules.keys():
                if m not in modules:
                    del sys.modules[m]
