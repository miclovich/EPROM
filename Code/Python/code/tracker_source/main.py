#!/usr/bin/env python
from trace import safe_call as XWrap
from trace import dump_exceptions as XSave

def Main():
    # Tracker uses several libraries,
    # Osal is the Operating system abstraction layer
    # Storage handles all input/output of stored data
    # Gps provides input data for the application
    # And Application handles all UI interaction as
    # well as the main program loop
    from osal import S60Osal as Osal
    from datastorage import S60DataStorage as Storage
    from dataprovider import S60DataProvider as Gps
    from s60views import S60Application as Application

    # Instantiate singletons
    Osal()
    Storage()
    Gps()
    Application()

    # Run the application
    app = Application.GetInstance()
    app.Init()
    app.Run()
    app.Exit()


if __name__ == '__main__':
    XWrap(Main)()
    XSave("c:\\data\\tracker.log")
