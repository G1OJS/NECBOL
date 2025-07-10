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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def build_contraspiral(model, d_mm, l_mm, main_wire_diameter_mm, helix_sep_mm, cld_mm, cl_alpha, cl_spacing_mm):

    model.start_geometry()
    antenna_components = geometry_builder.components()

    coupling_loop_wire_diameter_mm = 2.0
    
    bottom_helix = antenna_components.helix(diameter_mm = d_mm,
                                     length_mm = l_mm,
                                     pitch_mm = l_mm / 2,
                                     sense = "RH",
                                     wires_per_turn = 36,
                                     wire_diameter_mm = main_wire_diameter_mm)

    top_helix = antenna_components.helix(diameter_mm = d_mm,
                                     length_mm = l_mm,
                                     pitch_mm = l_mm / 2,
                                     sense = "LH",
                                     wires_per_turn = 36,
                                     wire_diameter_mm = main_wire_diameter_mm)
    top_helix.translate(dx_m = 0, dy_m=0, dz_mm = l_mm + helix_sep_mm)

    link = antenna_components.connector(bottom_helix, 71, 1, top_helix, 0, 0, wire_diameter_mm = main_wire_diameter_mm)
    
    coupling_loop = antenna_components.circular_arc(diameter_mm = cld_mm,
                                                    arc_phi_deg = 360,
                                                    n_wires=36,
                                                    wire_diameter_mm = coupling_loop_wire_diameter_mm)
    
    model.place_feed(coupling_loop, feed_alpha_object=0)
#    model.place_series_RLC_load(top_helix, R_ohms = 0, L_uH = 0, C_pf = 50, load_alpha_object=0.5)

    cl_offset_z_mm = cl_alpha*l_mm
    cl_offset_x_mm = (d_mm - cld_mm - coupling_loop_wire_diameter_mm - main_wire_diameter_mm)/2
    cl_offset_x_mm -= cl_spacing_mm
    coupling_loop.translate(dx_mm = cl_offset_x_mm, dy_m = 0, dz_mm = cl_offset_z_mm)

    model.add(bottom_helix)
    model.add(coupling_loop)
    model.add(top_helix)
    model.add(link)
    
    return model


from nec_lib.optimisers import RandomOptimiser

model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

param_init = {"d_mm":151, "l_mm":131, "main_wire_diameter_mm":2, "helix_sep_mm":122, "cld_mm":81, "cl_alpha":0.505, "cl_spacing_mm":2.1}

opt = RandomOptimiser(
    build_fn = build_contraspiral,
    param_init = param_init,
    cost_fn = cost_function,
)

best_params, best_info = opt.optimise(model, verbose=False)



print("Done")


