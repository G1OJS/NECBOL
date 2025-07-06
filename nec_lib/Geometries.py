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

class GeometryObject:
    def __init__(self, wires):
        self.wires = wires  # list of wire dicts with nTag, nS, x1, y1, ...

    def Rotate_ZtoY(self):
        R = np.array([[1, 0, 0],[0,  0, 1],[0,  -1, 0]])
        return self.rotate(R)
    
    def Rotate_ZtoX(self):
        R = np.array([[0, 0, -1],[0,  1, 0],[1,  0, 0]])
        return self.rotate(R)

    def rotate(self, R):
        for w in self.wires:
            p1 = np.array([w['x1'], w['y1'], w['z1']])
            p2 = np.array([w['x2'], w['y2'], w['z2']])
            p1 = R @ p1
            p2 = R @ p2
            w['x1'], w['y1'], w['z1'] = p1
            w['x2'], w['y2'], w['z2'] = p2

    def Translate(self, dx, dy, dz):
        d = np.array([dx, dy, dz])
        for w in self.wires:
            w['x1'] += d[0]; w['y1'] += d[1]; w['z1'] += d[2]
            w['x2'] += d[0]; w['y2'] += d[1]; w['z2'] += d[2]

    def add_wire(self, nTag, nS, x1, y1, z1, x2, y2, z2, wr):
        self.wires.append({"nTag":nTag, "nS":nS, "x1":x1, "y1":y1, "z1":z1, "x2":x2, "y2":y2, "z2":z2, "wr":wr})

    def get_wires(self):
        return self.wires


global lambda_mg, object_counter, nSegs_per_wavelength, segLength_m, object_counter, EX_TAG
nSegs_per_wavelength = 40

def set_lambda(wl_m):
    global lambda_m, segLength_m
    lambda_m = wl_m
    segLength_m = lambda_m / nSegs_per_wavelength

def init():
    global object_counter, wires, EX_TAG
    object_counter = 0
    EX_TAG = 999

def _nSegments(nSegs, length_m):
   return int(nSegs_per_wavelength*length_m/lambda_m) if (nSegs == 0) else nSegs

def wire_with_feedpoint(length_m = 1, wire_diameter_mm = 1, feedpoint_alpha = 0.5, nSegsIgnTagred = 0):
    # trying to allow choice of auto/specified segmentation but complicated with multi-wire objects 
    global object_counter
    object_counter += 1
    nTag = object_counter
    obj = GeometryObject([])
    z1 = -length_m/2
    zf1 = z1 + length_m * feedpoint_alpha - segLength_m / 2   
    zf2 = zf1 + segLength_m
    z2 = length_m/2
    nS = _nSegments(0, zf1 - z1)
    obj.add_wire(nTag,    nS, 0, 0, z1, 0, 0, zf1, wire_diameter_mm/2000)
    obj.add_wire(EX_TAG, 1, 0, 0, zf1, 0, 0, zf2, wire_diameter_mm/2000)
    nS = _nSegments(0, z2 - zf2)
    obj.add_wire(nTag,    nS, 0, 0, zf2, 0, 0, z2, wire_diameter_mm/2000)
    return obj
    
def rect_loop(length_m = 1, width_m = 0.2, wire_diameter_mm = 1, nSegsIgnTagred = 0):
    # trying to allow choice of auto/specified segmentation but complicated with multi-wire objects 
    global object_counter
    object_counter += 1
    nTag = object_counter
    obj = GeometryObject([])
    nS = _nSegments(0, length_m)
    obj.add_wire(nTag,    nS, -width_m/2, 0, -length_m/2, -width_m/2, 0, length_m/2, wire_diameter_mm/2000)
    obj.add_wire(nTag, nS,  width_m/2, 0, -length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
    nS = _nSegments(0, width_m)
    obj.add_wire(nTag, nS, -width_m/2, 0, -length_m/2,  width_m/2, 0,-length_m/2, wire_diameter_mm/2000)
    obj.add_wire(nTag, nS, -width_m/2, 0,  length_m/2,  width_m/2, 0, length_m/2, wire_diameter_mm/2000)
    return obj


