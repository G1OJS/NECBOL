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

def build_contraspiral(d_mm, l_mm, main_wire_diameter_mm, helix_sep_mm, cld_mm, cl_alpha, cl_spacing_mm):

    model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
    model.set_wire_conductivity(sigma = 58000000)
    model.set_frequency(MHz = 144.2)
    model.set_gain_point(azimuth = 90, elevation = 3)
    model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

    antenna_components = geometry_builder.components()
    model.start_geometry()

    coupling_loop_wire_diameter_mm = 2.0
    
    bottom_helix = antenna_components.helix(diameter_m = d_mm /1000,
                                     length_m = l_mm /1000,
                                     pitch_m = l_mm /2000,
                                     sense="RH",
                                     wires_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)

    top_helix = antenna_components.helix(diameter_m = d_mm /1000,
                                     length_m = l_mm /1000,
                                     pitch_m = l_mm /2000,
                                     sense="LH",
                                     wires_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)
    top_helix.translate(0,0, l_mm/1000 + helix_sep_mm/1000)

    link = antenna_components.connector(bottom_helix, 71, 1, top_helix, 0, 0, main_wire_diameter_mm)
    
    coupling_loop = antenna_components.circular_arc(diameter_m = cld_mm /1000,
                                                    arc_phi_deg = 360,
                                                    n_wires=36,
                                                    wire_diameter_mm = coupling_loop_wire_diameter_mm)
    
    model.place_feed(coupling_loop, feed_alpha_object=0)

    cl_offset_z = cl_alpha*l_mm/1000
    cl_offset_x = (d_mm - cld_mm - coupling_loop_wire_diameter_mm - main_wire_diameter_mm)/2000
    cl_offset_x -= cl_spacing_mm/1000
    coupling_loop.translate(cl_offset_x, 0, cl_offset_z)

    model.add(bottom_helix)
    model.add(coupling_loop)
    model.add(top_helix)
    model.add(link)
    

    return model


from nec_lib.optimisers import RandomOptimiser


param_init = {"d_mm":151, "l_mm":131, "main_wire_diameter_mm":2, "helix_sep_mm":122, "cld_mm":81, "cl_alpha":0.505, "cl_spacing_mm":2.1}

opt = RandomOptimiser(
    build_fn = build_contraspiral,
    param_init = param_init,
    cost_fn = cost_function,
)

best_params, best_info = opt.optimise(verbose=False)



print("Done")


