from . import NEC_runner as NEC
from . import Geometries as GEOMS

global GN_CARD, GE_CARD, LOADS, FR_CARD, RP_CARD, EX_CARD, GM_CARD_Origin_Height_AGL, comments


comments ="CM No comments specified\n"

def set_wire_conductivity(sigma):
    global LOADS
    LOADS.append(f"LD 5 0 0 0 {sigma:.6f} \n")

def set_frequency(MHz):
    global FR_CARD
    FR_CARD = f"FR 0 1 0 0 {MHz:.3f} 0\n"
    GEOMS.set_lambda(300/MHz)
    
def set_gain_point(azimuth, elevation):
    global RP_CARD
    RP_CARD = f"RP 0 1 1 1000 {90-elevation:.0f} {azimuth:.0f} 0 0\n"

def set_ground(eps_r = 1, sigma = 1, origin_height_m = 10):
    global GE_CARD, GN_CARD, GM_CARD_Origin_Height_AGL
    if(eps_r == 1.0):
        GE_CARD = "GE 0\n"
        GN_CARD = ""
        GM_CARD_Origin_Height_AGL = f"GM 0 0 0 0 0 0 0 0.000\n"
    else:
        GE_CARD = "GE 1\n"
        GN_CARD = f"GN 2 0 0 0 {eps_r:.3f} {sigma:.3f} \n"
        GM_CARD_Origin_Height_AGL = f"GM 0 0 0 0 0 0 0 {origin_height_m:.3f}\n"

def start_model(comments = "No comments specified"):
    global model, LOADS
    model = "CM "+ comments + "\nCE\n"
    LOADS = []
    GEOMS.init_object_counter()

def add_Wire(wireString):
    global model
    model += wireString

def set_Source(srcString):
    global EX_CARD
    EX_CARD = srcString

def write_model():
    global model
    model += GM_CARD_Origin_Height_AGL
    model += GE_CARD
    model += GN_CARD
    for load_card in LOADS:
        model += (load_card)
    model += EX_CARD
    model += FR_CARD
    model += RP_CARD
    model += "EN"
    with open(NEC.nec_in, "w") as f:
        f.write(model)
    f.close()
