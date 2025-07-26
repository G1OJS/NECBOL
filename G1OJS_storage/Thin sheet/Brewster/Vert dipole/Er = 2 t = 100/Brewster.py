import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "Ver_dip",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)
model.set_ground(eps_r = 1, sigma = 0.00, origin_height_m = 0.0)
model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)

antenna_components = components ()

dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)
#dipole.rotate_around_X(45)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
model.add(dipole)
model.write_nec()
model.run_nec()

model_dip = copy.deepcopy(model)

model.set_name("Ver_dip_sheet")
mesh = antenna_components.thin_sheet(model,  2, length_mm = 5000, height_mm = 5000, thickness_mm = 100, grid_pitch_mm = 100 )
mesh.rotate_around_Y(90)
#mesh.rotate_around_X(30)
mesh.translate(dx_m= 10, dy_mm = 0, dz_m = -1.5)
model.add(mesh)
model.write_nec()
model.run_nec()
#show_wires_from_file(model)


_plot_difference_field(model_dip, model, azimuth_deg = 0)
