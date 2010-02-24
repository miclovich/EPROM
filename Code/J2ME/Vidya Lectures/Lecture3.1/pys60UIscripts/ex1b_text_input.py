
import appuifw


input1 = appuifw.query(u"Type your first name:", "text")

appuifw.note(u"Your first name is: " + input1, "info")

input2 = appuifw.query(u"Type your last name:", "text")

appuifw.note(u"Your last name is: " + input2, "info")

appuifw.note(u"Your full name is: " + input1 +u" " + input2, "info")

