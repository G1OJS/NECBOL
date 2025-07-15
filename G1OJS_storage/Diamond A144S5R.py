
import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from necbol.nec_wrapper import NECModel
from necbol import geometry_builder
from necbol import wire_viewer

def build_antenna(model, l0_mm, l1_mm, l2_mm, l3_mm, l4_mm, dy1_mm, dy2_mm, dy3_mm, dy4_mm, driver_d_mm, d_R_mm, d_D1_mm, d_D2_mm, d_D3_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    ref = antenna_components.wire_Z(length_mm = l0_mm, wire_diameter_mm = d_R_mm)
    ref.rotate_ZtoX()
    driv = antenna_components.wire_Z(length_mm = l1_mm, wire_diameter_mm = driver_d_mm)
    driv.rotate_ZtoX()
    driv.translate(dx_m = 0, dy_mm = dy1_mm, dz_m = 0)
    d1 = antenna_components.wire_Z(length_mm = l2_mm, wire_diameter_mm = d_D1_mm)
    d1.rotate_ZtoX()
    d1.translate(dx_m = 0, dy_mm = dy1_mm + dy2_mm, dz_m = 0)
    d2 = antenna_components.wire_Z(length_mm = l2_mm, wire_diameter_mm = d_D2_mm)
    d2.rotate_ZtoX()
    d2.translate(dx_m = 0, dy_mm = dy1_mm + dy2_mm + dy3_mm, dz_m = 0)
    d3 = antenna_components.wire_Z(length_mm = l2_mm, wire_diameter_mm = d_D3_mm)
    d3.rotate_ZtoX()
    d3.translate(dx_m = 0, dy_mm = dy1_mm + dy2_mm + dy3_mm + dy4_mm, dz_m = 0)

    
    model.place_feed(driv, feed_alpha_object = 0.5)

    model.add(ref)
    model.add(driv)
    model.add(d1)
    model.add(d2)
    model.add(d3)

    return model

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 20-g
    return ({"cost":0.1*vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from necbol.optimisers import RandomOptimiser
    param_init = params
    best_params, best_info = RandomOptimiser(build_antenna, param_init, cost_function,
                                             max_iter=1000, bounds = bounds).optimise(model, verbose=False)

model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "Diamond AS144S5R",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

orig_params = {'l0_mm': 960, 'l1_mm': 1100, 'l2_mm': 920, 'l3_mm': 920, 'l4_mm': 920,
          'dy1_mm': 375, 'dy2_mm': 90, 'dy3_mm': 190,'dy4_mm': 265,
          'driver_d_mm':12, 'other_d_mm':5}

params={'l0_mm': 973.43, 'l1_mm': 1181.45, 'l2_mm': 958.36, 'l3_mm': 548.13, 'l4_mm': 649.32,
        'dy1_mm': 604.41, 'dy2_mm': 118.42, 'dy3_mm': 265.24, 'dy4_mm': 242.16, 'driver_d_mm': 14.46, 'd_R_mm': 4.97, 'd_D1_mm': 4.97, 'd_D2_mm': 4.97, 'd_D3_mm': 4.97}

bounds = {"l0_mm":(950,1200),"l1_mm":(800,1200),"l2_mm":(800,1200),"dy1_mm":(10,1000),"dy2_mm":(10,1000)}


# [] INITIAL: VSWR:1.11 Gain:14.71 with {'l0_mm': 973.43, 'l1_mm': 1181.45, 'l2_mm': 958.36, 'l3_mm': 548.13, 'l4_mm': 649.32, 'dy1_mm': 604.41, 'dy2_mm': 118.42, 'dy3_mm': 265.24, 'dy4_mm': 242.16, 'driver_d_mm': 14.46, 'other_d_mm': 4.97}
# []   FINAL: VSWR:2.32 Gain:15.03 with {'l0_mm': 988.56, 'l1_mm': 1006.14, 'l2_mm': 925.72, 'l3_mm': 583.52, 'l4_mm': 608.38, 'dy1_mm': 539.83, 'dy2_mm': 124.77, 'dy3_mm': 257.88, 'dy4_mm': 248.42, 'driver_d_mm': 15.10, 'other_d_mm': 5.28}

# [] INITIAL: VSWR:1.11 Gain:14.71 with {'l0_mm': 973.43, 'l1_mm': 1181.45, 'l2_mm': 958.36, 'l3_mm': 548.13, 'l4_mm': 649.32, 'dy1_mm': 604.41, 'dy2_mm': 118.42, 'dy3_mm': 265.24, 'dy4_mm': 242.16, 'driver_d_mm': 14.46, 'd_R_mm': 4.97, 'd_D1_mm': 4.97, 'd_D2_mm': 4.97, 'd_D3_mm': 4.97}
# []   FINAL: VSWR:1.28 Gain:15.04 with {'l0_mm': 988.39, 'l1_mm': 932.91, 'l2_mm': 921.64, 'l3_mm': 543.56, 'l4_mm': 805.03, 'dy1_mm': 563.23, 'dy2_mm': 130.66, 'dy3_mm': 214.39, 'dy4_mm': 244.76, 'driver_d_mm': 17.36, 'd_R_mm': 4.58, 'd_D1_mm': 4.37, 'd_D2_mm': 5.58, 'd_D3_mm': 5.30}

model = build_antenna(model, **params)
model.write_nec()
model.run_nec()
wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = model.model_name)


print("Done")


