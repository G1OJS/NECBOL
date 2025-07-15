"""
This file is part of the "NECBOL Plain Language Python NEC Runner"
Copyright (c) 2025 Alan Robinson G1OJS

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import numpy as np
import math
import warnings
import subprocess
import os

#=================================================================================
# The geometry object that holds a single component plus its methods
#=================================================================================

class GeometryObject:
    def __init__(self, wires):
        self.wires = wires  # list of wire dicts with iTag, nS, x1, y1, ...
        self.units = units()

    def add_wire(self, iTag, nS, x1, y1, z1, x2, y2, z2, wr):
        self.wires.append({"iTag":iTag, "nS":nS, "a":(x1, y1, z1), "b":(x2, y2, z2), "wr":wr})

    def get_wires(self):
        return self.wires

    def translate(self, **params):
        params_m = self.units.from_suffixed_params(params)
        for w in self.wires:
            w['a'] = tuple(map(float,np.array(w['a']) + np.array([params_m.get('dx_m'), params_m.get('dy_m'), params_m.get('dz_m')])))
            w['b'] = tuple(map(float,np.array(w['b']) + np.array([params_m.get('dx_m'), params_m.get('dy_m'), params_m.get('dz_m')])))

    def rotate_ZtoY(self):
        R = np.array([[1, 0, 0],[0,  0, 1],[0,  -1, 0]])
        return self.rotate(R)
    
    def rotate_ZtoX(self):
        R = np.array([[0, 0, 1],[0,  1, 0],[-1,  0, 0]])
        return self.rotate(R)

    def rotate_around_Z(self, angle_deg):
        ca, sa = self.cos_sin(angle_deg)
        R = np.array([[ca, -sa, 0],
                      [sa, ca, 0],
                      [0, 0, 1]])
        return self.rotate(R)

    def rotate_around_X(self, angle_deg):
        ca, sa = self.cos_sin(angle_deg)
        R = np.array([[1, 0, 0],
                      [0, ca, -sa],
                      [0, sa, ca]])
        return self.rotate(R)

    def rotate_around_Y(self, angle_deg):
        ca, sa = self.cos_sin(angle_deg)
        R = np.array([[ca, 0, sa],
                      [0, 1, 0],
                      [-sa, 0, ca]])
        return self.rotate(R)

    def cos_sin(self,angle_deg):
        angle_rad = math.pi*angle_deg/180
        ca = math.cos(angle_rad)
        sa = math.sin(angle_rad)
        return ca, sa
    
    def rotate(self, R):
        for w in self.wires:
            a = np.array(w['a'])
            b = np.array(w['b'])
            w['a'] = tuple(map(float, R @ a))
            w['b'] = tuple(map(float, R @ b))

    def connect_ends(self, other, tol=1e-3):
        wires_to_add=[]
        for ws in self.wires:
            for es in [ws["a"], ws["b"]]:
                for wo in other.wires:
                    if (self.point_should_connect_to_wire(es,wo['a'],wo['b'],tol)):
                        b = wo["b"]
                        wo['b']=tuple(es)
                        wires_to_add.append( (wo['iTag'], 0, *es, *b, wo['wr']) )
                        break #(for efficiency only)
        for params in wires_to_add:
            other.add_wire(*params)

    def point_should_connect_to_wire(self,P, A, B, tol=1e-6):
        P = np.array(P, dtype=float)
        A = np.array(A, dtype=float)
        B = np.array(B, dtype=float)
        AB = B - A
        AP = P - A
        AB_len = np.linalg.norm(AB)
        # can't connect to a zero length wire using the splitting method
        # but maybe should allow connecting by having the same co-ordinates
        if AB_len == 0:
            return False
        
        # Check perpendicular distance from wire axis
        # if we aren't close enough to the wire axis to need to connect, return false
        # NOTE: need to align tol with nec's check of volumes intersecting
        perp_dist = np.linalg.norm(np.cross(AP, AB)) / AB_len
        if perp_dist > tol: 
            return False    

        # We *are* close enough to the wire axis but if we're not between the ends, return false
        t = np.dot(AP, AB) / (AB_len ** 2)
        if (t<0 or t>1):
            return False
        
        # if we are within 1mm of either end (wires are written to 3dp in m), return false
        if ((np.linalg.norm(AP) < 0.001) or (np.linalg.norm(B-P) < 0.001)):
            return False

        return True

    def point_on_object(self,geom_object, wire_index, alpha_wire):
        if(wire_index> len(geom_object.wires)):
            wire_index = len(geom_object.wires)
            alpha_wire = 1.0
        w = geom_object.wires[wire_index]
        A = np.array(w["a"], dtype=float)
        B = np.array(w["b"], dtype=float)
        P = A + alpha_wire * (B-A)
        return P



#=================================================================================
# Units processor
#=================================================================================

class units:
    
    _UNIT_FACTORS = {
        "m": 1.0,
        "mm": 1000.0,
        "cm": 100.0,
        "in": 39.3701,
        "ft": 3.28084,
    }

    def __init__(self, default_unit: str = "m"):
        if default_unit not in self._UNIT_FACTORS:
            raise ValueError(f"Unsupported unit: {default_unit}")
        self.default_unit = default_unit

    def from_suffixed_params(self, params: dict, whitelist=[]) -> dict:
        """Converts suffixed values like 'd_mm' to meters.

        Output keys have '_m' suffix unless they already end with '_m',
        in which case they are passed through unchanged (assumed meters).
        """
        
        out = {}
        names_seen = []
        for key, value in params.items():
    
            if not isinstance(value, (int, float)):
                continue  # skip nested dicts or other structures

            name = key
            suffix = ""
            if "_" in name:
                name, suffix = name.rsplit("_", 1)
                
            if(name in names_seen):
                warnstr = f"Duplicate value of '{name}' seen: ignoring latest ({key} = {value})"
                warnings.warn(warnstr)
                continue

            names_seen.append(name)

            if suffix in self._UNIT_FACTORS:
                # Convert value, output key with '_m' suffix
                out[name + "_m"] = value / self._UNIT_FACTORS[suffix]
                continue

            if key in whitelist:
                continue
            
            # fallback: no recognised suffix, assume metres
            warnings.warn(f"No recognised units specified for {name}: '{suffix}' specified, metres assumed")
            # output key gets '_m' suffix added
            out[name + "_m"] = value

        return out


#=================================================================================
# NEC Wrapper functions for writing .nec file and reading output
#=================================================================================

class NECModel:
    def __init__(self, working_dir, nec_exe_path, model_name = "Unnamed_Antennna", verbose=False):
        self.verbose = verbose
        self.working_dir = working_dir
        self.nec_exe = nec_exe_path
        self.nec_bat = working_dir + "\\nec.bat"
        self.nec_in = working_dir + "\\" + model_name +  ".nec"
        self.nec_out = working_dir + "\\" + model_name +  ".out"
        self.files_txt = working_dir + "\\files.txt"
        self.model_name = model_name
        self.model_text = ""
        self.LD_WIRECOND = ""
        self.FR_CARD = ""
        self.RP_CARD = ""
        self.GE_CARD = "GE 0\n"
        self.GN_CARD = ""
        self.GM_CARD = ""
        self.comments = ""
        self.EX_TAG = 999
        self.nSegs_per_wavelength = 40
        self.segLength_m = 0
        self.units = units()
        self.write_runner_files()

    def write_runner_files(self):
        for filepath, content in [
            (self.nec_bat, f"{self.nec_exe} < {self.files_txt} \n"),
            (self.files_txt, f"{self.nec_in}\n{self.nec_out}\n")
        ]:
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)  # create directory if it doesn't exist
            try:
                with open(filepath, "w") as f:
                    f.write(content)
            except Exception as e:
                print(f"Error writing file {filepath}: {e}")


    def set_wire_conductivity(self, sigma):
        self.LD_WIRECOND = f"LD 5 0 0 0 {sigma:.6f} \n"

    def set_frequency(self, MHz):
        self.FR_CARD = f"FR 0 1 0 0 {MHz:.3f} 0\n"
        lambda_m = 300/MHz
        self.segLength_m = lambda_m / self.nSegs_per_wavelength
        
    def set_gain_point(self, azimuth, elevation):
        self.RP_CARD = f"RP 0 1 1 1000 {90-elevation:.2f} {azimuth:.2f} 0 0\n"

    def set_gain_az_arc(self, azimuth_start, azimuth_stop, nPoints, elevation):
        if(nPoints<2):
            nPoints=2
        dAz = (azimuth_stop - azimuth_start) / (nPoints-1)
        self.RP_CARD = f"RP 0 1 {nPoints} 1000 {90-elevation:.2f} {azimuth:.2f} 0 {dAz:.2f}\n"

    def set_ground(self, eps_r, sigma, **params):
        """
            Sets the ground relative permitivity and conductivity. Currently limited to simple choices.
            If eps_r = 1, nec is told to use no ground (free space model), and you may omit the origin height parameter
            If you don't call this function, free space will be assumed.
            Othewise you should set the origin height so that the antenna reference point X,Y,Z = (0,0,0) is set to be
            the specified distance above ground.
            Parameters:
                eps_r (float): relative permittivity (relative dielectric constant) of the ground
                sigma (float): conductivity of the ground in mhos/meter
                origin_height_{units_string} (float): Height of antenna reference point X,Y,Z = (0,0,0)
        """
        if eps_r == 1.0:
            self.GE_CARD = "GE 0\n"
            self.GN_CARD = ""
            self.GM_CARD = "GM 0 0 0 0 0 0 0 0.000\n"
        else:
            origin_height_m = self.units.from_suffixed_params(params)['origin_height_m']
            self.GE_CARD = "GE -1\n"
            self.GN_CARD = f"GN 2 0 0 0 {eps_r:.3f} {sigma:.3f} \n"
            self.GM_CARD = f"GM 0 0 0 0 0 0 0 {origin_height_m:.3f}\n"

    def start_geometry(self, comments="No comments specified"):
        # effectively *resets* the model, except that all of the parameters
        # set by set_ functions are still incorporated when the file is written
        self.comments = comments
        self.model_text = "CM " + comments + "\nCE\n"
        # TO DO: decide if 500 is the right tag to start at, and whether to limit # of loads
        self.LOAD_iTag = 500
        self.LOADS = []

    def place_series_RLC_load(self, geomObj, R_ohms, L_uH, C_pf, load_alpha_object=-1, load_wire_index=-1, load_alpha_wire=-1):
        """
            inserts a single segment containing a series RLC load into an existing geometry object
            see _place_feed_or_load for how to specify the position of the segment within the object
        """
        self.LOADS.append(f"LD 0 {self.LOAD_iTag} 0 0 {R_ohms} {L_uH * 1e-6} {C_pf * 1e-12}\n")
        self._place_feed_or_load(geomObj, self.LOAD_iTag, load_alpha_object, load_wire_index, load_alpha_wire)
        self.LOAD_iTag +=1
        
    def place_parallel_RLC_load(self, geomObj, R_ohms, L_uH, C_pf, load_alpha_object=-1, load_wire_index=-1, load_alpha_wire=-1):
        """
            inserts a single segment containing a parakllel RLC load into an existing geometry object
            see _place_feed_or_load for how to specify the position of the segment within the object
        """
        self.LOADS.append(f"LD 1 {self.LOAD_iTag} 0 0 {R_ohms} {L_uH * 1e-6} {C_pf * 1e-12}\n")
        self._place_feed_or_load(geomObj, self.LOAD_iTag, load_alpha_object, load_wire_index, load_alpha_wire)
        self.LOAD_iTag +=1

    def place_feed(self,  geomObj, feed_alpha_object=-1, feed_wire_index=-1, feed_alpha_wire=-1):
        """
            inserts a single segment containing the excitation point into an existing geometry object
            see _place_feed_or_load for how to specify the position of the segment within the object
        """
        self._place_feed_or_load(geomObj, self.EX_TAG, feed_alpha_object, feed_wire_index, feed_alpha_wire)

    def _place_feed_or_load(self, geomObj, item_iTag, item_alpha_object, item_wire_index, item_alpha_wire):
        """
            inserts a single segment with a specified iTag into an existing geometry object
            position within the object is specied as
            EITHER:
              item_alpha_object (range 0 to 1) as a parameter specifying the length of
                                wire traversed to reach the item by following each wire in the object,
                                divided by the length of all wires in the object
            OR:
              item_wire_index AND item_alpha_wire
              which specify the i'th wire in the n wires in the object, and the distance along that
              wire divided by that wire's length
        """
        wires = geomObj.get_wires()
        if(item_alpha_object >=0):
            item_wire_index = min(len(wires)-1,int(item_alpha_object*len(wires))) # 0 to nWires -1
            item_alpha_wire = item_alpha_object - item_wire_index
        w = wires[item_wire_index]       

        # calculate wire length vector AB, length a to b and distance from a to feed point
        A = np.array(w["a"], dtype=float)
        B = np.array(w["b"], dtype=float)
        AB = B-A
        wLen = np.linalg.norm(AB)
        feedDist = wLen * item_alpha_wire

        if (wLen <= self.segLength_m):
            # feed segment is all of this wire, so no need to split
            w['nS'] = 1
            w['iTag'] = item_iTag
        else:
            # split the wire AB into three wires: A to C, CD (feed segment), D to B
            nS1 = int(feedDist / self.segLength_m)              # no need for min of 1 as we always have the feed segment
            C = A + AB * (nS1 * self.segLength_m) / wLen        # feed segment end a
            D = A + AB * ((nS1+1) * self.segLength_m) / wLen    # feed segment end b
            nS2 = int((wLen-feedDist) / self.segLength_m)       # no need for min of 1 as we always have the feed segment
            # write results back to geomObj: modify existing wire to end at C, add feed segment CD and final wire DB
            # (nonzero nS field is preserved during segmentation in 'add')
            w['b'] = tuple(C)
            w['nS'] = nS1
            geomObj.add_wire(item_iTag , 1, *C, *D, w["wr"])
            geomObj.add_wire(w["iTag"] , nS2, *D, *B, w["wr"])
                
    def add(self, geomObj):
        for w in geomObj.get_wires():
            A = np.array(w["a"], dtype=float)
            B = np.array(w["b"], dtype=float)
            if(w['nS'] == 0): # preserve pre-calculated segments
                w['nS'] = 1+int(np.linalg.norm(B-A) / self.segLength_m)
            self.model_text += f"GW {w['iTag']} {w['nS']} "
            for v in A:
                self.model_text += f"{v:.3f} "
            for v in B:
                self.model_text += f"{v:.3f} "
            self.model_text += f"{w['wr']}\n"

    def finalise(self):
        self.model_text += self.GM_CARD
        self.model_text += self.GE_CARD
        self.model_text += self.GN_CARD
        self.model_text += "EK\n"
        self.model_text += self.LD_WIRECOND
        for LD in self.LOADS:
            self.model_text += LD
        self.model_text += f"EX 0 {self.EX_TAG} 1 0 1 0\n"
        self.model_text += self.FR_CARD
        self.model_text += self.RP_CARD
        self.model_text += "EN"

    def write_nec(self):
        self.finalise()
        with open(self.nec_in, "w") as f:
            f.write(self.model_text)

    def run_nec(self):
        subprocess.run([self.nec_bat], creationflags=subprocess.CREATE_NO_WINDOW)

    def gains(self):
        try:
            with open(self.nec_out) as f:
                while "RADIATION PATTERNS" not in f.readline():
                    pass
                for _ in range(5):
                    l = f.readline()
                if self.verbose:
                    print("Gains line:", l.strip())
        except (RuntimeError, ValueError):
            raise ValueError(f"Something went wrong reading gains from {nec_out}")

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
        try:
            with open(self.nec_out) as f:
                while "ANTENNA INPUT PARAMETERS" not in f.readline():
                    pass
                for _ in range(4):
                    l = f.readline()
                if self.verbose:
                    print("Z line:", l.strip())
                r = float(l[60:72])
                x = float(l[72:84])
        except (RuntimeError, ValueError):
            raise ValueError(f"Something went wrong reading input impedance from {nec_out}")

        z_in = r + x * 1j
        z0 = 50
        gamma = (z_in - z0) / (z_in + z0)
        return (1 + abs(gamma)) / (1 - abs(gamma))


