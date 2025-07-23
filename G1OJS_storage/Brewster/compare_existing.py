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
data_dipole_sheet_1 = _read_radiation_pattern(path + "Ver_dip D_Sheet 5x5m x=10m Er = 2 t=10mm Z= -5m.out")
data_dipole_sheet_2 = _read_radiation_pattern(path + "Ver_dip D_Sheet 5x5m x=10m Er = 3 t=10mm Z= -5m.out")


#_plot_gains(data_dipole, azimuth_deg = 0)
#_plot_gains(data_dipole_sheet_1, azimuth_deg = 0)
#_plot_gains(data_dipole_sheet_2, azimuth_deg = 0)



diff = _subtract_patterns(data_dipole, data_dipole_sheet_1)
_plot_gains(diff, azimuth_deg = 0)

diff = _subtract_patterns(data_dipole, data_dipole_sheet_2)
_plot_gains(diff, azimuth_deg = 0)




