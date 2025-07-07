from nec_lib.nec_model import NECModel
from nec_lib import geometry_builder
from nec_lib import rf_utils


def build_hentenna(h_m, w_m, fp_m, wd_mm):
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
    
    feed_rod.connect_ends(outer_loop)
    
    model.add(feed_rod)
    model.add(outer_loop)



model = NECModel(working_dir="C:\\Users\\drala\\Documents\\GitHub\\Python_nec\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)

antenna_components = geometry_builder.components(starting_tag_nr = 0,
                            segment_length_m = model.segLength_m,
                            ex_tag = model.EX_TAG)

for i in range(-5, 5):
    h_m = 1+i*0.01
    model.start_geometry()
    build_hentenna(h_m, 0.28, 0.12, 5)
    model.run()
    gain = model.extract_gain()
    z = model.extract_input_impedance()
    vswr = rf_utils.vswr_from_z(z)
    print(f"h_m {h_m:.3f}", gain, f"vswr:{vswr:.2f}")




