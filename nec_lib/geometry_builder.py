#Component	Description	Key Params / Conventions
#Dipole	Straight wire element	length, wire diameter, axis_az/el, center anchor
#Rectangular Loop	Four-wire rectangle in a plane	width, height, wire diameter, nTagrmal_az/el, center anchor
#Circular Loop	Circular wire loop	radius, wire diameter, nTagrmal_az/el, center anchor
#Folded Dipole	Parallel wire folded structure	base dipole params + fold spacing, fold wire diameter
#MonTagpole	Dipole over ground plane	length, wire diameter, axis, center at feedpoint (ground)
#Helix	Helical wire antenna	diameter, pitch, number of turns, wire diameter, axis, center
#Stub / Matching Section	Short wire segment for impedance matching	length, wire diameter, axis, center
#Wire Array	Array of wires with specified spacing and phasing	component type + array geometry
#Patch / Panel	Flat conducting surface (for reflectors, ground planes)	dimensions, thickness, nTagrmal_a

import numpy as np

class components:
    def __init__(self, starting_tag_nr, segment_length_m, ex_tag):
        self.object_counter = starting_tag_nr
        self.segLen_m = segment_length_m
        self.EX_TAG = ex_tag
        
    def wire_with_feedpoint(self, length_m = 1, wire_diameter_mm = 1.0, feedpoint_alpha = 0.5): 
        self.object_counter += 1
        nTag = self.object_counter
        obj = GeometryObject([])
        z1 = -length_m/2
        zf1 = z1 + length_m * feedpoint_alpha - self.segLen_m / 2   
        zf2 = zf1 + self.segLen_m
        z2 = length_m/2
        nS = int( (zf1 - z1) / self.segLen_m)
        obj.add_wire(nTag,    nS, 0, 0, z1, 0, 0, zf1, wire_diameter_mm/2000)
        obj.add_wire(self.EX_TAG, 1, 0, 0, zf1, 0, 0, zf2, wire_diameter_mm/2000)
        nS = int((z2 - zf2) / self.segLen_m)
        obj.add_wire(nTag,    nS, 0, 0, zf2, 0, 0, z2, wire_diameter_mm/2000)
        return obj
    
    def rect_loop(self, length_m = 1, width_m = 0.2, wire_diameter_mm = 1.0):
        self.object_counter += 1
        nTag = self.object_counter
        obj = GeometryObject([])
        nS = int((length_m) / self.segLen_m)
        obj.add_wire(nTag,    nS, -width_m/2, 0, -length_m/2, -width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        obj.add_wire(nTag, nS,  width_m/2, 0, -length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        nS = int((width_m) / self.segLen_m)
        obj.add_wire(nTag, nS, -width_m/2, 0, -length_m/2,  width_m/2, 0,-length_m/2, wire_diameter_mm/2000)
        obj.add_wire(nTag, nS, -width_m/2, 0,  length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
        return obj

class GeometryObject:
    def __init__(self, wires):
        self.wires = wires  # list of wire dicts with nTag, nS, x1, y1, ...

    def add_wire(self, nTag, nS, x1, y1, z1, x2, y2, z2, wr):
        self.wires.append({"nTag":nTag, "nS":nS, "a":(x1, y1, z1), "b":(x2, y2, z2), "wr":wr})

    def get_wires(self):
        return self.wires

    def Translate(self, dx, dy, dz):
        for w in self.wires:
            w['a'] = tuple(map(float,np.array(w['a']) + np.array([dx, dy, dz])))
            w['b'] = tuple(map(float,np.array(w['b']) + np.array([dx, dy, dz])))

    def Rotate_ZtoY(self):
        R = np.array([[1, 0, 0],[0,  0, 1],[0,  -1, 0]])
        return self.rotate(R)
    
    def Rotate_ZtoX(self):
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
                        a = np.array(wo['a'])
                        b = np.array(wo['b'])
                        p = np.array(es)
                        ab = np.linalg.norm(b - a)
                        ap = np.linalg.norm(p - a)
                        s1 = max(1,round(wo['nS']*(ap/ab)) )
                        s2 = wo['nS'] - s1
                        wo['b']=tuple(es)
                        wo['nS'] = s1
                        wires_to_add.append( (wo['nTag']+1, s2, *es, *b, wo['wr']) )
                        break #(for efficiency only)
        for params in wires_to_add:
            self.add_wire(*params)


# =============
# these will go in the wire class eventually
def touches(end, wire, tol=1e-6):
    return _point_on_segment(end, wire['a'], wire['b'], tol)

def _point_on_segment(P, A, B, tol=1e-6):
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


def ends(wire):
    return [wire["a"], wire["b"]]
#===========





