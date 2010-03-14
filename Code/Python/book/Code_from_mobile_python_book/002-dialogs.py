# Welcome to the "Learning in Code" series
"""
In this script we look at querries... 
When designing applications, you will expect to 
want some interaction... This interaction could
involve the user to type a passcode or to download
a file...

Below, you will see several widgets. If you upload this
script to your phone and run it, they will consecutive run
until the last statement (in Python) is complete... don't get
scared, its just the Python executing every statement
"""

import appuifw

"""
The syntax is the same... every function here takes two arguments
unless you want to extend the methods by overloading them.
The two arguments are always
- a unicode string that informs the user of the next action
- label: defines the usual look or text rendering method
"""
appuifw.query(u"Type a word:", "text") # a label of text will accept both numerals and alphabet letters

appuifw.query(u"Type a number:", "number") # a number label forces the widget to render just numbers/figures

appuifw.query(u"Type a time:", "time") # a time widget will show soemthing like 00:00 and a dropdown list of possible times to be set

appuifw.query(u"Type a password:", "code") # the code label... everything the user types will be masked... or hidden: maybe as circles or *

appuifw.query(u"Do you like PyS60", "query")#
