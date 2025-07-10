import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_hentenna_yagi(h_m, w_m, fp_m, refl_sep_m, refl_scale, wd_mm):

    model.start_geometry()

    antenna_components = geometry_builder.components()   
    feed_rod = antenna_components.wire_Z(length_m = w_m,
                                           wire_diameter_mm = wd_mm)
    feed_rod.rotate_ZtoX()
    feed_rod.translate(dx_m = 0, dy_m = 0, dz_m = fp_m)
    
    hentenna_outer_loop = antenna_components.rect_loop_XZ(length_m = h_m,
                                   width_m = w_m,
                                   wire_diameter_mm = wd_mm)
    hentenna_outer_loop.translate(dx_m = 0, dy_m = 0, dz_m = h_m/2)


    reflector_loop = antenna_components.rect_loop_XZ(length_m = refl_scale*(h_m-fp_m),
                                   width_m = refl_scale*w_m,
                                   wire_diameter_mm = wd_mm)
    
    feed_rod.connect_ends(hentenna_outer_loop)
    reflector_loop.translate(dx_m = 0, dy_m = -refl_sep_m, dz_m = h_m/2 + fp_m/2)
    
    support_rod = antenna_components.connector(from_object = hentenna_outer_loop, from_wire_index=3, from_alpha_wire=0.5,
                                               to_object = reflector_loop, to_wire_index=3, to_alpha_wire=0.5)
    support_rod.connect_ends(hentenna_outer_loop)
    support_rod.connect_ends(reflector_loop)

    model.place_feed(feed_rod, feed_wire_index=0, feed_alpha_wire=0.5)
    
    model.add(feed_rod)
    model.add(reflector_loop)
    model.add(hentenna_outer_loop)
    model.add(support_rod)

    return model

model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)

for i in range(-5, 5):
    hen_height_m = 0.97
    hen_width_m = 0.271
    feed_height_m = 0.12
    refl_scale = 0.985
    refl_sep = 0.33
    parameter = feed_height_m *(1 + 0.01 *i)
    feed_height_m = parameter
    model = build_hentenna_yagi(hen_height_m, hen_width_m, feed_height_m, refl_sep, refl_scale, 5)
    model.write_nec()
    model.run_nec()
    gains = model.gains()
    vswr = model.vswr()
    print(f"parameter {parameter:.3f}", gains, f"vswr:{vswr:.2f}")

wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title='Hentenna with reflector')

print("Done")


