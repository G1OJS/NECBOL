import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol.modeller import *
from necbol.components import *
from necbol.gui import *

from necbol.modeller import _read_radiation_pattern
from necbol.gui import _subtract_patterns
from necbol.gui import _plot_gains

model = NECModel(working_dir="nec_wkg",
                 model_name = "Ver_dip",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)
model.set_gain_sphere_1deg()
model.set_ground(eps_r = 1, sigma = 0.01, origin_height_m = 0.0) 

antenna_components = components ()

model.start_geometry()
dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)
dipole.rotate_around_X(45)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
model.add(dipole)
model.write_nec()
model.run_nec()
data_dipole = model.read_radiation_pattern()

model.set_name("Ver_dip D_Sheet 5x5m x=10m Er = 4 t=10mm Z= -5m")
#mesh = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = 1000, height_mm = 1000, thickness_mm = 5, grid_pitch_mm = 50 )
mesh = antenna_components.thin_sheet(model, 0, 4, length_mm = 5000, height_mm = 5000, thickness_mm = 5, grid_pitch_mm = 100 )
mesh.rotate_around_Y(90)
mesh.translate(dx_m= 10, dy_mm = 0, dz_m = -5)
model.add(mesh)
model.write_nec()
model.run_nec()
#show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)
data_dipole_sheet = model.read_radiation_pattern()

diff = _subtract_patterns(data_dipole, data_dipole_sheet)
_plot_gains(diff, azimuth_deg = 0)

