from nec_lib.nec_model import NECModel
from nec_lib import geometry_builder
from nec_lib import rf_utils
from nec_lib import wire_viewer

def build_helix(d_mm, l_mm, main_wire_diameter_mm, cld_mm, cl_alpha, cl_spacing_mm):
    global model


    coupling_loop_wire_diameter_mm = 2.0
    
    helix = antenna_components.helix(diameter_mm = d_mm,
                                     length_mm=l_mm,
                                     pitch_mm = l_mm/2,
                                     sense="RH",
                                     segments_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)
    
    coupling_loop = antenna_components.circular_loop_with_feedpoint(diameter_mm = cld_mm,
                                                                    segments=36,
                                                                    wire_diameter_mm = coupling_loop_wire_diameter_mm)

    cl_offset_z = cl_alpha*l_mm/1000
    cl_offset_x = (d_mm - cld_mm - coupling_loop_wire_diameter_mm - main_wire_diameter_mm)/2000
    cl_offset_x -= cl_spacing_mm/1000
    coupling_loop.translate(cl_offset_x, 0, cl_offset_z)

    model.add(helix)
    model.add(coupling_loop)



model = NECModel(working_dir="C:\\Users\\drala\\Documents\\GitHub\\Python_nec\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)


for i in range(-5, 5):
    antenna_components = geometry_builder.components(starting_tag_nr = 0,
                            segment_length_m = model.segLength_m,
                            ex_tag = model.EX_TAG)
    d_mm = 160.5
    l_mm = 159
    wd_mm = 8
    cld_mm = 78
    cl_spacing_mm = 2
    cl_alpha=0.495
    parameter = cl_alpha *(1 + 0.01 *i)
    cl_alpha = parameter
    model.start_geometry()
    build_helix(d_mm, l_mm, wd_mm, cld_mm, cl_alpha, cl_spacing_mm)
    model.run()
    gain = model.extract_gain()
    z = model.extract_input_impedance()
    vswr = rf_utils.vswr_from_z(z)
    print(f"parameter {parameter:.3f}", gain, f"vswr:{vswr:.2f}")

wire_viewer.view_nec_input(model.nec_in)

print("Done")


