# This script uses the multi_query function of the appuifw module

# import the application user interface framework module
import appuifw

# create 2 text input fields at the same time:  appuifw.multi_query(label1, label2)
input1,input2 = appuifw.multi_query(u"Type your first name:",u"Type your last name:")

# print the results on the screen
print input1
print input2