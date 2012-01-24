# print statements for debugging

import sys
try: 
    from django.conf import settings
    SHOW_DEBUG_MSG = settings.DEBUG
except:
    SHOW_DEBUG_MSG = True
    
def msg(m): 
    if SHOW_DEBUG_MSG: 
        print m
    
def dashes(): msg('-' * 40)
def msgt(m): dashes(); msg(m); dashes()
def msgx(m): msgt(m); print 'exiting...'; sys.exit(0)