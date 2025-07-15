

from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file

def cost_function(model):
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def build_contraspiral(model, d_mm, l_mm, main_wire_diameter_mm, helix_sep_mm, cld_mm, cl_alpha, cl_spacing_mm):

    model.start_geometry()
    antenna_components = components()

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


from necbol.optimisers import RandomOptimiser

model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "G1OJS Contraspiral",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

param_init = {"d_mm":151, "l_mm":131, "main_wire_diameter_mm":2, "helix_sep_mm":122, "cld_mm":81, "cl_alpha":0.505, "cl_spacing_mm":2.1}

model=build_contraspiral(model, **param_init)
model.write_nec()
show_wires_from_file(model.nec_in, model.EX_TAG, title = model.model_name)

opt = RandomOptimiser(
    build_fn = build_contraspiral,
    param_init = param_init,
    cost_fn = cost_function,
)

best_params, best_info = opt.optimise(model, verbose=False)



print("Done")


