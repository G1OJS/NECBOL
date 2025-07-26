import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "Strip",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)
model.set_ground(eps_r = 1, sigma = 0.00, origin_height_m = 0.0)
model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)

antenna_components = components ()

h = 50
w = 150
le = 5000
ws = 300
dg = 50

dipole = antenna_components.wire_Z(length_mm = h, wire_diameter_mm = 1)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
model.add(dipole)

ground_plane = antenna_components.thin_sheet(model,  1, length_mm = ws, height_mm = le, thickness_mm = 1, grid_pitch_mm = dg )
ground_plane.rotate_around_Y(90)
ground_plane.translate(dx_mm = le/2, dy_mm = 0, dz_mm = -h/2)
model.add(ground_plane)

strip = antenna_components.thin_sheet(model,  1, length_mm = w, height_mm = le, thickness_mm = 1, grid_pitch_mm = dg )
strip.rotate_around_Y(90)
strip.translate(dx_mm = le/2, dy_mm = 0, dz_mm = h/2)
model.add(strip)

load = antenna_components.wire_Z(length_mm = h, wire_diameter_mm = 1)
load.translate(dx_mm = le, dy_mm = 0, dz_mm = 0)
model.place_RLC_load(load, 50, 0, 0, 'parallel', load_wire_index=0, load_alpha_wire=0.5)
model.add(load)

model.write_nec()
show_wires_from_file(model)

#
#model.run_nec()




