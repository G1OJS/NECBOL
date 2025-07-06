from nec_lib import NEC_runner as NEC
from nec_lib import NEC_builder as BUILD
from nec_lib import Geometries as GEOMS
from nec_lib import RF_utils as RF

def tabulate(length):
    BUILD.start_model()
    BUILD.set_wire_conductivity(sigma = 58000000)
    BUILD.set_frequency(MHz = 144.2)
    BUILD.set_gain_point(azimuth = 0, elevation = 5)
    BUILD.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
    GEOMS.add_wire_with_feedpoint(length_m = length, wire_diameter_mm = 1.0, feedpoint_alpha = 0.5)
    BUILD.write_model()
    
    NEC.run()
    gain = NEC.extract_gain()
    z = NEC.extract_input_impedance()
    vswr = RF.vswr_from_z(z)
    print(length, gain, vswr)

NEC.init()

for i in range(5):
    l = 0.8+0.1*i
    tabulate(l)
