import subprocess
import os

class NECModel:
    def __init__(self, working_dir, nec_exe_path, verbose=False):
        self.verbose = verbose
        self.working_dir = working_dir
        self.nec_exe = nec_exe_path
        self.nec_bat = working_dir + "\\nec.bat"
        self.nec_in = working_dir + "\\model.nec"
        self.nec_out = working_dir + "\\model.out"
        self.files_txt = working_dir + "\\files.txt"
        self.model_text = ""
        self.LD_WIRECOND = ""
        self.FR_CARD = ""
        self.RP_CARD = ""
        self.GE_CARD = ""
        self.GN_CARD = ""
        self.GM_CARD = ""
        self.comments = ""
        self.EX_TAG = 999
        self.nSegs_per_wavelength = 40
        self.segLength_m = 0
        self.write_runner_files()
        
    def write_runner_files(self):
        with open(self.nec_bat, "w") as f:
            f.write(f"{self.nec_exe} < {self.files_txt} \n")
        with open(self.files_txt, "w") as f:
            f.write(f"{self.nec_in}\n{self.nec_out}\n")

    def set_wire_conductivity(self, sigma):
        self.LD_WIRECOND = f"LD 5 0 0 0 {sigma:.6f} \n"

    def set_frequency(self, MHz):
        self.FR_CARD = f"FR 0 1 0 0 {MHz:.3f} 0\n"
        lambda_m = 300/MHz
        self.segLength_m = lambda_m / self.nSegs_per_wavelength
        
    def set_gain_point(self, azimuth, elevation):
        self.RP_CARD = f"RP 0 1 1 1000 {90-elevation:.0f} {azimuth:.0f} 0 0\n"

    def set_ground(self, eps_r=1, sigma=1, origin_height_m=10):
        if eps_r == 1.0:
            self.GE_CARD = "GE 0\n"
            self.GN_CARD = ""
            self.GM_CARD = "GM 0 0 0 0 0 0 0 0.000\n"
        else:
            self.GE_CARD = "GE 1\n"
            self.GN_CARD = f"GN 2 0 0 0 {eps_r:.3f} {sigma:.3f} \n"
            self.GM_CARD = f"GM 0 0 0 0 0 0 0 {origin_height_m:.3f}\n"

    def start_geometry(self, comments="No comments specified"):
        self.comments = comments
        self.model_text = "CM " + comments + "\nCE\n"

    def add(self, geomObj):
        for w in geomObj.get_wires():
            x1, y1, z1 = w['a']
            x2, y2, z2 = w['b']
            self.model_text += (
                f"GW {w['nTag']} {w['nS']} {x1:.3f} {y1:.3f} {z1:.3f} "
                f"{x2:.3f} {y2:.3f} {z2:.3f} {w['wr']:.3f}\n"
            )

    def finalise(self):
        self.model_text += self.GM_CARD
        self.model_text += self.GE_CARD
        self.model_text += self.GN_CARD
        self.model_text += "EK\n"
        self.model_text += self.LD_WIRECOND
        self.model_text += f"EX 0 {self.EX_TAG} 1 0 1 0\n"
        self.model_text += self.FR_CARD
        self.model_text += self.RP_CARD
        self.model_text += "EN"

    def run(self):
        self.finalise()
        with open(self.nec_in, "w") as f:
            f.write(self.model_text)
        with open(os.devnull, "w") as devnull:
            subprocess.run([self.nec_bat], creationflags=subprocess.CREATE_NO_WINDOW)

    def gains(self):
        with open(self.nec_out) as f:
            while "RADIATION PATTERNS" not in f.readline():
                pass
            for _ in range(5):
                l = f.readline()
            if self.verbose:
                print("Gains line:", l.strip())
            return {
                "v_gain": float(l[21:29]),
                "h_gain": float(l[29:37]),
                "total": float(l[37:45]),
            }

    def h_gain(self):
        return self.gains()['h_gain']

    def v_gain(self):
        return self.gains()['v_gain']

    def tot_gain(self):
        return self.gains()['total']

    def vswr(self):
        with open(self.nec_out) as f:
            while "ANTENNA INPUT PARAMETERS" not in f.readline():
                pass
            for _ in range(4):
                l = f.readline()
            if self.verbose:
                print("Z line:", l.strip())
            r = float(l[60:72])
            x = float(l[72:84])
            z_in = r + x * 1j
            z0 = 50
            gamma = (z_in - z0) / (z_in + z0)
            return (1 + abs(gamma)) / (1 - abs(gamma))

