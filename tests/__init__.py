import sys
import os

directory_name = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, "{}/spytrack".format(directory_name))
