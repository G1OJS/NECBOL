from nec_lib import NEC_runner as NEC
from nec_lib import NEC_builder as BUILD
from nec_lib import Geometries as GEOMDEF
from nec_lib import RF_utils as RF


def set_environment():
    BUILD.set_wire_conductivity(sigma = 58000000)
    BUILD.set_frequency(MHz = 144.2)
    BUILD.set_gain_point(azimuth = 90, elevation = 5)
    BUILD.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)


def build_hentenna(h_m, w_m, fp_m, wd_mm):
    BUILD.start_model()
    feed_rod = GEOMDEF.wire_with_feedpoint(length_m = w_m, wire_diameter_mm = wd_mm, feedpoint_alpha = 0.5)
    feed_rod.Rotate_ZtoX()
    feed_rod.Translate(0,0,fp_m-h_m/2)
    outer_loop = GEOMDEF.rect_loop(length_m = h_m, width_m = w_m, wire_diameter_mm = wd_mm)
    feed_rod.connect_ends(outer_loop)
    BUILD.CommitToModel(feed_rod)
    BUILD.CommitToModel(outer_loop)
    BUILD.write_model()

def tabulate(length):
    build_hentenna(length, 0.28, 0.12, 5)
    NEC.run()
    gain = NEC.extract_gain()
    z = NEC.extract_input_impedance()
    vswr = RF.vswr_from_z(z)
    print(f"Length {length:.3f}", gain, f"vswr:{vswr:.2f}")

NEC.init()

set_environment()

for i in range(5):
    l = 0.97+0.01*i
    tabulate(l)


