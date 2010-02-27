
import time, json

def init_server():
    global title, choices, already_voted, started
    started = time.time()
    already_voted = {}
    title = u"What shall we eat?"
    choices = {u"Tacos": 0,\
               u"Pizza": 0,\
               u"Sushi": 0}
    print "Voting starts"

def vote_status():
    voting_closed = time.time() - started > 60
    results = []
    for choice, count in choices.items():
        results.append((count, choice))
    return voting_closed, max(results)

def process_json(query):
    voting_closed, winner = vote_status()
    if voting_closed:
        return {"closed": True, "winner": winner}

    msg = ""
    if "choice" in query:
        if query["voter"] in already_voted:
                msg = "You have voted already"
        else:
                choices[query["choice"]] += 1
                already_voted[query["voter"]] = True
                msg = "Thank you for your vote!"
        
    return {"title": title, "winner": winner,\
            "choices": choices, "msg": msg}

def process_get(path, query):
   voting_closed, winner = vote_status()
   msg = "<html><body><h1>Vote: %s</h1><br/>" % title
   for choice, count in choices.items():
       msg += "<b>%s</b> %d<br/>" % (choice, count)

   if voting_closed:
       msg += "<p><h2>Voting closed.</h2></p>"
       msg += "<h1>The winner is: %s</h1>" % winner[1]
   else:
       msg += "<h2>%d seconds until closing</h2>" %\
                    (60 - (time.time() - started))
   
   return "text/html", "%s</body></html>" % msg   

init_server()
httpd = Server(('', 9000), Handler)
httpd.serve_forever()
