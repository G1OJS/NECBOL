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
from necbol.modeller import GeometryObject,units

#=================================================================================
# Cannonical components
#=================================================================================

class components:
    def __init__(self, starting_tag_nr = 0):
        """Sets object_counter to starting_tag_nr (tags number identifies an object)
        and loads the units module class units()
        """
        self.object_counter = starting_tag_nr
        self.units = units()

    def new_geometry_object(self):
        """increment the object counter and return a GeometryObject with the counter's new value
        """
        self.object_counter += 1
        iTag = self.object_counter
        return iTag, GeometryObject([])

    def copy_of(self, existing_obj):
        """Returns a clone of existing_obj with a new iTag
        """
        iTag, obj = self.new_geometry_object()
        for w in existing_obj.wires:
            obj.add_wire(iTag, w['nS'], *w['a'], *w['b'], w['wr'])
        return obj
        
    def wire_Z(self, **dimensions):
        """
        Create a straight wire aligned along the Z-axis, centered at the origin.

        The wire extends from -length/2 to +length/2 on the Z-axis, with the specified diameter.

        dimensions:
            length_{units_string} (float): Length of the wire. 
            wire_diameter_{units_string} (float): Diameter of the wire.
            In each case, the unit suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wire.
        """
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)
        half_length_m = dimensions_m.get('length_m')/2
        wire_radius_m = dimensions_m.get('wire_diameter_m')/2
        obj.add_wire(iTag, 0, 0, 0, -half_length_m, 0, 0, half_length_m, wire_radius_m)
        return obj
    
    def rect_loop_XZ(self, **dimensions):
        """
        Create a rectangular wire loop in the XZ plane, centered at the origin, with the specified wire diameter.
        The 'side' wires extend from Z=-length/2 to Z=+length/2 at X = +/- width/2.
        The 'top/bottom' wires extend from X=-width/2 to X=+width/2 at Z = +/- length/2.
        dimensions:
            length_{units_string} (float): 'Length' (extension along Z) of the rectangle. 
            width_{units_string} (float): 'Width' (extension along X) of the rectangle. 
            wire_diameter_{units_string} (float): Diameter of the wires.
            In each case, the unit suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wires.
        """
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)
        half_length_m = dimensions_m.get('length_m')/2
        half_width_m = dimensions_m.get('width_m')/2
        wire_radius_m = dimensions_m.get('wire_diameter_m')/2        
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
        Arguments:
            from_object (GeometryObject), from_wire_index (int, 0 .. n_wires_in_from_object - 1), from_alpha_wire (float, 0 .. 1)
            to_object (GeometryObject), to_wire_index (int, 0 .. n_wires_in_to_object - 1), to_alpha_wire (float, 0 .. 1)
        Returns:
            obj (GeometryObject): The constructed geometry object with the defined wire.
        """
        iTag, obj = self.new_geometry_object()
        from_point = obj.point_on_object(from_object, from_wire_index, from_alpha_wire)
        to_point = obj.point_on_object(to_object, to_wire_index, to_alpha_wire)
        obj.add_wire(iTag, 0, *from_point, *to_point, wire_diameter_mm/2000) 
        return obj

    def helix(self,  wires_per_turn, sense, **dimensions):
        """
        Create a single helix with axis = Z axis
        Arguments_
            sense ("LH"|"RH") - the handedness of the helix          
            wires_per_turn (int) - the number of wires to use to represent the helix, per turn
            dimensions:
                radius_{units} (float) - helix radius 
                length_{units} (float) - helix length along Z 
                pitch_{units} (float)  - helix length along Z per whole turn
                wire_diameter_{units} (float) - diameter of wire making the helix
                In each case above, the units suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object representing the helix.
        """
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)
        radius_m = dimensions_m.get('diameter_m')/2
        length_m = dimensions_m.get('length_m')
        pitch_m = dimensions_m.get('pitch_m')
        wire_radius_m = dimensions_m.get('wire_diameter_m')/2

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

    def flexi_helix(self, sense, wires_per_turn, n_cos,r_cos_params,p_cos_params, **dimensions):
        """
        Create a helix along the Z axis where radius and pitch vary as scaled sums of cosines:

            r(Z) = r0 * Σ [RA_i * cos(i * π * Z / l + RP_i)] for i=0..n-1
            p(Z) = p0 * Σ [PA_i * cos(i * π * Z / l + PP_i)] for i=0..n-1

        The geometry is generated by stepping through helical phase (φ), and computing local radius and pitch from cosine series 
        as functions of normalized φ (mapped to Z via cumulative pitch integration).

        Parameters:
            sense (str): "RH" or "LH" handedness
            wires_per_turn (int): Resolution (segments per full turn)
            n_cos (int): Number of cosine terms
            r_cos_params (list of tuples): [(RA0, RP0), ...] radius amplitudes and phases
            p_cos_params (list of tuples): [(PA0, PP0), ...] pitch amplitudes and phases
            dimensions:
                l_{units} (float): Approximate helix length along Z
                r0_{units} (float): Base radius scale factor
                p0_{units} (float): Base pitch scale factor (length per full turn)
                wire_diameter_{units} (float): Wire thickness

        Returns:
            GeometryObject: The constructed helix geometry object.
        """

        def cosine_series(s, terms):
            return sum(A * math.cos(i * math.pi * s + P) for i, (A, P) in enumerate(terms))

        # === Parameter unpacking and setup ===
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)

        l_m = dimensions_m.get('length_m')
        r0_m = dimensions_m.get('r0_m')
        p0_m = dimensions_m.get('p0_m')
        wire_radius_m = dimensions_m.get('wire_diameter_m') / 2

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


    def circular_arc(self, n_wires, arc_phi_deg, **dimensions):
        """
        Create a single circular arc in the XY plane centred on the origin
        Arguments:
            n_wires (int) - the number of wires to use to represent the arc         
            arc_phi_deg (float) - the angle subtended at the origin by the arc in degrees. Note that a continuous circular loop can be constructed by specifying arc_phi_deg = 360.
            dimensions:
                radius_{units} (float) - helix radius 
                wire_diameter_{units} (float) - diameter of wire making the helix
                In each case above, the units suffix (e.g., _mm, _m) must be present in the units class dictionary '_UNIT_FACTORS' (see units.py)
        Returns:
            obj (GeometryObject): The constructed geometry object representing the helix.
        """
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)
        radius_m = dimensions_m.get('diameter_m')/2
        wire_radius_m = dimensions_m.get('wire_diameter_m')/2    

        delta_phi_deg = arc_phi_deg / n_wires        
        for i in range(n_wires):
            ca, sa = obj.cos_sin(delta_phi_deg * i)
            x1 = radius_m * ca
            y1 = radius_m * sa
            ca, sa = obj.cos_sin(delta_phi_deg * (i+1))
            x2 = radius_m * ca
            y2 = radius_m * sa
            obj.add_wire(iTag, 0, x1, y1, 0, x2, y2, 0, wire_radius_m)

        return obj


    def thin_sheet(self, model, sigma, epsillon_r, force_odd = True,
                   close_start = True, close_end = True,
                   close_bottom = True, close_top = True,
                   enforce_exact_pitch = True,
                   **dimensions):
        """
        Creates a grid of wires interconnected at segment level to economically model a flat sheet
        which is normal to the x axis and extends from z=-height/2 to z= height/2, and y = -length/2 to length/2
        Models *either* conductive or dielectric sheet, not both.
        Set epsillon_r to 1.0 for conductive sheet
        Set epsillon_r > 1.0 for dielectric sheet (conductivity value is then not used)

        Arguments:
            model - the object model being built
            sigma - conductivity in mhos/metre
            epsillon_r - relative dielectric constant
            force_odd = true ensures wires cross at y=z=0
            The four 'close_' parameters determine whether or not the edges are 'sealed' with a final wire (if True) or
            not (if False) so that the grid can be joined to other grids without wires overlapping:
                close_end = True completes the grid with a final end z wire at y = length/2 
                close_start = True starts the grid with a z wire at y = -length/2 
                close_top = True completes the grid with a y wire at z = height/2 
                close_bottom = True starts the grid with a y wire at z = -height/2 
            enforce_exact_pitch: if True, length and height are adjusted to fit an integer number
            of grid cells of the specified pitch. If False, length and height remain as specified and
            the grid pitch in Y and Z is adjusted to fit the number of grid cells calculated from the
            grid pitch and force_odd value. Behaviour prior to V2.0.3 was enforce_exact_pitch.

        Dimensions are length_, height_, thickness_, grid_pitch_
        """
        
        print("NOTE: The thin_sheet model has been tested functionally but not validated quantitavely")
        iTag, obj = self.new_geometry_object()
        dimensions_m = self.units.from_suffixed_dimensions(dimensions)
        length_m = dimensions_m.get('length_m')
        height_m = dimensions_m.get('height_m')
        grid_pitch_m = dimensions_m.get('grid_pitch_m')
        thickness_m = dimensions_m.get('thickness_m')
        E = epsillon_r     
        dG = grid_pitch_m

        nY = int(length_m / dG) + 1
        nZ = int(height_m / dG) + 1
        if (force_odd):
            nY += (nY+1) % 2
            nZ += (nZ+1) % 2
        if (enforce_exact_pitch):
            L = (nY-1)*dG
            H = (nZ-1)*dG
            dY = dG
            dZ = dG
        else:
            dY = L/(nY-1)
            dZ = H/(nz-1)
        E0 = 8.854188 * 1e-12
        CD = E0*(E-1) * thickness_m
        wire_radius_m = thickness_m/2

        # Create sheet
        i0 = 0 if close_start else 1
        i1 = nY if close_end else nY-1
        j0 = 0 if close_bottom else 1
        j1 = nZ if close_top else nZ-1
        for i in range(i0, i1):     # make z wires
            x1, y1, z1, x2, y2, z2 = [0, -L/2+i*dY, -H/2, 0, -L/2+i*dY, H/2]
            nSegs = nZ-1
            obj.add_wire(iTag, nSegs, x1, y1, z1, x2, y2, z2, wire_radius_m)

        for j in range(j0, j1):     # make y wires
            x1, y1, z1, x2, y2, z2 = [0, -L/2, -H/2+j*dZ, 0, L/2, -H/2+j*dZ]
            nSegs = nY-1
            obj.add_wire(iTag, nSegs, x1, y1, z1, x2, y2, z2, wire_radius_m)

        # add conductive / capacitive load to the iTag of this object
        # note we aren't ineserting a new segment specifically for the load, so there's no need to
        # increment model.LOAD_iTag
        if(epsillon_r > 1.0):
            R_Ohms = 1e12
            C_F = CD
        else:
            R_Ohms = dG / sigma
            C_F = 0.0
        model.LOADS.append(f"LD 1 {iTag} 0 0 {R_Ohms:.6e} {1e-12:.6e} {CD:.6e}\n")
                    
        return obj


