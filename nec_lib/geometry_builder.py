import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import math
from nec_lib.units import units

#=================================================================================
# Cannonical components
#=================================================================================

class components:
    def __init__(self, starting_tag_nr = 0):
        self.object_counter = starting_tag_nr
        self.units = units()

    def new_geometry_object(self):
        self.object_counter += 1
        iTag = self.object_counter
        return iTag, GeometryObject([])
        
    def wire_Z(self, **params):
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params)
        half_length_m = params_m.get('length_m')/2
        wire_radius_m = params_m.get('wire_diameter_m')/2
        obj.add_wire(iTag, 0, 0, 0, -half_length_m, 0, 0, half_length_m, wire_radius_m)
        return obj
    
    def rect_loop_XZ(self, **params):
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
        iTag, obj = self.new_geometry_object()
        from_point = _point_on_object(from_object, from_wire_index, from_alpha_wire)
        to_point = _point_on_object(to_object, to_wire_index, to_alpha_wire)
        obj.add_wire(iTag, 0, *from_point, *to_point, wire_diameter_mm/2000) 
        return obj

    def helix(self, **params):
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params)
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

    def circular_arc(self, **params):
        iTag, obj = self.new_geometry_object()
        params_m = self.units.from_suffixed_params(params)
        radius_m = params_m.get('diameter_m')/2
        wire_radius_m = params_m.get('wire_diameter_m')/2    
        sense = params.get("sense", "RH")
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
        R = np.array([[0, 0, -1],[0,  1, 0],[1,  0, 0]])
        return self.rotate(R)

    def rotate_around_Z(self, angle_deg):
        ca, sa = _cos_sin(angle_deg)
        R = np.array([[ca, sa, 0], [-sa, ca, 0], [0,0,1]])
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






