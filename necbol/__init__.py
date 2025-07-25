from necbol.components import *
from necbol.visualiser import *
from necbol.analyser import *
from necbol.modeller import *
from necbol.optimisers import *

from importlib.metadata import version
try:
    __version__ = version("necbol")
except:
    __version__ = ""
print(f"\nNECBOL V{__version__} by Dr Alan Robinson G1OJS\n\n")


