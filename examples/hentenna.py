import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_hentenna(h_m, w_m, fp_m, wd_mm):
    global model

    
    feed_rod = antenna_components.wire_Z(length_m = w_m,
                                           wire_diameter_mm = wd_mm)
    feed_rod.rotate_ZtoX()
    feed_rod.translate(0, 0, fp_m)
    
    outer_loop = antenna_components.rect_loop_XZ(length_m = h_m,
                                   width_m = w_m,
                                   wire_diameter_mm = wd_mm,
                                   Origin_Z = -h_m/2)
    
    feed_rod.connect_ends(outer_loop)

    model.place_feed(feed_rod, feed_wire_index=0, feed_alpha_wire=0.5)
    
    model.add(feed_rod)
    model.add(outer_loop)



model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)

antenna_components = geometry_builder.components()

for i in range(-5, 5):
    h_m = 1+i*0.01
    model.start_geometry()
    build_hentenna(h_m, 0.28, 0.12, 5)
#    model.write_nec()
    model.write_nec_and_run()
    gains = model.gains()
    vswr = model.vswr()
    print(gains, f"vswr:{vswr:.2f}")

wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title='Hentenna')


