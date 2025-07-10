"""
This file is part of the "NECBOL Plain Language Python NEC Runner"
Copyright (c) 2025 Alan Robinson G1OJS

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_antenna(model, l0_mm, l1_mm, l2_mm, y1_mm, y2_mm, main_wire_diameter_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    ref = antenna_components.wire_Z(length_mm = l0_mm, wire_diameter_mm = main_wire_diameter_mm)
    ref.rotate_ZtoX()
    driv = antenna_components.wire_Z(length_mm = l1_mm, wire_diameter_mm = main_wire_diameter_mm)
    driv.rotate_ZtoX()
    driv.translate(dx_m = 0, dy_mm = y1_mm, dz_m = 0)
    d1 = antenna_components.wire_Z(length_mm = l2_mm, wire_diameter_mm = main_wire_diameter_mm)
    d1.rotate_ZtoX()
    d1.translate(dx_m = 0, dy_mm = y2_mm, dz_m = 0)
    
    model.place_feed(driv, feed_alpha_object = 0.5)

    model.add(ref)
    model.add(driv)
    model.add(d1)

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

def analyse(model):
    model.run_nec()
    gains = model.gains()
    vswr = model.vswr()
    print(gains, f"vswr:{vswr:.2f}")

model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "Yagi example",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)


params = {'l0_mm': 1040, 'l1_mm': 1040, 'l2_mm': 1040, 'y1_mm': 250, 'y2_mm': 500, 'main_wire_diameter_mm': 10}
#params = {'l0_mm': 997.23, 'l1_mm': 994.02, 'l2_mm': 889.92, 'y1_mm': 304.22, 'y2_mm': 511.18, 'main_wire_diameter_mm': 8.13}
#params = {'l0_mm': 800.7, 'l1_mm': 1006.48, 'l2_mm': 943.58, 'y1_mm': 117.11, 'y2_mm': 395.46, 'main_wire_diameter_mm': 5.41}

model = build_antenna(model, **params)
model.write_nec()

wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = model.model_name)
analyse(model)
optimise()


print("Done")


