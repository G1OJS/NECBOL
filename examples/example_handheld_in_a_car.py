
from necbol import *
"""
 This file has been written to demonstrate how easy it is to build a model of a car (at
 the moment, just the passenger cell) using necbol. But note that no claims are made for
 the suitability of this geometry for generating accurate results from NEC.

 Provided that the sheet models join at their *edges*, and appropriate use is made of the
 close_* options so that end wires from two joining grids don't overlap,
 as in the code below, this produces a nec.inp file that runs in nec with no errors, allowing
 far field distortion and currents on the car's surfaces to be seen.

 The code below models a passenger cell with the specified dimensions, with a 25cm long antenna
 in the front right seat, operating at 144.2 MHz.
 
"""

car_width_mm = 2000
pcell_length_mm = 1600
car_height_mm = 1900
car_window_base_mm = 800
roof_length_mm = 1400
roof_start_mm = 0
floor_height_mm = 250

model = NECModel(working_dir="nec_wkg",
                 model_name = "Car",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_az_arc(azimuth_start=0, azimuth_stop=360, nPoints=360, elevation=10)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_mm = 0 )



antenna_components = components ()
model.start_geometry()

dipole = antenna_components.wire_Z(length_mm = 250, wire_diameter_mm = 10)
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)
dipole.translate(dx_mm = car_width_mm*0.25, dy_mm = pcell_length_mm*0.8, dz_mm = 700 + floor_height_mm)
model.add(dipole)

left_side = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = pcell_length_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
left_side.translate(dx_mm = -car_width_mm/2, dy_mm = pcell_length_mm/2, dz_mm= car_window_base_mm/2 + floor_height_mm)


right_side = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = pcell_length_mm, height_mm = car_window_base_mm, thickness_mm = 1, grid_pitch_mm = 200 )
right_side.translate(dx_mm = car_width_mm/2, dy_mm = pcell_length_mm/2, dz_mm=car_window_base_mm/2 + floor_height_mm)


front_bulkhead = antenna_components.thin_sheet(model, 58000000, 1.0,
                                               length_mm = car_width_mm, height_mm = car_window_base_mm,
                                               thickness_mm = 1, grid_pitch_mm = 200,
                                               close_start = False, close_end = False)
front_bulkhead.rotate_around_Z(90)
front_bulkhead.translate(dx_mm = 0, dy_mm= pcell_length_mm, dz_mm=car_window_base_mm/2 + floor_height_mm)
front_bulkhead.connect_ends(left_side)
front_bulkhead.connect_ends(right_side)


rear_bulkhead = antenna_components.thin_sheet(model, 58000000, 1.0,
                                               length_mm = car_width_mm, height_mm = car_window_base_mm,
                                               thickness_mm = 1, grid_pitch_mm = 200,
                                               close_start = False, close_end = False)
rear_bulkhead.rotate_around_Z(90)
rear_bulkhead.translate(dx_mm = 0, dy_mm=0, dz_mm=car_window_base_mm/2 + floor_height_mm)
rear_bulkhead.connect_ends(left_side)
rear_bulkhead.connect_ends(right_side)

floor = antenna_components.thin_sheet(model, 58000000, 1.0,
                                      length_mm = pcell_length_mm, height_mm = car_width_mm, thickness_mm = 1, grid_pitch_mm = 200,
                                      close_start=False, close_end=False, close_top=False, close_bottom=False)
floor.rotate_around_Y(90)
floor.translate(dx_mm = 0, dy_mm = pcell_length_mm/2, dz_mm=floor_height_mm)
floor.connect_ends(front_bulkhead)
floor.connect_ends(rear_bulkhead)
floor.connect_ends(left_side)
floor.connect_ends(right_side)

roof = antenna_components.thin_sheet(model, 58000000, 1.0, length_mm = roof_length_mm, height_mm = car_width_mm, thickness_mm = 1, grid_pitch_mm = 200 )
roof.rotate_around_Y(90)
roof.translate(dx_mm = 0, dy_mm=pcell_length_mm/2+roof_start_mm, dz_mm=(-car_window_base_mm/2) + car_height_mm+floor_height_mm)

model.add(left_side)
model.add(right_side)
model.add(front_bulkhead)
model.add(rear_bulkhead)
model.add(floor)
model.add(roof)

model.write_nec() 
show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)
model.run_nec()
data_dipole = model.read_radiation_pattern()
plot_gain(data_dipole, 10, 'gain_horz_db')

vswr = model.vswr()
print(f"vswr:{vswr:.2f}")

print(f"\n\nEnd of example {model.model_name}")

