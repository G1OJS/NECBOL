import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol.modeller import *
from necbol.components import *
from necbol.gui import *


from necbol.modeller import _read_radiation_pattern
from necbol.gui import _subtract_patterns
from necbol.gui import _plot_gains

path = r"C:\Users\drala\Documents\Projects\GitHub\NECBOL\G1OJS_storage\Brewster\nec_wkg/"
data_dipole = _read_radiation_pattern(path + "Ver_dip.out")
data_dipole_sheet_1 = _read_radiation_pattern(path + "Ver_dip cond Sheet 1x1m x=5m Er = 1 t=10mm Z= -2m.out")
data_dipole_sheet_2 = _read_radiation_pattern(path + "Ver_dip D_Sheet 3x3m x=10m Er = 2 t=10mm Z= -m.out")

diff = _subtract_patterns(data_dipole, data_dipole_sheet_1)
_plot_gains(diff, azimuth_deg = 0)

diff = _subtract_patterns(data_dipole, data_dipole_sheet_2)
_plot_gains(diff, azimuth_deg = 0)




