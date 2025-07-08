import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder

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
    
    support_rod = antenna_components.wire_Z(length_m = refl_sep_m, wire_diameter_mm = wd_mm)
    support_rod.rotate_ZtoY()
    support_rod.translate(0,-refl_sep_m/2,h_m)
    
    support_rod.connect_ends(outer_loop)
    support_rod.connect_ends(reflector_loop)

    model.add(feed_rod)
    model.add(reflector_loop)
    model.add(outer_loop)
    model.add(support_rod)


model = NECModel(working_dir="..\\nec_wkg",
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
    refl_scale = 1.0
    refl_sep = 0.1+.01*i
    model.start_geometry()
    build_hentenna_yagi(0.97, 0.28, 0.12, refl_sep, refl_scale, 5)
    model.run()
    gains = model.gains()
    vswr = model.vswr()
    print(gains, f"vswr:{vswr:.2f}")
    
print("Done")


