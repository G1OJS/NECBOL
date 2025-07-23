import sys, os
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file, plot_gain

def build_antenna(model, l_mm, ra1,rp1,ra2,rp2,ra3,rp3, pa1,pp1,pa2,pp2,pa3,pp3):

    model.start_geometry()
    antenna_components = components()
    
    helix = antenna_components.flexi_helix(
                                length_mm=l_mm,
                                r0_mm=100,
                                p0_mm=50,
                                wire_diameter_mm=2.0,
                                wires_per_turn=32,
                                sense="RH",
                                n_cos=3,
                                r_cos_params=[(ra1-1, rp1-1), (ra2-1, rp2-1), (ra3-1, rp3-1)],   
                                p_cos_params=[(pa1-1, pp1-1), (pa2-1, pp2-1), (pa3-1, pp3-1)]    
                                )
    # flexi-helix produces antennas longer than l_mm?
    # maybe start a bit simpler than this!


    helix.translate(dx_mm=0, dy_mm=0, dz_mm = l_mm/2)
    
    model.place_feed(helix, feed_alpha_object=0)

    model.add(helix)
    
    return model


def cost_function(model):
    vcost = model.vswr()
    g = model.v_gain()
    gcost = 8-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from necbol.optimisers import RandomOptimiser
    param_init = params
    best_params, best_info = RandomOptimiser(build_antenna, param_init, cost_function, delta_init=0.05).optimise(model, verbose=False, tty=False)

model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "G1OJS FlexiHelix",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 1.01, sigma = 58000000, origin_height_m = 0.0)

params = {'l_mm': 206.36, 'ra1': 1.34, 'rp1': 0.93, 'ra2': 1.38, 'rp2': 1.10, 'ra3': 1.60, 'rp3': 1.12, 'pa1': 5.99, 'pp1': 0.80, 'pa2': 0.62, 'pp2': 1.23, 'pa3': 0.63, 'pp3': 1.16}

bounds = {'l_mm':(10,200)}

model=build_antenna(model,**params)
model.write_nec()
show_wires_from_file(model.nec_in, model.EX_TAG, title=model.model_name)


optimise()

print("Done")

# [] INITIAL: VSWR:20.77 Gain:6.93 with {'l_mm': 520.00, 'ra1': 1.81, 'rp1': 0.96, 'ra2': 1.40, 'rp2': 1.03, 'ra3': 1.60, 'rp3': 0.76, 'pa1': 3.27, 'pp1': 1.05, 'pa2': 0.88, 'pp2': 1.06, 'pa3': 0.70, 'pp3': 1.16}
# []   FINAL: VSWR:1.41 Gain:7.19 with {'l_mm': 549.91, 'ra1': 1.60, 'rp1': 0.94, 'ra2': 1.46, 'rp2': 1.07, 'ra3': 1.58, 'rp3': 0.80, 'pa1': 3.02, 'pp1': 1.01, 'pa2': 0.94, 'pp2': 1.05, 'pa3': 0.65, 'pp3': 1.17}
