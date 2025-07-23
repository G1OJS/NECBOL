import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol.modeller import NECModel, read_radiation_pattern
from necbol.components import components 
from necbol.gui import show_wires_from_file, plot_gains, subtract_patterns

path = r"C:\Users\drala\Documents\Projects\GitHub\NECBOL\G1OJS_storage\Brewster\nec_wkg/"
data_dipole = read_radiation_pattern(path + "Ver_dip.out")
data_dipole_sheet_1 = read_radiation_pattern(path + "Ver_dip cond Sheet 1x1m x=5m Er = 1 t=10mm Z= -2m.out")
data_dipole_sheet_2 = read_radiation_pattern(path + "Ver_dip D_Sheet 3x3m x=10m Er = 2 t=10mm Z= -2m.out")

diff = subtract_patterns(data_dipole, data_dipole_sheet_1)
plot_gains(diff, azimuth_deg = 0)

diff = subtract_patterns(data_dipole, data_dipole_sheet_2)
plot_gains(diff, azimuth_deg = 0)




