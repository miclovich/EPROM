# This script demonstrates how to use a single-field dialog (text input field)
# and displays the users input as a pop-up note 


import appuifw
input = appuifw.query(u"Type a word:", "text")

appuifw.note(u"The typed word was: " + input, "info")


