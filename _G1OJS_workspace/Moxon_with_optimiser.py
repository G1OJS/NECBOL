import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_antenna(model, A_m, B_m, C_m, D_m, main_wire_diameter_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    f1 = antenna_components.wire_Z(length_m = A_m, wire_diameter_mm = main_wire_diameter_mm)
    f1.rotate_ZtoX()
    f1.translate(dx_m = 0, dy_m = B_m, dz_m = 0)

    f2 = antenna_components.wire_Z(length_m = B_m, wire_diameter_mm = main_wire_diameter_mm)
    f2.rotate_ZtoX()
    f2.translate(dx_m = A_m/2, dy_m = B_m/2, dz_m = 0)

    model.place_feed(f1, feed_alpha_object = 0.5)

    model.add(f1)

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

params = {'A_m': 0.75, 'B_m': 0.1, 'C_m': .03, 'D_m': 0.14, 'main_wire_diameter_mm': 10}

model = build_antenna(model, **params)
model.write_nec()
wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = "Circulare slot cube")

#optimise()
print("Done")


