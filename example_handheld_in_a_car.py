
from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file, plot_gain

# This file is extremely experimental, and more targetted at discovering how easy it is to build a car
# using necbol, than draw any solid conclusions about RF effects. At the moment, I'm exploring how
# to make it easier to join grids together when they don't meet at global grid points, and then
# investigate how important this is for the RF results

car_width_mm = 2000
car_length_mm = 3500
car_height_mm = 1900
car_window_base_mm = 900
car_front_bulkhead_y_mm =(car_length_mm/2) - 800
car_rear_bulkhead_y_mm = (-car_length_mm/2) + 400


model = NECModel(working_dir="nec_wkg",
                 model_name = "Horizontal Dipole with end loading plates",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_az_arc(azimuth_start=0, azimuth_stop=360, nPoints=360, elevation=10)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_mm = 0 )

z_lift = 300 + car_window_base_mm / 2

antenna_components = components ()
model.start_geometry()

dipole = antenna_components.wire_Z(length_mm = 250, wire_diameter_mm = 10)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
dipole.translate(dx_mm = 600, dy_mm = car_front_bulkhead_y_mm - 500, dz_mm = 700 + z_lift)
model.add(dipole)

left_side = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_length_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
left_side.translate(dx_mm = -car_width_mm/2, dy_m=0, dz_mm=z_lift)
model.add(left_side)

right_side = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_length_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
right_side.translate(dx_mm = car_width_mm/2, dy_mm=0, dz_mm=z_lift)
model.add(right_side)

front_bulkhead = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_width_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
front_bulkhead.rotate_around_Z(90)
front_bulkhead.translate(dx_mm = 0, dy_mm=car_front_bulkhead_y_mm, dz_mm=z_lift)
model.add(front_bulkhead)

rear_bulkhead = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_width_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
rear_bulkhead.rotate_around_Z(90)
rear_bulkhead.translate(dx_mm = 0, dy_mm=car_rear_bulkhead_y_mm, dz_mm=z_lift)
model.add(rear_bulkhead)

floor = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_length_mm, height_mm = car_width_mm, thickness_mm = 1, grid_pitch_mm = 200 )
floor.rotate_around_Y(90)
floor.translate(dx_mm = 0, dy_mm=0, dz_mm=(-car_window_base_mm/2)+z_lift)
model.add(floor)

roof = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = car_length_mm -1400, height_mm = car_width_mm, thickness_mm = 1, grid_pitch_mm = 200 )
roof.rotate_around_Y(90)
roof.translate(dx_mm = 0, dy_mm=-400, dz_mm=(-car_window_base_mm/2) -300 + car_height_mm+z_lift)
model.add(roof)


model.write_nec() 
show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)
model.run_nec()
data_dipole = model.read_radiation_pattern()
plot_gain(data_dipole, 10, 'gain_horz_db')

vswr = model.vswr()
print(f"vswr:{vswr:.2f}")

print(f"\n\nEnd of example {model.model_name}")

