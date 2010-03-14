
import appuifw
"""
# asking data from a user is quite simple
# Nokia already has libraries built... there's no need to
# rewrite libraries

# the appuifw libraries has all widgets or most of the widgets
# that you could use

What is a widget?
-----------------
A widget is component or design.. for examples include
- dialogs that come up to issue warnings to users
- dialogs that come when a message has been sent, received or deleted
- the stuff that pops as you receive a call

What is appuifw?
appuifw stands for "Application User Interface FrameWork"


In python it is easy to use.. just import appuifw into the namespace
of the program.. and access widgets using a "dot" operator
"""

# when you tell users to type a word or somethign
# you don't want it to get lost, you will want to
# save it somewhere... that's where the variable "data" comes in
data = appuifw.query(u"Type a word:", "text")
# Whatever the user types can be accessed through "data"

appuifw.note(u"The typed word was: " + str(data), "info")

# appuifw.note is the note widget... its a function that will take
# several values or arguments: a unicode string and the widget label
# There are several labels in place: info, conf, error
