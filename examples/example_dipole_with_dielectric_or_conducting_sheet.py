
from necbol import *

model = NECModel(working_dir="nec_wkg",
                 model_name = "Vertical Dipole in free space",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

#model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0) 

antenna_components = components ()

dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
dipole.translate(dx_m = -1, dy_m=0, dz_m = 0)
model.add(dipole)           

model.write_nec() 
show_wires_from_file(model)
model.run_nec()
plot_total_gain(model)

nearby_sheet = antenna_components.thin_sheet(model, 1.0, length_mm = 1000, height_mm = 500, thickness_mm = 5, grid_pitch_mm = 50 )
model.set_name(f"Vertical Dipole with nearby conducting sheet")
model.add(nearby_sheet)
model.write_nec()
show_wires_from_file(model)
model.run_nec()
plot_total_gain(model)



print(f"\n\nEnd of example")

