global GN_CARD, GE_CARD, LOADS, FR_CARD, RP_CARD, GM_CARD_Origin_Height_AGL, comments, LD_WIRECOND

def set_wire_conductivity(sigma):
    global LD_WIRECOND
    LD_WIRECOND=f"LD 5 0 0 0 {sigma:.6f} \n"

def set_frequency(MHz):
    global FR_CARD
    FR_CARD = f"FR 0 1 0 0 {MHz:.3f} 0\n"
    
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

def start(comments = "No comments specified"):
    global model, LOADS
    model = "CM "+ comments + "\nCE\n"
    LOADS = []

def add(geomObj):
    global model
    for w in geomObj.get_wires():
        x1, y1, z1 = w['a']
        x2, y2, z2 = w['b']
        model += f"GW {w['nTag']} {w['nS']} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {w['wr']:.3f}\n"

def finalise():
    global model
    model += GM_CARD_Origin_Height_AGL
    model += GE_CARD
    model += GN_CARD
    model += LD_WIRECOND
    EX_CARD = f"EX 0 999 1 0 1 0\n"
    model += EX_CARD
    model += FR_CARD
    model += RP_CARD
    model += "EN"
    return model

