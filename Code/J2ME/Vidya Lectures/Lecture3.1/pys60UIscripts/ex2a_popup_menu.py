# simple pop-up menu


import appuifw

L = [u"video", u"image", u"text"]

test = appuifw.popup_menu(L, u"Select + press OK:")

if test == 0 :
    appuifw.note(u"video, Utube", "info")
if test == 1 :
    appuifw.note(u"image, Flickr", "info")
if test == 2 :
    appuifw.note(u"text, Google", "info")




