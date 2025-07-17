
from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file
import math

# note that everything from here down is user code to adapt

def build_csc(model, d_mm, h_mm, main_wire_diameter_mm, feed_gap_mm):

    model.start_geometry()
    antenna_components = components()

    feed_gap_angle_deg = 360*feed_gap_mm / (math.pi*d_mm)

    top_loop = antenna_components.circular_arc(diameter_mm = d_mm, arc_phi_deg = 360-feed_gap_angle_deg, n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    bottom_loop = antenna_components.circular_arc(diameter_mm = d_mm, arc_phi_deg = 360-feed_gap_angle_deg,  n_wires=36, wire_diameter_mm = main_wire_diameter_mm)
    
    top_loop.translate(dx_m = 0, dy_m = 0, dz_mm = h_mm)

    # with new treatment of wire splitting for connections, this has to come before connecting wires
    # otherwise a zero-length wire is created
 #  model.place_feed(top_loop, feed_alpha_object = 1)
       
    slot_wire1 = antenna_components.wire_Z(length_mm = h_mm, wire_diameter_mm = main_wire_diameter_mm)
    slot_wire1.translate(dx_mm = d_mm / 2, dy_m = 0, dz_mm = h_mm /2)
    slot_wire1.connect_ends(top_loop)
    slot_wire1.connect_ends(bottom_loop)

    slot_wire2 = antenna_components.wire_Z(length_mm = h_mm, wire_diameter_mm = main_wire_diameter_mm)
    slot_wire2.translate(dx_mm = d_mm/2, dy_m = 0, dz_mm = h_mm /2)  
    slot_wire2.rotate_around_Z(angle_deg = -feed_gap_angle_deg)
    slot_wire2.connect_ends(top_loop, tol = 0.1)
    slot_wire2.connect_ends(bottom_loop, tol = 0.1)

    model.add(top_loop)
    model.add(bottom_loop)
    model.add(slot_wire1)
    model.add(slot_wire2)

    return model

def cost_function(model):
    # this function should return the cost and info entries as appropriate for your optimisation
    # the example below creates cost from:
    #   the square of VSWR, added to
    #   the square of the amount by which the gain in the specified direction is below 15dBi
    # depending on what you want to optimise, changing this cost function may get you better results
    vcost = model.vswr()
    g = model.h_gain()
    gcost = 15-g
    return ({"cost":vcost*vcost + gcost*gcost, "info":f"VSWR:{vcost:.2f} Gain:{g:.2f}"})

def optimise():
    from necbol.optimisers import RandomOptimiser
    param_init = params
    best_params, best_info = RandomOptimiser(build_csc, param_init, cost_function).optimise(model, tty=False)

model = NECModel(working_dir="nec_wkg",
                 model_name="Circular slot cube",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)

params = {'d_mm': 200, 'h_mm': 200, 'main_wire_diameter_mm': 5, 'feed_gap_mm': 10}
model = build_csc(model, **params)
model.write_nec()
show_wires_from_file(model.nec_in, model.EX_TAG, title = model.model_name)

optimise()

print(f"\n\nEnd of example {model.model_name}")


