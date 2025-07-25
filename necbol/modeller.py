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
        self.nSegs_per_wavelength = 40
        self.segLength_m = 0
        self._units = _units()
        self.default_wire_sigma = None
        self.MHz = None
        self.MHz_stop = None
        self.MHz_step = None
        self.origin_height_m = 0
        self.segLength_m
        self.el_datum_deg = 0
        self.az_datum_deg = 0
        self.az_step_deg = 10
        self.el_step_deg = 5
        self.ground_sigma = 0
        self.ground_Er = 1.0
        self.geometry = []
        self.EX_tag = 999
        self.LOADS = []
        self.LOADS_start_tag = 8000
        self.max_total_gain = None
        self.vswr = None

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
            Set wire conductivity to be assumed for all wires that don't have an explicitly-set load.
        """
        self.default_wire_sigma = sigma
        self.LD_WIRECOND = f"LD 5 0 0 0 {sigma:.6f} \n"

    def set_frequency(self, MHz):
        """
            Request NEC to perform all analysis at the specified frequency. 
        """
        self.MHz = MHz
        lambda_m = 300/MHz
        self.segLength_m = lambda_m / self.nSegs_per_wavelength

    def set_gain_point(self, azimuth_deg, elevation_deg):
        """
            Set the azimuth and elevation of a single gain point that
            must appear in the output radiation pattern
        """
        self.az_datum_deg = azimuth_deg
        self.el_datum_deg = elevation_deg


    def set_angular_resolution(self, az_step_deg, el_step_deg):
        """
            Set resolution required in az and el in degrees
            If a ground is specified, NEC will be asked for a hemisphere, otherwise a sphere
        """
        self.az_step_deg = az_step_deg
        self.el_step_deg = el_step_deg

    def set_ground(self, eps_r, sigma, **origin_height):
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
        self.ground_Er = eps_r
        self.ground_sigma = sigma
        if(eps_r >1.0):
            self.origin_height_m = self._units._from_suffixed_dimensions(origin_height)['origin_height_m']
            if(self.el_datum_deg <= 0):
                self.el_datum_deg = 1

    def place_RLC_load(self, geomObj, R_Ohms, L_uH, C_pf, load_type = 'series', load_alpha_object=-1, load_wire_index=-1, load_alpha_wire=-1):
        """
            inserts a single segment containing an RLC load into an existing geometry object
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

            NEC LD card specification: https://www.nec2.org/part_3/cards/ld.html
        """

        iTag = self.LOADS_start_tag + len(self.LOADS)
        self.LOADS.append({'iTag': iTag, 'load_type': load_type, 'RoLuCp': (R_Ohms, L_uH, C_pf), 'alpha': None})
        self._insert_special_segment(geomObj, iTag, load_alpha_object, load_wire_index, load_alpha_wire)

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
        self._insert_special_segment(geomObj, self.EX_tag, feed_alpha_object, feed_wire_index, feed_alpha_wire)
   
    def add(self, geomObj):
        """
            Add a completed component to the specified model: model_name.add(component_name). Any changes made
            to the component after this point are ignored.
        """
        self.geometry.append(geomObj)

    def write_nec(self):
        """
            Write the entire model to the NEC input file ready for analysis. At this point, the function
            "show_wires_from_file" may be used to see the specified geometry in a 3D view.
        """
        self._write_runner_files()
        
        # open the .nec file
        with open(self.nec_in, "w") as f:
            f.write("CM\nCE\n")
            
            # 1. Write GW lines for all geometry
            for geomObj in self.geometry:
                for w in geomObj._get_wires():
                    A = np.array(w["a"], dtype=float)
                    B = np.array(w["b"], dtype=float)
                    if(w['nS'] == 0): # calculate and update number of segments only if not already present
                        w['nS'] = 1+int(np.linalg.norm(B-A) / self.segLength_m)
                    f.write(f"GW {w['iTag']} {w['nS']} ")
                    f.write(' '.join([f"{A[i]:.3f} " for i in range(3)]))
                    f.write(' '.join([f"{B[i]:.3f} " for i in range(3)]))
                    f.write(f" {w['wr']}\n")

            # 2. Write GE card, Ground Card, and GM card to set origin height
            if self.ground_Er == 1.0:
                f.write("GE 0\n")
            else:
                f.write(f"GM 0 0 0 0 0 0 0 {self.origin_height_m:.3f}\n")
                f.write("GE -1\n")
                f.write(f"GN 2 0 0 0 {self.ground_Er:.3f} {self.ground_sigma:.3f} \n")

            # 3. Write out the loads
            for LD in self.LOADS:
                LDTYP = ['series','parallel','series_per_metre','parallel_per_metre','impedance_not_used','conductivity'].index(LD['load_type'])
                LDTAG = LD['iTag']
                R_Ohms, L_uH , C_pF = LD['RoLuCp']
                # these strings are set programatically so shouldn't need an error trap
                f.write(f"LD {LDTAG} {LDTYP} 0 0 {R_Ohms} {L_uH * 1e-6} {C_pF * 1e-12}\n")

            # 4. Feed
            f.write(f"EX 0 {self.EX_tag} 1 0 1 0\n")

            # 5. Frequency
            # update to include sweep
            f.write(f"FR 0 1 0 0 {self.MHz:.3f} 0\n")

            # 6. Pattern points
            # Need to update logic to set nTheta to 1 if fsweep 
            n_phi = 1 + int(360 / self.az_step_deg)
            d_phi = 360 / (n_phi - 1)
            phi_start_deg = self.az_datum_deg
            if self.ground_Er == 1.0:  # free space, no ground card, full sphere is appropriate
                theta_start_deg, d_theta, n_theta = self._set_theta_grid_from_el_datum(self.el_datum_deg, self.el_step_deg, hemisphere = False)
                f.write(f"RP 0 {n_theta} {n_phi} 1003 {theta_start_deg} {phi_start_deg} {d_theta} {d_phi}\n")
            else:                       # ground exists, upper hemisphere is appropriate
                theta_start_deg, d_theta, n_theta = self._set_theta_grid_from_el_datum(self.el_datum_deg, self.el_step_deg, hemisphere = True)
                f.write(f"RP 0 {n_theta} {n_phi} 1003 {theta_start_deg} {phi_start_deg} {d_theta} {d_phi}\n")
                
            f.write("EN")

    def run_nec(self):
        """
            Pass the model file to NEC for analysis and wait for the output.
        """
        
        subprocess.run([self.nec_bat], creationflags=subprocess.CREATE_NO_WINDOW)


#===============================================================
# internal functions for class NECModel
#===============================================================


    def _set_frequency_sweep(self, MHz, MHz_stop, MHz_step):
        """
            Set parameters for frequency sweep. This also sets the angular pattern resolution
            to 10 degrees in azimuth and elevation to limit the size of output files           
        """
        self.MHz_stop = MHz_stop
        self.MHz_step = MHz_step
        self.MHz = MHz
        lambda_m = 300/MHz_stop
        self.segLength_m = lambda_m / self.nSegs_per_wavelength
        self.set_angular_resolution(10,10)


    def _set_theta_grid_from_el_datum(self, el_datum_deg, el_step_deg, hemisphere = True):
        theta_datum = 90 - el_datum_deg
        d_theta = el_step_deg
        theta_range = 90 if hemisphere else 180

        theta_start = theta_datum % d_theta
        # Fix float errors (e.g. 0.0000001)
        theta_start = round(theta_start, 6)

        # Clip to max range
        max_theta = theta_start + d_theta * (int((theta_range - theta_start) / d_theta))
        n_theta = 1 + int((max_theta - theta_start) / d_theta)
        return theta_start, d_theta, n_theta

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

    def _insert_special_segment(self, geomObj, item_iTag, item_alpha_object, item_wire_index, item_alpha_wire):
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
        """
        ca, sa = self._cos_sin(angle_deg)
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

    def _from_suffixed_dimensions(self, params: dict, whitelist=[]) -> dict:
        """Converts suffixed values like 'd_mm' to meters.

        Output keys have '_m' suffix unless they already end with '_m',
        in which case they are passed through unchanged (assumed meters).
        """

        _UNIT_FACTORS = {
        "m": 1.0,
        "mm": 1000.0,
        "cm": 100.0,
        "in": 39.3701,
        "ft": 3.28084,
        }

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

            if suffix in _UNIT_FACTORS:
                # Convert value, output key with '_m' suffix
                out[name + "_m"] = value / _UNIT_FACTORS[suffix]
                continue

            if key in whitelist:
                continue
            
            # fallback: no recognised suffix, assume metres
            warnings.warn(f"No recognised units specified for {name}: '{suffix}' specified, metres assumed")
            # output key gets '_m' suffix added
            out[name + "_m"] = value

        return out



