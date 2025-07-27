import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol import *
from necbol.analyser import _plot_difference_field
import copy

model = NECModel(working_dir="nec_wkg",
                 model_name = "DOG",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_frequency(MHz = 144.2)

model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)
model.set_gain_point(azimuth_deg = 0, elevation_deg = 10)

comps = components ()

dipole = comps.wire_Z(length_m = 1.04, wire_diameter_mm = 1)
model.place_feed(dipole, feed_alpha_object = 0.5)
dipole.rotate_ZtoY()
dipole.translate(dx_m=0, dy_m= 0, dz_m = 1)

case = 2

if(case ==1):
    model.set_ground(eps_r = 4, sigma = 1e-12, origin_height_m = 0.0)
elif (case == 2):
    model.set_ground(eps_r = 1.001, sigma = 2000, origin_height_m = 0.0)    
elif (case == 3):
    diel_sheet = comps.thin_sheet(model,  epsillon_r = 4, length_mm = 2000,
                                    height_mm = 2000,
                                    dielectric_thickness_mm = 10,
                                    grid_pitch_mm = 200 )
    diel_sheet.rotate_ZtoX()
    model.add(diel_sheet, wireframe_color = 'yellow')
else:
    cond_sheet = comps.thin_sheet(model,  conductivity = 2000, length_mm = 2000,
                                height_mm = 2000,
                                wire_diameter_mm = 1,
                                grid_pitch_mm = 200 )
    cond_sheet.rotate_ZtoX()
    model.add(cond_sheet, wireframe_color = 'brown')


model.add(dipole)

model.write_nec()
show_wires_from_file(model, view_el = 10, view_az = 75)
model.run_nec()
plot_pattern_gains(model, azimuth_deg = 0)



