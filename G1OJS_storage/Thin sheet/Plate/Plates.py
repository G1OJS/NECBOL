#import sys
#sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "Plates",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)
model.set_ground(eps_r = 1, sigma = 0.00, origin_height_m = 0.0)
model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)

comps = components ()

dipole = comps.wire_Z(length_m = 2, wire_diameter_mm = 1)
model.place_feed(dipole, feed_alpha_object = 0.5)
dipole.translate (dx_mm = -2000, dy_mm = 0, dz_mm = 0)

cond_sheet = comps.thin_sheet(model,  1, length_mm = 2000,
                                height_mm = 2000, conducting_wire_diameter_mm = 3,
                                conductivity = 10*1/377,
                                grid_pitch_mm = 200 )


model.add(cond_sheet, wireframe_color = 'silver')

model.add(dipole)



model.write_nec()
show_wires_from_file(model, view_el = 10, view_az = 75)
model.run_nec()
plot_pattern_gains(model)



