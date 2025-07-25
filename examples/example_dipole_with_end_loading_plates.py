
from necbol import *

model = NECModel(working_dir="nec_wkg",
                 model_name = "Horizontal Dipole with end loading plates",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 14)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

antenna_components = components ()

dplen_m =4.5

dipole = antenna_components.wire_Z(length_m = dplen_m, wire_diameter_mm = 10)
dipole.rotate_ZtoX()
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
model.add(dipole)

loading_plate_left = antenna_components.thin_sheet(model, 1.0, length_mm = 1000, height_mm = 1000, thickness_mm = 1, grid_pitch_mm = 200 )
loading_plate_left.translate(dx_m = -dplen_m/2, dy_m=0, dz_m=0)
model.add(loading_plate_left)

loading_plate_right = antenna_components.thin_sheet(model, 1.0, length_mm = 1000, height_mm = 1000, thickness_mm = 1, grid_pitch_mm = 200 )
loading_plate_right.translate(dx_m = dplen_m/2, dy_m=0, dz_m=0)
model.add(loading_plate_right)

model.write_nec() 
model.run_nec()

show_wires_from_file(model)
plot_total_gain(model)

vswr = vswr(model)
print(f"vswr:{vswr:.2f}")

print(f"\n\nEnd of example {model.model_name}")

