
import appuifw, e32, urllib, socket, e32dbm, json, os.path, os

APP_KEY = "5IsN4V9AdLwI3Dde"
SEARCH_URL = "http://api.evdb.com/json/events/search?"

CONF_FILE = u"E:\\Data\\Eventfu\\eventfu.cfg"
DESCRIPTION_FILE = u"E:\\Data\\Eventfu\\eventfu.html"
UPDATE_INTERVAL = 600

if not os.path.exists("E:\\Data\\Eventfu"):
        os.makedirs("E:\\Data\\Eventfu")

WHEN = [u"All", u"Future", u"Past", u"Today",
        u"Last Week", u"This Week", u"Next week"]
ORDER = [u'relevance', u'date', u'title',
         u'venue_name', u'distance']
EVENT_FIELDS = [u'title', u'start_time', u'venue_name',
                u'venue_address']

def show_prefs():
        if appuifw.app.title.find("Updating") != -1:
                return
        form = appuifw.Form([
            (u"Location", "text", prefs.get("Location", u"")),
            (u"Keywords", "text", prefs.get("Keywords", u"")),
            (u"When", "combo", (WHEN, 3)),
            (u"Sort_order", "combo", (ORDER, 0))],
            appuifw.FFormEditModeOnly)
        form.menu = []
        form.save_hook = save_prefs
        form.execute()


def save_prefs(new_prefs):
        db = e32dbm.open(CONF_FILE, "nf")
        for label, type, value in new_prefs:
                if label == "When" or label == "Sort_order":
                        value = value[0][value[1]]
                prefs[label] = value
                db[label] = value.encode("utf-8")
        db.close()
        timer.cancel()
        timer.after(0, update_list)
        return True

def load_prefs():
        global prefs
        try:
                prefs = {}
                db = e32dbm.open(CONF_FILE, "r")
                for k, v in db.iteritems():
                        prefs[k] = v.decode("utf-8")
                db.close()
        except Exception, x:
                prefs = {}
        return prefs


def update_list():
        global alive, events
        lprefs = {'app_key': APP_KEY, 'page_size': '10'}
        for k, v in prefs.items():
                if v:
                        lprefs[k.lower()] = v

        listbox.set_list([u"Updating..."])
        appuifw.app.title = u"Updating %s..." %\
                            prefs.get('Location', u"")
        try:
                url = SEARCH_URL + urllib.urlencode(lprefs)
                res = urllib.urlopen(url).read()
                events = json.read(res)['events']['event']
                titles = []
                for event in events:
                        titles.append(unicode(event['title']))
                listbox.set_list(titles)
                appuifw.app.title = prefs['Location']
        except:
                listbox.set_list([u"Could not fetch events"])
                appuifw.app.title = u"EventFu"
        if alive:
                timer.after(UPDATE_INTERVAL, update_list)


def show_description():
        global desc 
        f = file(DESCRIPTION_FILE, "w")
        f.write(u"<html><body>%s</body></html>" % desc)
        f.close()
        lock = e32.Ao_lock()
        viewer = appuifw.Content_handler(lock.signal)
        viewer.open(DESCRIPTION_FILE)
        lock.wait()

def show_event():
        global desc
        if not events:
                return
       
        event = events[listbox.current()]
        form_elements = []
        for field in EVENT_FIELDS:
                if field in event and event[field]:
                     key = field.capitalize()
                     value = event[field].decode("utf-8")
                     form_elements.append((key, "text", value))

        form = appuifw.Form(form_elements,
                appuifw.FFormViewModeOnly)

        if 'description' in event:
                desc = event['description'].decode("utf-8")
                form.menu = [(u"description", show_description)]

        form.execute()


def access_point():
        ap_id = socket.select_access_point()
        apo = socket.access_point(ap_id)
        socket.set_default_access_point(apo)
                
def quit():
        global alive
        alive = False
        timer.cancel()
        app_lock.signal()

events = None
alive = True
timer = e32.Ao_timer()
appuifw.app.exit_key_handler = quit
appuifw.app.title = u"EventFu"
appuifw.app.menu = [(u"Preferences", show_prefs),
                    (u"Access point", access_point),
                    (u"Quit", quit)]

appuifw.app.body = listbox = appuifw.Listbox([u""], show_event)

load_prefs()
update_list()
app_lock = e32.Ao_lock()
app_lock.wait()
