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

def build_antenna(model, l0_mm, l1_mm, l2_mm, dy1_mm, dy2_mm, w0d_mm, w1d_mm, w2d_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    ref = antenna_components.wire_Z(length_mm = l0_mm, wire_diameter_mm = w0d_mm)
    ref.rotate_ZtoX()
    driv = antenna_components.wire_Z(length_mm = l1_mm, wire_diameter_mm = w1d_mm)
    driv.rotate_ZtoX()
    driv.translate(dx_m = 0, dy_mm = dy1_mm, dz_m = 0)
    d1 = antenna_components.wire_Z(length_mm = l2_mm, wire_diameter_mm = w2d_mm)
    d1.rotate_ZtoX()
    d1.translate(dx_m = 0, dy_mm = dy1_mm + dy2_mm, dz_m = 0)
    
    model.place_feed(driv, feed_alpha_object = 0.5)

    model.add(ref)
    model.add(driv)
    model.add(d1)

    return model

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":0.1*vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from nec_lib.optimisers import RandomOptimiser
    param_init = params
    best_params, best_info = RandomOptimiser(build_antenna, param_init, cost_function,
                                             max_iter=1000, bounds = bounds).optimise(model, verbose=False)

model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "2m Yagi 3 ele indep wire radii",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

params = {'l0_mm': 708.92, 'l1_mm': 1021.76, 'l2_mm': 939.93, 'dy1_mm': 154.03, 'dy2_mm': 208.08, 'w0d_mm': 8.64, 'w1d_mm': 11.25, 'w2d_mm': 7.85}
bounds = {"l0_mm":(950,1200),"l1_mm":(800,1200),"l2_mm":(800,1200),"dy1_mm":(10,1000),"dy2_mm":(10,1000)}

# Optimiser Results (copy and paste into your antenna file for reference)
# [] INITIAL: VSWR:2.31 Gain:12.00 with {'l0_mm': 800.01, 'l1_mm': 1030.42, 'l2_mm': 946.23, 'dy1_mm': 172.44, 'dy2_mm': 189.56, 'w0d_mm': 9.06, 'w1d_mm': 10.97, 'w2d_mm': 7.50}
# []   FINAL: VSWR:2.11 Gain:12.17 with {'l0_mm': 708.92, 'l1_mm': 1021.76, 'l2_mm': 939.93, 'dy1_mm': 154.03, 'dy2_mm': 208.08, 'w0d_mm': 8.64, 'w1d_mm': 11.25, 'w2d_mm': 7.85}
# []   FINAL: VSWR:2.08 Gain:12.23 with {'l0_mm': 669.80, 'l1_mm': 1015.67, 'l2_mm': 939.54, 'dy1_mm': 151.21, 'dy2_mm': 216.39, 'w0d_mm': 8.79, 'w1d_mm': 11.54, 'w2d_mm': 7.54}


model = build_antenna(model, **params)
model.write_nec()
wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = model.model_name)
optimise()


print("Done")


