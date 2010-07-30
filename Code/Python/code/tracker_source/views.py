from osal import *
from dataprovider import *


class View:
    def __init__(self):
        pass

    def UpdateSignal(self,signal):
        pass

    def UpdateTime(self,time):
        pass

    def UpdatePosition(self,point):
        pass

    def UpdateCourse(self,course):
        pass

    def GetPosition(self):
        pass


class DashView(View):
    instance = None

    def __init__(self):
        View.__init__(self)
        DashView.instance = self

    def GetInstance():
        return DashView.instance

    def Show(self):
        pass

    def Hide(self):
        pass

    GetInstance = staticmethod(GetInstance)


class MapView(View):
    instance = None

    def __init__(self):
        View.__init__(self)
        MapView.instance = self

    def GetInstance():
        return DashView.instance

    def Show(self):
        pass

    def Hide(self):
        pass

    GetInstance = staticmethod(GetInstance)


class Application:
    instance = None

    def __init__(self):
        Application.instance = self

    def GetInstance():
        return Application.instance

    def Init(self):
        pass

    def Run(self):
        pass

    def Exit(self):
        pass

    GetInstance = staticmethod(GetInstance)
