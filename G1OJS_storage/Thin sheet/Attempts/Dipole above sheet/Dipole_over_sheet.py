import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "Dipole over sheet",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz =  300)

model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)
model.set_gain_point(azimuth_deg = 0, elevation_deg = 10)

comps = components ()

dipole = comps.wire_Z(length_m = 0.01, wire_diameter_mm = 1)
model.place_feed(dipole, feed_alpha_object = 0.5)
dipole.translate(dx_m=0, dy_m= 0, dz_m = 0.25)
model.add(dipole)



diel_sheet=comps.thin_sheet(model,  epsillon_r = 20, length_m = 1,
                                    height_m = 1,
                                    dielectric_thickness_m = 0.001,
                                    grid_pitch_m = 0.025 )
diel_sheet.rotate_ZtoX()
model.add(diel_sheet, wireframe_color = 'yellow')


model.write_nec()
show_wires_from_file(model, view_el = 10, view_az = 75)
#model.run_nec()
#plot_pattern_gains(model, azimuth_deg = 0)



