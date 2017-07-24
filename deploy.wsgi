
import sys
import os
# sys.path.insert(0, '/var/www/tf')
# this should work...
sys.path.insert(0, os.getcwd())

from myapp import app as application
