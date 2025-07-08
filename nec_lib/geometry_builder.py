#Component	Description	Key Params / Conventions
#Circular Loop	Circular wire loop	radius, wire diameter, nTagrmal_az/el, center anchor
#Folded Dipole	Parallel wire folded structure	base dipole params + fold spacing, fold wire diameter
#Wire Array	Array of wires with specified spacing and phasing	component type + array geometry
#Patch / Panel	Flat conducting surface (for reflectors, ground planes)	dimensions, thickness, nTagrmal_a

# make at least this file self-documenting
#Helix	Helical wire antenna	diameter, pitch, number of turns, wire diameter, axis, center
# split to accomodate Helix_with_feed?

#Feedlines (for common mode)
#Stub / Matching Section	Short wire segment for impedance matching	length, wire diameter, axis, center
# - TL from EX_TAG to another TAG plus a stub

#Replicator to stack & bay?

import numpy as np
import math

class components:
    def __init__(self, starting_tag_nr, segment_length_m, ex_tag):
        self.object_counter = starting_tag_nr
        self.segLen_m = segment_length_m
        self.EX_TAG = ex_tag

    def new_geometry_object(self):
        self.object_counter += 1
        nTag = self.object_counter
        return nTag, GeometryObject([])
        
    def wire_Z(self, length_m = 1, wire_diameter_mm = 1.0, Origin_Z = 0):
        nTag, obj = self.new_geometry_object()
        z1 = -length_m/2
        z2 = length_m/2
        nS = int( (z2 - z1) / self.segLen_m)
        obj.add_wire(nTag,    nS, 0, 0, z1, 0, 0, z2, wire_diameter_mm/2000)
        obj.translate(0, 0, -Origin_Z)
        return obj

    def wire_Z_with_feedpoint(self, length_m = 1, wire_diameter_mm = 1.0, feedpoint_alpha = 0.5, Origin_Z = 0): 
        nTag, obj = self.new_geometry_object()
        z1 = -length_m/2
        zf1 = z1 + length_m * feedpoint_alpha - self.segLen_m / 2   
        zf2 = zf1 + self.segLen_m
        z2 = length_m/2
        nS = int( (zf1 - z1) / self.segLen_m)
        obj.add_wire(nTag,    nS, 0, 0, z1, 0, 0, zf1, wire_diameter_mm/2000)
        obj.add_wire(self.EX_TAG, 1, 0, 0, zf1, 0, 0, zf2, wire_diameter_mm/2000)
        nS = int((z2 - zf2) / self.segLen_m)
        obj.add_wire(nTag,    nS, 0, 0, zf2, 0, 0, z2, wire_diameter_mm/2000)
        obj.translate(0, 0, -Origin_Z)
        return obj
    
    def rect_loop_XZ(self, length_m = 1, width_m = 0.2, wire_diameter_mm = 1.0, Origin_X = 0, Origin_Z = 0):
        nTag, obj = self.new_geometry_object()
        nS = int((length_m) / self.segLen_m)
        obj.add_wire(nTag,    nS, -width_m/2, 0, -length_m/2, -width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        obj.add_wire(nTag, nS,  width_m/2, 0, -length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        nS = int((width_m) / self.segLen_m)
        obj.add_wire(nTag, nS, -width_m/2, 0, -length_m/2,  width_m/2, 0,-length_m/2, wire_diameter_mm/2000)
        obj.add_wire(nTag, nS, -width_m/2, 0,  length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        obj.translate(-Origin_X, 0, -Origin_Z)
        return obj

    def connector(self, fromObject, fromParam, toObject, toParam, wire_diameter_mm = 1.0):
        nTag, obj = self.new_geometry_object()
        from_point = parametricPoint(fromObject, fromParam)
        to_point = parametricPoint(toObject, toParam)
        l = distance(from_point, to_point)
        nS = int(l / self.segLen_m)
        obj.add_wire(nTag, nS, *from_point, *to_point, wire_diameter_mm/2000) 
        return obj

    def helix(self, diameter_mm, length_mm, pitch_mm, sense="RH", segments_per_turn=36, wire_diameter_mm = 1.0):
        nTag, obj = self.new_geometry_object()

        turns = length_mm / pitch_mm
        total_segments = int(turns * segments_per_turn)
        delta_theta = (2 * math.pi) / segments_per_turn  # angle per segment
        delta_z = pitch_mm / segments_per_turn /1000
        theta_sign = 1 if sense.upper() == "RH" else -1
        radius = diameter_mm/2000

        for i in range(total_segments):
            theta1 = theta_sign * delta_theta * i
            theta2 = theta_sign * delta_theta * (i + 1)
            x1 = radius * math.cos(theta1)
            y1 = radius * math.sin(theta1)
            z1 = delta_z * i
            x2 = radius * math.cos(theta2)
            y2 = radius * math.sin(theta2)
            z2 = delta_z * (i + 1)
            obj.add_wire(nTag, 1, x1, y1, z1, x2, y2, z2, wire_diameter_mm / 2000)

        return obj

    def circular_loop_with_feedpoint(self, diameter_mm, segments=36, wire_diameter_mm = 1.0):
        objTag, obj = self.new_geometry_object()
        delta_phi = (2 * math.pi) / segments
        radius = diameter_mm/2000

        for i in range(segments):
            phi1 = delta_phi * i
            phi2 = delta_phi * (i + 1)
            x1 = radius * math.cos(phi1)
            y1 = radius * math.sin(phi1)
            x2 = radius * math.cos(phi2)
            y2 = radius * math.sin(phi2)
            nTag = objTag if (i!=0) else self.EX_TAG
            obj.add_wire(nTag, 1, x1, y1, 0, x2, y2, 0, wire_diameter_mm / 2000)

        return obj

class GeometryObject:
    def __init__(self, wires):
        self.wires = wires  # list of wire dicts with nTag, nS, x1, y1, ...

    def add_wire(self, nTag, nS, x1, y1, z1, x2, y2, z2, wr):
        self.wires.append({"nTag":nTag, "nS":nS, "a":(x1, y1, z1), "b":(x2, y2, z2), "wr":wr})

    def get_wires(self):
        return self.wires

    def translate(self, dx, dy, dz):
        for w in self.wires:
            w['a'] = tuple(map(float,np.array(w['a']) + np.array([dx, dy, dz])))
            w['b'] = tuple(map(float,np.array(w['b']) + np.array([dx, dy, dz])))

    def rotate_ZtoY(self):
        R = np.array([[1, 0, 0],[0,  0, 1],[0,  -1, 0]])
        return self.rotate(R)
    
    def rotate_ZtoX(self):
        R = np.array([[0, 0, -1],[0,  1, 0],[1,  0, 0]])
        return self.rotate(R)

    def rotate(self, R):
        for w in self.wires:
            a = np.array(w['a'])
            b = np.array(w['b'])
            w['a'] = tuple(map(float, R @ a))
            w['b'] = tuple(map(float, R @ b))

    def connect_ends(self, other):
        wires_to_add=[]
        for ws in self.wires:
            for es in ends(ws):
                for wo in other.wires:
                    if (touches(es,wo)):
                        _split_wire_at(wo, es, wires_to_add)
                        break #(for efficiency only)
        for params in wires_to_add:
            other.add_wire(*params)
        

# =============
# these will go in the wire class eventually
def touches(end, wire, tol=1e-6):
    return _point_lies_on_line(end, wire['a'], wire['b'], tol)

def _point_lies_on_line(P, A, B, tol=1e-6):
    P = np.array(P, dtype=float)
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)

    AB = B - A
    AP = P - A
    AB_len = np.linalg.norm(AB)

    if AB_len == 0:
        # Degenerate wire, treat as a point
        return np.linalg.norm(P - A) < tol

    # 1. Check perpendicular distance
    perp_dist = np.linalg.norm(np.cross(AP, AB)) / AB_len
    if perp_dist > tol:
        return False

    # 2. Check scalar projection is within segment
    t = np.dot(AP, AB) / (AB_len ** 2)
    return 0 <= t <= 1

def _split_wire_at(wo, es, wires_to_add):
    a = np.array(wo['a'])
    b = np.array(wo['b'])
    p = np.array(es)
    ab = np.linalg.norm(b - a)
    ap = np.linalg.norm(p - a)
    s1 = max(1,round(wo['nS']*(ap/ab)) )
    s2 = wo['nS'] - s1
    wo['b']=tuple(es)
    wo['nS'] = s1
    wires_to_add.append( (wo['nTag'], s2, *es, *b, wo['wr']) )

def ends(wire):
    return [wire["a"], wire["b"]]

def parametricPoint(geom_object, wire_index_plus_alpha):
    wire_index = int(wire_index_plus_alpha)
    alpha = wire_index_plus_alpha - wire_index
    w = geom_object.wires[wire_index]
    A = np.array(w["a"], dtype=float)
    B = np.array(w["b"], dtype=float)
    P = A + alpha * (B-A)
    return P

def distance(point1, point2):
    A = np.array(point1)
    B = np.array(point2)
    V = B-A
    return np.linalg.norm(V)

#===========





