#Component	Description	Key Params / Conventions
#Dipole	Straight wire element	length, wire diameter, axis_az/el, center anchor
#Rectangular Loop	Four-wire rectangle in a plane	width, height, wire diameter, normal_az/el, center anchor
#Circular Loop	Circular wire loop	radius, wire diameter, normal_az/el, center anchor
#Folded Dipole	Parallel wire folded structure	base dipole params + fold spacing, fold wire diameter
#Monopole	Dipole over ground plane	length, wire diameter, axis, center at feedpoint (ground)
#Helix	Helical wire antenna	diameter, pitch, number of turns, wire diameter, axis, center
#Stub / Matching Section	Short wire segment for impedance matching	length, wire diameter, axis, center
#Wire Array	Array of wires with specified spacing and phasing	component type + array geometry
#Patch / Panel	Flat conducting surface (for reflectors, ground planes)	dimensions, thickness, normal_a

from nec_lib import NEC_builder as BUILD
global lambda_mg, object_counter, nSegs_per_wavelength, segLength_m, object_counter
nSegs_per_wavelength = 40

def set_lambda(wl_m):
    global lambda_m, segLength_m
    lambda_m = wl_m
    segLength_m = lambda_m / nSegs_per_wavelength

def init_object_counter(n=1):
    global object_counter
    object_counter = n

def nSegments(nSegs, length_m):
   return int(nSegs_per_wavelength*length_m/lambda_m) if (nSegs == 0) else nSegs

def add_wire_with_feedpoint(length_m = 1, wire_diameter_mm = 1, feedpoint_alpha = 0.5, nSegsIgnored = 0):
    # trying to allow choice of auto/specified segmentation but complicated with multi-wire objects 
    global object_counter
    EX_TAG = 999
    nO = object_counter
    object_counter += 1
    x1,y1,z1 = [0,0,-length_m/2]
    x2,y2,z2 = [0,0,length_m/2]
    xf,yf,zf = [0,0,z1 + length_m * feedpoint_alpha]    
    nS = nSegments(0, zf - z1)
    BUILD.add_Wire(f"GW {nO} {nS} {x1:.4f} {y1:.4f} {z1:.4f} {xf:.4f} {yf:.4f} {zf-segLength_m/2:.4f}  {wire_diameter_mm/2000:.4f} \n")
    BUILD.add_Wire(f"GW {EX_TAG} 1 {xf:.4f} {yf:.4f} {zf-segLength_m/2:.4f} {x2:.4f} {y2:.4f} {zf+segLength_m/2:.4f}  {wire_diameter_mm/2000:.4f} \n")
    nS = nSegments(0, z2 - zf)
    BUILD.add_Wire(f"GW {nO} {nS} {xf:.4f} {yf:.4f} {zf+segLength_m/2:.4f} {x2:.4f} {y2:.4f} {z2:.4f}  {wire_diameter_mm/2000:.4f} \n")
    BUILD.set_Source(f"EX 0 {EX_TAG} 1 0 1 0\n")

