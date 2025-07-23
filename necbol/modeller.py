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
        self._units = _units()

    def translate(self, **params):
        """
            Translate an object by dx, dy, dz
            Arguments are dx_{units}, dy_{units}, dz_{units}
        """
        params_m = self._units._from_suffixed_dimensions(params)
        for w in self.wires:
            w['a'] = tuple(map(float,np.array(w['a']) + np.array([params_m.get('dx_m'), params_m.get('dy_m'), params_m.get('dz_m')])))
            w['b'] = tuple(map(float,np.array(w['b']) + np.array([params_m.get('dx_m'), params_m.get('dy_m'), params_m.get('dz_m')])))

    def rotate_ZtoY(self):
        """
            Rotate the object through 90 degrees around X
        """
        R = np.array([[1, 0, 0],[0,  0, 1],[0,  -1, 0]])
        return self._rotate(R)
    
    def rotate_ZtoX(self):
        """
            Rotate the object through 90 degrees around Y
        """
        R = np.array([[0, 0, 1],[0,  1, 0],[-1,  0, 0]])
        return self._rotate(R)

    def rotate_around_X(self, angle_deg):
        """
            Rotate the object through angle_deg degrees around X
        """
        ca, sa = self._cos_sin(angle_deg)
        R = np.array([[1, 0, 0],
                      [0, ca, -sa],
                      [0, sa, ca]])
        return self._rotate(R)

    def rotate_around_Y(self, angle_deg):
        """
            Rotate the object through angle_deg degrees around Y
        """        ca, sa = self._cos_sin(angle_deg)
        R = np.array([[ca, 0, sa],
                      [0, 1, 0],
                      [-sa, 0, ca]])
        return self._rotate(R)

    def rotate_around_Z(self, angle_deg):
        """
            Rotate the object through angle_deg degrees around Z
        """
        ca, sa = self._cos_sin(angle_deg)
        R = np.array([[ca, -sa, 0],
                      [sa, ca, 0],
                      [0, 0, 1]])
        return self._rotate(R)

    def connect_ends(self, other, tol=1e-3, verbose = False):
        """
            Check both ends of the wire to see if they lie on any wires in the specified object,
            and if so, split the wires of the specified object so that NEC considers them to be
            a valid T junction. Usage is:

            wire.connect_ends(object, [tol in m], [verbose])

            if verbose is True, details of the wire connection(s) are printed
        """
        ca, sa = self._cos_sin(angle_deg)
        R = np.array([[ca, -sa, 0],
                      [sa, ca, 0],
                      [0, 0, 1]])
        return self._rotate(R)
        wires_to_add=[]
        for ws in self.wires:
            if(verbose):
                print(f"\nChecking if ends of wire from {ws['a']} to {ws['b']} should connect to any of {len(other.wires)} other wires:")
            for es in [ws["a"], ws["b"]]:
                for wo in other.wires:
                    if (self._point_should_connect_to_wire(es,wo,tol)):
                        wire_seg_status = f"{wo['nS']} segment" if wo['nS'] > 0 else 'unsegmented'
                        length_orig = np.linalg.norm(np.array(wo["a"]) - np.array(wo["b"]))
                        b_orig = wo["b"]
                        wo['b']=tuple(es)
                        length_shortened = np.linalg.norm(np.array(wo["a"]) - np.array(wo["b"]))
                        nS_shortened = max(1, int(wo['nS']*length_shortened/length_orig))
                        nS_orig = wo['nS']
                        wo['nS'] = nS_shortened
                        nS_remainder = max(1,nS_orig - nS_shortened)
                        wires_to_add.append( (wo['iTag'], nS_remainder, *wo['b'], *b_orig, wo['wr']) )
                        length_remainder = np.linalg.norm(np.array(wo["b"]) - np.array(b_orig))
                        if(verbose):
                            print(f"Inserting end of wire at {wo['b']} into {wire_seg_status} wire {length_orig}m wire from {wo['a']} to {b_orig}:")
                            print(f"    by shortening wire to end at {wo['b']}: {length_shortened}m, using {nS_shortened} segments")
                            print(f"    and adding wire from {wo["b"]} to {b_orig}:  {length_remainder}m using {nS_remainder} segments")
                        break #(for efficiency only)
        for params in wires_to_add:
            other._add_wire(*params)

#===============================================================
# internal functions for class GeometryObject
#===============================================================

    def _cos_sin(self,angle_deg):
        angle_rad = math.pi*angle_deg/180
        ca = math.cos(angle_rad)
        sa = math.sin(angle_rad)
        return ca, sa
    
    def _rotate(self, R):
        for w in self.wires:
            a = np.array(w['a'])
            b = np.array(w['b'])
            w['a'] = tuple(map(float, R @ a))
            w['b'] = tuple(map(float, R @ b))

    def _add_wire(self, iTag, nS, x1, y1, z1, x2, y2, z2, wr):
        self.wires.append({"iTag":iTag, "nS":nS, "a":(x1, y1, z1), "b":(x2, y2, z2), "wr":wr})

    def _get_wires(self):
        return self.wires

    def _point_should_connect_to_wire(self,P, wire, tol=1e-3):
        P = np.array(P, dtype=float)
        A = np.array(wire['a'], dtype=float)
        B = np.array(wire['b'], dtype=float)
        AB = B - A
        AP = P - A
        AB_len = np.linalg.norm(AB)
        # can't connect to a zero length wire using the splitting method
        if AB_len == 0:
            return False
        
        # Check perpendicular distance from wire axis
        # if we aren't close enough to the wire axis to need to connect, return false
        # NOTE: need to align tol with nec's check of volumes intersecting
        perp_dist = np.linalg.norm(np.cross(AP, AB)) / AB_len
        if perp_dist > tol: 
            return False    

        # Project point onto the wire to get fractional position
        alpha = np.dot(AP, AB) / (AB_len**2)
        if not (0 <= alpha <= 1):
            return False  # point is on the wire axis but not between the wire ends

        # If we are within allowable tolerance of the wire ends, don't split the wire
        dist_from_end = min(alpha*AB_len, (1-alpha)*AB_len)
        if (dist_from_end < tol):
            return False

        # IF the wire is already segmented (e.g. in a grid), check how far from the
        # *nearest* segment boundary this projected alpha is
        if(wire['nS']>0):
            segment_pitch = 1 / wire['nS']
            nearest_alpha = round(alpha / segment_pitch) * segment_pitch
            alpha_dist = abs(alpha - nearest_alpha)
            alpha_tol = tol / AB_len  # convert spatial tol to alpha-space
            if alpha_dist < alpha_tol:
                return False  # near a segment end — NEC will handle this as a normal junction

        return True  # wire needs to be split to allow the connection

    def _point_on_object(self,geom_object, wire_index, alpha_wire):
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

class _units:
    
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

    def _from_suffixed_dimensions(self, params: dict, whitelist=[]) -> dict:
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
        self._units = _units()
        self._write_runner_files()

    def set_name(self, name):
        """
            Set the name of the model. This is used in NEC input file generation and is reflected in the NEC
            output file name. It is permissible to use this function to re-set the name after a NEC run has completed,
            so that the analysis continues (with updated input parameters) and outputs more than one test case
        """
        self.model_name = name
        self.nec_in = self.working_dir + "\\" + self.model_name +  ".nec"
        self.nec_out = self.working_dir + "\\" + self.model_name +  ".out"
        self._write_runner_files()

    def set_wire_conductivity(self, sigma):
        """
            Set wire conductivity for all wires.

            NOTE that NEC achieves this by specifying a 'load' applicable to all wires, and addition
            of further loads will interact with this. A future version of necbol will examine
            this specification so that both wire conductivity and load parameters are accounted for in this case.
        """
        self.LD_WIRECOND = f"LD 5 0 0 0 {sigma:.6f} \n"

    def set_frequency(self, MHz):
        """
            Request NEC to perform all analysis at the specified frequency. 
        """
        self.FR_CARD = f"FR 0 1 0 0 {MHz:.3f} 0\n"
        lambda_m = 300/MHz
        self.segLength_m = lambda_m / self.nSegs_per_wavelength
        
    def set_gain_point(self, azimuth, elevation):
        """
            Request NEC to produce a gain pattern at a single specified azimuth and elevation
            (Typically used when optimising gain in a fixed direction)
        """
        self.RP_CARD = f"RP 0 1 1 1000 {90-elevation:.2f} {azimuth:.2f} 0 0\n"

    def set_gain_az_arc(self, azimuth_start, azimuth_stop, nPoints, elevation):
        """
            Request NEC to produce a gain pattern over a specified azimuth
            range at a single elevation using nPoints points
        """
        if(nPoints<2):
            nPoints=2
        dAz = (azimuth_stop - azimuth_start) / (nPoints-1)
        self.RP_CARD = f"RP 0 1 {nPoints} 1000 {90-elevation:.2f} {azimuth_start:.2f} 0 {dAz:.2f}\n"

    def set_gain_sphere_1deg(self):
        """
            Request NEC to produce a full sphere's worth of data points,
            using 1 degree steps in both azimuth and elevation
        """
        self.RP_CARD = "RP 0 361 361 1003 -180 0 1 1\n"

    def set_gain_hemisphere_1deg(self):
        """
            Request NEC to produce a full half-sphere's worth of data points covering the 'above ground' half space,
            using 1 degree steps in both azimuth and elevation
        """
        self.RP_CARD = "RP 0 181 361 1003 -180 0 1 1\n"

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
            origin_height_m = self._units._from_suffixed_dimensions(params)['origin_height_m']
            self.GE_CARD = "GE -1\n"
            self.GN_CARD = f"GN 2 0 0 0 {eps_r:.3f} {sigma:.3f} \n"
            self.GM_CARD = f"GM 0 0 0 0 0 0 0 {origin_height_m:.3f}\n"

    def start_geometry(self, comments="No comments specified"):
        """
            Effectively *resets* the model by deleting all wires, feed and loads.
            All of the parameters set by "set_" functions are still incorporated when the file is written
        """
        self.comments = comments
        self.model_text = "CM " + comments + "\nCE\n"
        # TO DO: decide if 500 is the right tag to start at, and whether to limit # of loads
        self.LOAD_iTag = 500
        self.LOADS = []

    def place_series_RLC_load(self, geomObj, R_ohms, L_uH, C_pf, load_alpha_object=-1, load_wire_index=-1, load_alpha_wire=-1):
        """
            inserts a single segment containing a series RLC load into an existing geometry object
            Position within the object is specied as
            EITHER:
              load_alpha_object (range 0 to 1) as a parameter specifying the length of
                                wire traversed to reach the item by following each wire in the object,
                                divided by the length of all wires in the object
                                (This is intended to be used for objects like circular loops where there
                                are many short wires each of the same length)
            OR:
              load_wire_index AND load_alpha_wire
              which specify the i'th wire (0 to n-1) in the n wires in the object, and the distance along that
              wire divided by that wire's length
        """
        self.LOADS.append(f"LD 0 {self.LOAD_iTag} 0 0 {R_ohms} {L_uH * 1e-6} {C_pf * 1e-12}\n")
        self._place_feed_or_load(geomObj, self.LOAD_iTag, load_alpha_object, load_wire_index, load_alpha_wire)
        self.LOAD_iTag +=1
        
    def place_parallel_RLC_load(self, geomObj, R_ohms, L_uH, C_pf, load_alpha_object=-1, load_wire_index=-1, load_alpha_wire=-1):
        """
            inserts a single segment containing a parallel RLC load into an existing geometry object
            Position within the object is specied as
            EITHER:
              load_alpha_object (range 0 to 1) as a parameter specifying the length of
                                wire traversed to reach the item by following each wire in the object,
                                divided by the length of all wires in the object
                                (This is intended to be used for objects like circular loops where there
                                are many short wires each of the same length)
            OR:
              load_wire_index AND load_alpha_wire
              which specify the i'th wire (0 to n-1) in the n wires in the object, and the distance along that
              wire divided by that wire's length
        """
        self.LOADS.append(f"LD 1 {self.LOAD_iTag} 0 0 {R_ohms} {L_uH * 1e-6} {C_pf * 1e-12}\n")
        self._place_feed_or_load(geomObj, self.LOAD_iTag, load_alpha_object, load_wire_index, load_alpha_wire)
        self.LOAD_iTag +=1

    def place_feed(self,  geomObj, feed_alpha_object=-1, feed_wire_index=-1, feed_alpha_wire=-1):
        """
            Inserts a single segment containing the excitation point into an existing geometry object.
            Position within the object is specied as
            EITHER:
              feed_alpha_object (range 0 to 1) as a parameter specifying the length of
                                wire traversed to reach the item by following each wire in the object,
                                divided by the length of all wires in the object
                                (This is intended to be used for objects like circular loops where there
                                are many short wires each of the same length)
            OR:
              feed_wire_index AND feed_alpha_wire
              which specify the i'th wire (0 to n-1) in the n wires in the object, and the distance along that
              wire divided by that wire's length
        """
        self._place_feed_or_load(geomObj, self.EX_TAG, feed_alpha_object, feed_wire_index, feed_alpha_wire)

                
    def add(self, geomObj):
        """
            Add a completed component to the specified model: model_name.add(component_name). Any changes made
            to the component after this point are ignored.
        """
        for w in geomObj._get_wires():
            A = np.array(w["a"], dtype=float)
            B = np.array(w["b"], dtype=float)
            if(w['nS'] == 0): # calculate and update number of segments only if not already present
                w['nS'] = 1+int(np.linalg.norm(B-A) / self.segLength_m)
            self.model_text += f"GW {w['iTag']} {w['nS']} "
            for v in A:
                self.model_text += f"{v:.3f} "
            for v in B:
                self.model_text += f"{v:.3f} "
            self.model_text += f"{w['wr']}\n"


    def write_nec(self):
        """
            Write the entire model to the NEC input file ready for analysis. At this point, the function
            "show_wires_from_file" may be used to see the specified geometry in a 3D view.
        """
        tail_text = self.GM_CARD
        tail_text += self.GE_CARD
        tail_text += self.GN_CARD
        tail_text += "EK\n"
        tail_text += self.LD_WIRECOND
        for LD in self.LOADS:
            tail_text += LD
        tail_text += f"EX 0 {self.EX_TAG} 1 0 1 0\n"
        tail_text += self.FR_CARD
        tail_text += self.RP_CARD
        tail_text += "EN"
        with open(self.nec_in, "w") as f:
            f.write(self.model_text + tail_text)

    def run_nec(self):
        """
            Pass the model file to NEC for analysis and wait for the output.
        """
        subprocess.run([self.nec_bat], creationflags=subprocess.CREATE_NO_WINDOW)

    def h_gain(self):
        """
            Return the horizontal polarisation gain at the specified single gain point
        """
        return self._get_single_point_gains()['h_gain']

    def v_gain(self):
        """
            Return the vertical polarisation gain at the specified single gain point
        """
        return self._get_single_point_gains()['v_gain']

    def tot_gain(self):
        """
            Return the total gain at the specified single gain point
        """
        return self._get_single_point_gains()['total']

    def vswr(self, Z0 = 50):
        """
            Return the antenna VSWR at the feed point assuming a 50 ohm system
            Or another value if specified
        """
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
        gamma = (z_in - Z0) / (z_in + Z0)
        return (1 + abs(gamma)) / (1 - abs(gamma))

    def read_radiation_pattern(self):
        """
            read the radiation pattern from the model.nec_out file
            into a list of dictionaries with format:
                {'theta': theta,
                'phi': phi,
                'gain_vert_db': gain_vert,
                'gain_horz_db': gain_horz,
                'gain_total_db': gain_total,
                'axial_ratio': axial_ratio,
                'tilt_deg': tilt_deg,
                'sense': sense,
                'E_theta_mag': e_theta_mag,
                'E_theta_phase_deg': e_theta_phase,
                'E_phi_mag': e_phi_mag,
                'E_phi_phase_deg': e_phi_phase}
                
        """

        return _read_radiation_pattern(self.nec_out)

#===============================================================
# internal functions for class NECModel
#===============================================================
    def _get_single_point_gains(self):
        # this will be refactored to call _read_radiation_pattern
        # and store the result, so that if it is called again
        # the read is not needed
        # Also, either using interpolation or aligning a cut / sphere with the
        # needed point may provide efficiencies (and maintainability, more importantly)
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


    def _write_runner_files(self):
        """
            Write the .bat file to start NEC, and 'files.txt' to tell NEC the name of the input and output files
        """
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

    def _place_feed_or_load(self, geomObj, item_iTag, item_alpha_object, item_wire_index, item_alpha_wire):
        """
            inserts a single segment with a specified iTag into an existing geometry object
            position within the object is specied as either item_alpha_object or item_wire_index, item_alpha_wire
            (see calling functions for more details)
        """
        wires = geomObj._get_wires()
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
            geomObj._add_wire(item_iTag , 1, *C, *D, w["wr"])
            geomObj._add_wire(w["iTag"] , nS2, *D, *B, w["wr"])
            

def _read_radiation_pattern(filepath):        
    data = []
    in_data = False
    start_lineNo = 1e9
    with open(filepath) as f:
        lines = f.readlines()
    for lineNo, line in enumerate(lines):
        if ('RADIATION PATTERNS' in line):
            in_data = True
            start_lineNo = lineNo + 5

        if (lineNo > start_lineNo and line=="\n"):
            in_data = False
            
        if (in_data and lineNo >= start_lineNo):
            theta = float(line[0:9])
            phi = float(line[9:18])
            gain_vert = float(line[18:28])
            gain_horz = float(line[28:36])
            gain_total = float(line[36:45])
            axial_ratio = float(line[45:55])
            tilt_deg = float(line[55:63])
            # SENSE is a string (LINEAR, LHCP, RHCP, etc.)
            sense = line[63:72].strip()
            e_theta_mag = float(line[72:87])
            e_theta_phase = float(line[87:96])
            e_phi_mag = float(line[96:111])
            e_phi_phase = float(line[111:119])

            data.append({
                'theta': theta,
                'phi': phi,
                'gain_vert_db': gain_vert,
                'gain_horz_db': gain_horz,
                'gain_total_db': gain_total,
                'axial_ratio': axial_ratio,
                'tilt_deg': tilt_deg,
                'sense': sense,
                'E_theta_mag': e_theta_mag,
                'E_theta_phase_deg': e_theta_phase,
                'E_phi_mag': e_phi_mag,
                'E_phi_phase_deg': e_phi_phase
            })


    return data


