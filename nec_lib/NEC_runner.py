import subprocess
#import os

global nec_bat, nec_in, nec_out, verbose
verbose = True

def init():
    global nec_bat, nec_in, nec_out
    wd = "C:\\Users\\drala\\Documents\\GitHub\\Python_nec\\nec_wkg\\"
    nec_exe = "C:\\4nec2\\exe\\nec2dxs11k.exe"
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
    proc = subprocess.run([nec_bat])

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





    
