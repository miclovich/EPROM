
import urllib, json, appuifw, time

URL = "http://developer.yahooapis.com/TimeService/V1/" +\
      "getTime?appid=MobilePython&output=json"

output = json.read(urllib.urlopen(URL).read())
print "Yahoo response: ", output
tstamp = int(output["Result"]["Timestamp"])

appuifw.note(u"Yahoo says that time is %s" %
             time.ctime(tstamp))
