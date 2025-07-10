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


def build_csc(model, d_mm, h_mm, main_wire_diameter_mm, feed_gap_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    feed_gap_angle_deg = 360*feed_gap_mm / (math.pi*d_mm)

    top_loop = antenna_components.circular_arc(diameter_mm = d_mm, arc_phi_deg = 360-feed_gap_angle_deg, n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    bottom_loop = antenna_components.circular_arc(diameter_mm = d_mm, arc_phi_deg = 360-feed_gap_angle_deg,  n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    top_loop.translate(dx_m = 0, dy_m = 0, dz_mm = h_mm)
    
    slot_wire1 = antenna_components.wire_Z(length_mm = h_mm, wire_diameter_mm = main_wire_diameter_mm)
    slot_wire1.translate(dx_mm = d_mm / 2, dy_m = 0, dz_mm = h_mm /2)
    slot_wire1.connect_ends(top_loop)
    slot_wire1.connect_ends(bottom_loop)

    slot_wire2 = antenna_components.wire_Z(length_mm = h_mm, wire_diameter_mm = main_wire_diameter_mm)
    slot_wire2.translate(dx_mm = d_mm/2, dy_m = 0, dz_mm = h_mm /2)  
    slot_wire2.rotate_around_Z(angle_deg = feed_gap_angle_deg)
    slot_wire2.connect_ends(top_loop, tol = 0.1)
    slot_wire2.connect_ends(bottom_loop, tol = 0.1)

    model.place_feed(top_loop, feed_alpha_object = 1)

    model.add(top_loop)
    model.add(bottom_loop)
    model.add(slot_wire1)
    model.add(slot_wire2)

    return model

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from nec_lib.optimisers import RandomOptimiser

    param_init = params
    best_params, best_info = RandomOptimiser(build_csc, param_init, cost_function).optimise(model, verbose=False)

def analyse():
    model = build_csc(model, **params)
    model.write_nec()
    model.run_nec()
    gains = model.gains()
    vswr = model.vswr()
    print(gains, f"vswr:{vswr:.2f}")

def view():
    model = build_csc(model, **params)
    model.write_nec()
    wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = "Circular slot cube")

model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)


params = {'d_mm': 209.49, 'h_mm': 202.84, 'main_wire_diameter_mm': 3.67, 'feed_gap_mm': 10.08}
#view()
#analyse()
optimise()
print("Done")


