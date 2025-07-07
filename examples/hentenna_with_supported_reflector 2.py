from nec_lib.nec_model import NECModel
from nec_lib import geometry_builder
from nec_lib import rf_utils
from nec_lib import wire_viewer

def build_hentenna_yagi(h_m, w_m, fp_m, refl_sep_m, refl_scale, wd_mm):
    global model

    
    feed_rod = antenna_components.wire_Z_with_feedpoint(length_m = w_m,
                                           wire_diameter_mm = wd_mm,
                                           feedpoint_alpha = 0.5)
    feed_rod.rotate_ZtoX()
    feed_rod.translate(0, 0, fp_m)
    
    outer_loop = antenna_components.rect_loop_XZ(length_m = h_m,
                                   width_m = w_m,
                                   wire_diameter_mm = wd_mm,
                                   Origin_Z = -h_m/2)

    reflector_loop = antenna_components.rect_loop_XZ(length_m = refl_scale*(h_m-fp_m),
                                   width_m = refl_scale*w_m,
                                   wire_diameter_mm = wd_mm,
                                   Origin_Z = -h_m/2)
    
    feed_rod.connect_ends(outer_loop)
    reflector_loop.translate(0,-refl_sep_m,fp_m/2)
    
    support_rod = antenna_components.connector(fromObject = outer_loop, fromParam=3.5, toObject = reflector_loop, toParam=3.5)
    support_rod.connect_ends(outer_loop)
    support_rod.connect_ends(reflector_loop)
    
    model.add(feed_rod)
    model.add(reflector_loop)
    model.add(outer_loop)
    model.add(support_rod)


model = NECModel(working_dir="C:\\Users\\drala\\Documents\\GitHub\\Python_nec\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = -90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)


for i in range(-5, 5):
    antenna_components = geometry_builder.components(starting_tag_nr = 0,
                            segment_length_m = model.segLength_m,
                            ex_tag = model.EX_TAG)
    hen_height_m = 0.97
    hen_width_m = 0.274
    feed_height_m = 0.12
    refl_scale = 0.96
    refl_sep = 0.242
    parameter = feed_height_m *(1 + 0.01 *i)
    feed_height_m = parameter
    model.start_geometry()
    build_hentenna_yagi(hen_height_m, hen_width_m, feed_height_m, refl_sep, refl_scale, 5)
    model.run()
    gain = model.extract_gain()
    z = model.extract_input_impedance()
    vswr = rf_utils.vswr_from_z(z)
    print(f"parameter {parameter:.3f}", gain, f"vswr:{vswr:.2f}")

wire_viewer.view_nec_input(model.nec_in)

print("Done")


