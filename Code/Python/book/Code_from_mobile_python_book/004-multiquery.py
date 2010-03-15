# We look at asking users for input
# the queries we make here are more than one... "multi" means many!

import appuifw # bring the UI framework into the namespace

names = appuifw.multi_query(u"First name:", u" Last name:") # The multi query function
"""
multi_query() gets values that form a tuple
names becomes (<firstname>, <lastname>)
i.e.
Whatever the user types first takes the 0th position of the "names" tuple
the next input goes to the 1st position
"""

"""
More exciting stuff happens when we add some "conditions" to our input
In this case... we first test whether the "names" tuple is not empty i.e. if True:
We reassign values.... to first and last variables

Python supports some great stuff... this is called "unpacking a tuple"
Suppose I have a coordinate

point A,
A = (3,7)

Assume that we want to split the coordinate/position A
we can do this
x = A[0]
y = A[1]

or we could do all that in one line
x,y = A
which translates to
x, y = (3,7)
"""
if names: 
        first, last = names
        """
        The next part of the program will utilize Python's text processing abilities:
        ====> String concatenation
        >>> y = u"Y"
        >>> x = u"X can be added to: " + y
        >>> x
        'X can be added to: Y'
        >>>
        
        There are some cautions you can take... sanitize your variables...
        when concatenating there are certain rules to follow...
        str() + str() = str()
        str() just means string! :)
        so... when adding data, we have to make sure that they are similar
        Strings can be added to strings
        """
        appuifw.note(u"Your full name is: " + first + " " + last)
# When the first condition is true... the note that tells you about your full name comes up
else:
# Otherwise... a note widget that tells you to cancel shows up!
        appuifw.note(u"Cancel!")
