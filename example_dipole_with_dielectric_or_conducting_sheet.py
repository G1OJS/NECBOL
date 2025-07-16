
from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file, plot_gain

model = NECModel(working_dir="nec_wkg",
                 model_name = "A: Vertical Dipole in free space",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

#model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_az_arc(azimuth_start=0, azimuth_stop=360, nPoints=360, elevation=3)
model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0) 

antenna_components = components ()
model.start_geometry()

dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
dipole.translate(dx_m = -1, dy_m=0, dz_m = 1)
model.add(dipole)           

model.write_nec() 
show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)
model.run_nec()
data_dipole = model.read_radiation_pattern()
plot_gain(data_dipole, 3, 'gain_vert_db')

nearby_sheet = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = 1000, height_mm = 500, thickness_mm = 5, grid_pitch_mm = 50 )
#nearby_sheet = antenna_components.thin_sheet(model, 0, 2.0, length_mm = 1000, height_mm = 500, thickness_mm = 5, grid_pitch_mm = 100 )
model.set_name(f"B: Vertical Dipole with nearby conducting sheet")
model.add(nearby_sheet)
model.write_nec()
show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)
model.run_nec()
data_dipole_sheet = model.read_radiation_pattern()
plot_gain(data_dipole_sheet, elevation_deg = 3, component = 'gain_vert_db', polar = True)

print(f"\n\nEnd of example {model.model_name}")

