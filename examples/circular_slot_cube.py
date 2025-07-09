import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_csc(d_mm, h_mm, main_wire_diameter_mm, feed_gap_mm):
    global model

    feed_gap_angle_deg = 360*feed_gap_mm / (math.pi*d_mm)
    print(d_mm, feed_gap_mm, feed_gap_angle_deg)

    model.start_geometry()

    top_loop = antenna_components.circular_arc(diameter_m = d_mm /1000, arc_phi_deg = 360-feed_gap_angle_deg, n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    bottom_loop = antenna_components.circular_arc(diameter_m = d_mm /1000, arc_phi_deg = 360-feed_gap_angle_deg,  n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    top_loop.translate(0,0,h_mm/1000)
    
    slot_wire1 = antenna_components.wire_Z(length_m = h_mm /1000, wire_diameter_mm = main_wire_diameter_mm, Origin_Z = -h_mm/2000)
    slot_wire1.translate(d_mm/2000,0,0)
    slot_wire1.connect_ends(top_loop)
    slot_wire1.connect_ends(bottom_loop)

    slot_wire2 = antenna_components.wire_Z(length_m = h_mm /1000, wire_diameter_mm = main_wire_diameter_mm, Origin_Z = -h_mm/2000)
    slot_wire2.translate(d_mm/2000,0,0)    
    slot_wire2.rotate_around_Z(angle_deg = feed_gap_angle_deg)
    slot_wire2.connect_ends(top_loop, tol = 0.1)
    slot_wire2.connect_ends(bottom_loop, tol = 0.1)

    model.place_feed(top_loop, feed_alpha_object = 1)
  

    model.add(top_loop)
    model.add(bottom_loop)
    model.add(slot_wire1)
    model.add(slot_wire2)



model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)

antenna_components = geometry_builder.components()

d_mm = 200
h_mm = 200
wd_mm = 10
fd_gap_mm = 10
build_csc(d_mm, h_mm, wd_mm, fd_gap_mm)
#model.write_nec()
model.write_nec_and_run()
gains = model.gains()
vswr = model.vswr()
print(gains, f"vswr:{vswr:.2f}")
print("Note - design not yet optimised")

wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = "Circulare slot cube")

print("Done")


