import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_antenna(model, A_mm, B_mm, C_mm, D_mm, main_wire_diameter_mm):

    E_mm  = B_mm + C_mm + D_mm

    model.start_geometry()
    antenna_components = geometry_builder.components()

    front = antenna_components.wire_Z(length_mm = A_mm, wire_diameter_mm = main_wire_diameter_mm)
    front.rotate_ZtoX()
    front.translate(dx_mm = 0, dy_mm = E_mm , dz_mm = 0)

    front_left = antenna_components.wire_Z(length_mm = B_mm, wire_diameter_mm = main_wire_diameter_mm)
    front_left.rotate_ZtoX()
    front_left.rotate_around_Z(90)
    front_left.translate(dx_mm = -A_mm/2, dy_mm = B_mm/2 + C_mm + D_mm, dz_mm = 0)

    front_right = antenna_components.copy_of(front_left)
    front_right.translate(dx_mm = A_mm, dy_mm = 0, dz_mm = 0)

    rear = antenna_components.copy_of(front)
    rear.translate(dx_mm = 0, dy_mm = -E_mm, dz_mm = 0)

    rear_left = antenna_components.wire_Z(length_mm =D_mm, wire_diameter_mm = main_wire_diameter_mm)
    rear_left.rotate_ZtoX()
    rear_left.rotate_around_Z(90)
    rear_left.translate(dx_mm = -A_mm/2, dy_mm = D_mm/2, dz_mm = 0)

    rear_right = antenna_components.copy_of(rear_left)
    rear_right.translate(dx_mm = A_mm, dy_mm = 0, dz_mm = 0)
 
    model.place_feed(front, feed_alpha_object = 0.5)

    model.add(front)
    model.add(front_left)
    model.add(front_right)
    model.add(rear)
    model.add(rear_left)
    model.add(rear_right)    
 
    return model

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from nec_lib.optimisers import RandomOptimiser
    param_init = params
    bounds = {"l0_mm":(800,1200),"l1_mm":(800,1200),"l2_mm":(800,1200),"y1_mm":(100,310),"y2_mm":(320,800)}
    best_params, best_info = RandomOptimiser(build_antenna, param_init, cost_function,
                                             max_iter=1000, bounds = bounds).optimise(model, verbose=False)

model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

params = {'A_mm': 750, 'B_mm': 100, 'C_mm': 30, 'D_mm': 140, 'main_wire_diameter_mm': 10}
# Optimiser Results (copy and paste into your antenna file for reference)
# [] INITIAL: VSWR:1.60 Gain:11.25 with {'A_mm': '750.00', 'B_mm': '100.00', 'C_mm': '30.00', 'D_mm': '140.00', 'main_wire_diameter_mm': '10.00'}
# []   FINAL: VSWR:1.57 Gain:12.00 with {'A_mm': '727.87', 'B_mm': '98.98', 'C_mm': '26.05', 'D_mm': '133.48', 'main_wire_diameter_mm': '9.72'}


model = build_antenna(model, **params)
model.write_nec()
wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = "Moxon")

optimise()
print("Done")


