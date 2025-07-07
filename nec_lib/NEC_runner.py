import subprocess
global nec_bat, nec_in, nec_out, verbose, model_text
verbose = False

class model:
    
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
        global model_text, LOADS
        model_text = "CM "+ comments + "\nCE\n"
        LOADS = []

    def add(geomObj):
        global model_text
        for w in geomObj.get_wires():
            x1, y1, z1 = w['a']
            x2, y2, z2 = w['b']
            model_text += f"GW {w['nTag']} {w['nS']} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {w['wr']:.3f}\n"

    def finalise():
        global model_text
        model_text += GM_CARD_Origin_Height_AGL
        model_text += GE_CARD
        model_text += GN_CARD
        model_text += LD_WIRECOND
        EX_CARD = f"EX 0 999 1 0 1 0\n"
        model_text += EX_CARD
        model_text += FR_CARD
        model_text += RP_CARD
        model_text += "EN"
        return model_text

def write_runner_files(nec_exe, wd):
    global nec_bat, nec_in, nec_out
    nec_bat = wd+"nec.bat"
    nec_in=wd + "model.nec"
    nec_out=wd + "model.out"
    nec_files = wd + "files.txt"
    with open(nec_bat, "w") as f:
        f.write(nec_exe+" < "+ wd+"files.txt\n")
    with open(nec_files, "w") as f:
        f.write(nec_in+"\n")
        f.write(nec_out+"\n")

def run():
    model_text = model.finalise()
    with open(nec_in, "w") as f:
        f.write(model_text)
    proc = subprocess.run([nec_bat], creationflags=subprocess.CREATE_NO_WINDOW)

def extract_gain():
    with open(nec_out) as f:
        while True:
            if("RADIATION PATTERNS" in f.readline()):
                break
        l = f.readline()
        l = f.readline()
        l = f.readline()
        l = f.readline()
        l = f.readline()
        if(verbose):
          print("0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")
          print(l)
        v_gain = float(l[21:29])
        h_gain = float(l[29:37])
        total = float(l[37:45])
        return {"v_gain": v_gain, "h_gain": h_gain, "total": total}

def extract_input_impedance():
    with open(nec_out) as f:
        while True:
            if("ANTENNA INPUT PARAMETERS" in f.readline()):
                break
        l = f.readline()
        l = f.readline()
        l = f.readline()
        l = f.readline()
        if(verbose):
          print("0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")
          print(l)
        r = float(l[60:72])
        x = float(l[72:84])
        return complex(r, x)





    
