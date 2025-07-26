import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "Helix",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)
model.set_ground(eps_r = 1, sigma = 0.00, origin_height_m = 0.0)
model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)

antenna_components = components ()


helix = antenna_components.helix(length_mm = 200, diameter_mm = 150, pitch_mm = 75, wires_per_turn = 16, sense = 'RH', wire_diameter_mm = 1, taper_factor = 0.8)
model.place_feed(helix, feed_wire_index=0, feed_alpha_wire=0.5)

ground_plane = antenna_components.thin_sheet(model,  1, length_mm = 400, height_mm = 400, thickness_mm = 1, grid_pitch_mm = 50 )
ground_plane.rotate_around_Y(90)
ground_plane.translate(dx_mm = 0, dy_mm = 0, dz_mm = 0)


helix.connect_ends(ground_plane)
model.add(helix)
model.add(ground_plane)


model.write_nec()
show_wires_from_file(model)

#
#model.run_nec()




