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

comps = components ()

helix = comps.helix(length_mm = 67, diameter_mm = 78,
                    pitch_mm = 25, wires_per_turn = 16, sense = 'RH',
                    wire_diameter_mm = 1, taper_factor = 54/78)
helix.rotate_around_Z(45)
helix.translate(dx_mm = 0, dy_mm = 0, dz_mm = 4)

ground_plane = comps.thin_sheet(model,  1, length_mm = 210,
                                height_mm = 140, conducting_wire_diameter_mm = 3,
                                grid_pitch_mm = 10 )
ground_plane.rotate_around_Y(90)
ground_plane.translate(dx_mm = 210/2 -90, dy_mm = 140/2 -80, dz_mm = 0)

top_sheet = comps.thin_sheet(model,  4.2, length_mm = 80, height_mm = 80,
                             dielectric_thickness_mm = 7, grid_pitch_mm = 5 )
top_sheet.rotate_around_Y(90)
top_sheet.translate(dx_mm = 0 , dy_mm = 0, dz_mm = 94)

feedwire = comps.connector(helix, 0,0, ground_plane, 15, 8/14)
model.place_feed(feedwire, feed_wire_index=0, feed_alpha_wire=0.5)

model.add(ground_plane, wireframe_color = 'silver')
model.add(feedwire)
model.add(helix)
model.add(top_sheet)


model.write_nec()
show_wires_from_file(model, view_el = 10, view_az = 75)
model.run_nec()




