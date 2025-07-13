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
from necbol.units import units

#=================================================================================
# Cannonical components
#=================================================================================

class components:
    def __init__(self, starting_tag_nr = 0):
        """Sets object_counter to starting_tag_nr (tags number identifies an object)
        and loads the units module class units()"""
        self.object_counter = starting_tag_nr
        self.units = units()

    def new_geometry_object(self):
        """increment the object counter and return a GeometryObject with the counter's new value """
        self.object_counter += 1
        iTag = self.object_counter
        return iTag, GeometryObject([])

    def copy_of(self, existing_obj):
        """Returns a clone of existing_obj with a new iTag """
        iTag, obj = self.new_geometry_object()
        for w in existing_obj.wires:
            obj.add_wire(iTag, w['nS'], *w['a'], *w['b'], w['wr'])
        return obj
        
    def wire_Z(self, **params):
        """
        Create a straight wire aligned along the Z-axis, centered at the origin.

        The wire extends from -length/2 to +length/2 on the Z-axis, with the specified diameter.

        Parameters:
            length_{units_string} (float): Length of the wire. 
            wire_diameter_{units_string} (float): Diameter of the wire.
            In each case, the unit suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wire.
        """
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params)
        half_length_m = params_m.get('length_m')/2
        wire_radius_m = params_m.get('wire_diameter_m')/2
        obj.add_wire(iTag, 0, 0, 0, -half_length_m, 0, 0, half_length_m, wire_radius_m)
        return obj
    
    def rect_loop_XZ(self, **params):
        """
        Create a rectangular wire loop in the XZ plane, centered at the origin, with the specified wire diameter.
        The 'side' wires extend from Z=-length/2 to Z=+length/2 at X = +/- width/2.
        The 'top/bottom' wires extend from X=-width/2 to X=+width/2 at Z = +/- length/2.
        Parameters:
            length_{units_string} (float): 'Length' (extension along Z) of the rectangle. 
            width_{units_string} (float): 'Width' (extension along X) of the rectangle. 
            wire_diameter_{units_string} (float): Diameter of the wires.
            In each case, the unit suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wires.
        """
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params)
        half_length_m = params_m.get('length_m')/2
        half_width_m = params_m.get('width_m')/2
        wire_radius_m = params_m.get('wire_diameter_m')/2        
        obj.add_wire(iTag, 0, -half_width_m , 0, -half_length_m, -half_width_m , 0, half_length_m, wire_radius_m)
        obj.add_wire(iTag, 0,  half_width_m , 0, -half_length_m,  half_width_m , 0, half_length_m, wire_radius_m)
        obj.add_wire(iTag, 0, -half_width_m , 0, -half_length_m,  half_width_m , 0,-half_length_m, wire_radius_m)
        obj.add_wire(iTag, 0, -half_width_m , 0,  half_length_m,  half_width_m , 0, half_length_m, wire_radius_m)
        return obj

    def connector(self, from_object, from_wire_index, from_alpha_wire, to_object, to_wire_index, to_alpha_wire,  wire_diameter_mm = 1.0):
        """
        Create a single wire from a specified point on the from_object to a specified point on the to_object.
        The point on an object is specified as {ftom|to}_wire_index AND {ftom|to}_alpha_wire, which specify respectively:
              the i'th wire in the n wires in the object, and
              the distance along that wire divided by that wire's length
        Parameters:
            from_object (GeometryObject), from_wire_index (int, 0 .. n_wires_in_from_object - 1), from_alpha_wire (float, 0 .. 1)
            to_object (GeometryObject), to_wire_index (int, 0 .. n_wires_in_to_object - 1), to_alpha_wire (float, 0 .. 1)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wire.
        """
        iTag, obj = self.new_geometry_object()
        from_point = _point_on_object(from_object, from_wire_index, from_alpha_wire)
        to_point = _point_on_object(to_object, to_wire_index, to_alpha_wire)
        obj.add_wire(iTag, 0, *from_point, *to_point, wire_diameter_mm/2000) 
        return obj

    def helix(self, **params):
        """
        Create a single helix with axis = Z axis
        Parameters:
            radius_{units} (float) - helix radius 
            length_{units} (float) - helix length along Z 
            pitch_{units} (float)  - helix length along Z per whole turn
            wire_diameter_{units} (float) - diameter of wire making the helix
            In each case above, the units suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
            wires_per_turn (int) - the number of wires to use to represent the helix, per turn
            sense ("LH"|"RH") - the handedness of the helix          
        Returns:
            obj (GeometryObject): The constructed geometry object representing the helix.
        """
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params, whitelist=['sense','wires_per_turn'])
        radius_m = params_m.get('diameter_m')/2
        length_m = params_m.get('length_m')
        pitch_m = params_m.get('pitch_m')
        wire_radius_m = params_m.get('wire_diameter_m')/2
        sense = params.get("sense", "RH")
        wires_per_turn = params.get("wires_per_turn", 36)

        turns = length_m / pitch_m
        n_wires = int(turns * wires_per_turn)
        delta_phi = (2 * math.pi) / wires_per_turn  # angle per segment
        delta_z_m = pitch_m / wires_per_turn 
        phi_sign = 1 if sense.upper() == "RH" else -1

        for i in range(n_wires):
            phi1 = phi_sign * delta_phi * i
            phi2 = phi_sign * delta_phi * (i + 1)
            x1 = radius_m * math.cos(phi1)
            y1 = radius_m * math.sin(phi1)
            z1 = delta_z_m * i
            x2 = radius_m * math.cos(phi2)
            y2 = radius_m * math.sin(phi2)
            z2 = delta_z_m * (i + 1)
            obj.add_wire(iTag, 0, x1, y1, z1, x2, y2, z2, wire_radius_m)

        return obj

    def flexi_helix(self, **params):
        """
        Create a helix along the Z axis where radius and pitch vary as scaled sums of cosines:

            r(Z) = r0 * Σ [RA_i * cos(i * π * Z / l + RP_i)] for i=0..n-1
            p(Z) = p0 * Σ [PA_i * cos(i * π * Z / l + PP_i)] for i=0..n-1

        The geometry is generated by stepping through helical phase (φ), and computing local radius and pitch from cosine series 
        as functions of normalized φ (mapped to Z via cumulative pitch integration).

        Parameters:
            l_{units} (float): Approximate helix length along Z
            r0_{units} (float): Base radius scale factor
            p0_{units} (float): Base pitch scale factor (length per full turn)
            n_cos (int): Number of cosine terms
            r_cos_params (list of tuples): [(RA0, RP0), ...] radius amplitudes and phases
            p_cos_params (list of tuples): [(PA0, PP0), ...] pitch amplitudes and phases
            wire_diameter_{units} (float): Wire thickness
            wires_per_turn (int): Resolution (segments per full turn)
            sense (str): "RH" or "LH" handedness

        Returns:
            GeometryObject: The constructed helix geometry object.
        """

        def cosine_series(s, terms):
            return sum(A * math.cos(i * math.pi * s + P) for i, (A, P) in enumerate(terms))

        # === Parameter unpacking and setup ===
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params, whitelist=['sense', 'wires_per_turn', 'n_cos','r_cos','p_cos'])

        l_m = params_m.get('length_m')
        r0_m = params_m.get('r0_m')
        p0_m = params_m.get('p0_m')
        wire_radius_m = params_m.get('wire_diameter_m') / 2
        sense = params.get("sense", "RH")
        wires_per_turn = params.get("wires_per_turn", 36)

        r_cos_params = params.get('r_cos_params')
        p_cos_params = params.get('p_cos_params')
        n_cos = params.get('n_cos')

        phi_sign = 1 if sense.upper() == "RH" else -1

        # Estimate number of turns from average pitch and total Z span
        est_turns = l_m / p0_m
        total_phi = est_turns * 2 * math.pi
        n_segments = int(wires_per_turn * est_turns)

        # Precompute all phi values
        phi_list = [i * total_phi / n_segments for i in range(n_segments + 1)]

        # === Generate 3D points ===
        z = -l_m / 2  # center the helix vertically
        points = []

        for i, phi in enumerate(phi_list):
            s = phi / total_phi  # Normalize φ to [0, +1]

            radius = r0_m * cosine_series(s, r_cos_params)
            pitch = p0_m * cosine_series(s, p_cos_params)
            delta_phi = total_phi / n_segments

            if i > 0:
                z += pitch * delta_phi / (2 * math.pi)
            x = radius * math.cos(phi_sign * phi)
            y = radius * math.sin(phi_sign * phi)
            points.append((x, y, z))

        # === Create wires ===
        for i in range(n_segments):
            x1, y1, z1 = points[i]
            x2, y2, z2 = points[i + 1]
            obj.add_wire(iTag, 0, x1, y1, z1, x2, y2, z2, wire_radius_m)

        return obj


    def circular_arc(self, **params):
        """
        Create a single circular arc in the XY plane centred on the origin
        Parameters:
            radius_{units} (float) - helix radius 
            wire_diameter_{units} (float) - diameter of wire making the helix
            In each case above, the units suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
            arc_phi_deg (float) - the angle subtended at the origin by the arc in degrees. Note that a continuous circular loop can be constructed by specifying arc_phi_deg = 360.
            n_wires (int) - the number of wires to use to represent the arc         
        Returns:
            obj (GeometryObject): The constructed geometry object representing the helix.
        """
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params, whitelist=['n_wires','arc_phi_deg'])
        radius_m = params_m.get('diameter_m')/2
        wire_radius_m = params_m.get('wire_diameter_m')/2    
        arc_phi_deg = params.get("arc_phi_deg")
        n_wires = params.get("n_wires", 36)

        delta_phi_deg = arc_phi_deg / n_wires        
        for i in range(n_wires):
            ca, sa = _cos_sin(delta_phi_deg * i)
            x1 = radius_m * ca
            y1 = radius_m * sa
            ca, sa = _cos_sin(delta_phi_deg * (i+1))
            x2 = radius_m * ca
            y2 = radius_m * sa
            obj.add_wire(iTag, 0, x1, y1, 0, x2, y2, 0, wire_radius_m)

        return obj

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
        ca, sa = _cos_sin(angle_deg)
        R = np.array([[ca, -sa, 0],
                      [sa, ca, 0],
                      [0, 0, 1]])
        return self.rotate(R)

    def rotate_around_X(self, angle_deg):
        ca, sa = _cos_sin(angle_deg)
        R = np.array([[1, 0, 0],
                      [0, ca, -sa],
                      [0, sa, ca]])
        return self.rotate(R)

    def rotate_around_Y(self, angle_deg):
        ca, sa = _cos_sin(angle_deg)
        R = np.array([[ca, 0, sa],
                      [0, 1, 0],
                      [-sa, 0, ca]])
        return self.rotate(R)

    
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
                    if (_point_should_connect_to_wire(es,wo['a'],wo['b'],tol)):
                        b = wo["b"]
                        wo['b']=tuple(es)
                        wires_to_add.append( (wo['iTag'], 0, *es, *b, wo['wr']) )
                        break #(for efficiency only)
        for params in wires_to_add:
            other.add_wire(*params)
               

#=================
# helper functions
#=================

def _cos_sin(angle_deg):
    angle_rad = math.pi*angle_deg/180
    ca = math.cos(angle_rad)
    sa = math.sin(angle_rad)
    return ca, sa

def _point_should_connect_to_wire(P, A, B, tol=1e-6):
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


def _point_on_object(geom_object, wire_index, alpha_wire):
    if(wire_index> len(geom_object.wires)):
        wire_index = len(geom_object.wires)
        alpha_wire = 1.0
    w = geom_object.wires[wire_index]
    A = np.array(w["a"], dtype=float)
    B = np.array(w["b"], dtype=float)
    P = A + alpha_wire * (B-A)
    return P






