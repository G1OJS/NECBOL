# V2.1.0
Changes forced by 'stretching test case' of building a model of a car passenger cell with a handheld transmitter inside. This requires meshed grids to connect cleanly, which requires 0,1,2,3 or 4 edges to be left 'open' *and* requires changes to the wire connection decision functions:

Revised sheet grid model to 
```
thin_sheet(self, model, sigma, epsillon_r, force_odd = True,
                   close_start = True, close_end = True,
                   close_bottom = True, close_top = True,
                   enforce_exact_pitch = True,
                   **dimensions):
```
where 
- force_odd forces an odd number of wires, ensuring one central z wire and one central y wire cross at x=0, to make attaching other objects easier
The four 'close_' parameters determine whether or not the edges are 'sealed' with a final wire (if True) or not (if False) so that the grid can be joined to other grids without wires overlapping:
            close_end = True completes the grid with a final end z wire at y = length/2 
            close_start = True starts the grid with a z wire at y = -length/2 
            close_top = True completes the grid with a y wire at z = height/2 
            close_bottom = True starts the grid with a y wire at z = -height/2 

If enforce_exact_pitch is True, length and height are adjusted to fit an integer number of grid cells of the specified pitch. If False, length and height remain as specified and the grid pitch in Y and Z is adjusted to fit the number of grid cells calculated from the grid pitch and force_odd value. Behaviour prior to V2.0.3 was enforce_exact_pitch.

"point_on_object()" deleted (not used)



"point_should_connect_to_wire" now also checks if wire to be connected is near a segment boundary, and preserves the wire (doesn't split it) if true


# V2.0.2
Revised sheet grid model to 
```
thin_sheet(self, model, sigma, epsillon_r, force_odd = True, close_end = True, **dimensions)
```
where 
- force_odd forces an odd number of wires, ensuring one central z wire and one central y wire cross at x=0, to make attaching other objects easier
- close_end creates a final end z wire - use close_end=False to allow copying and joining meshes together without wires overlapping
- model now has height symmetric around zero (as was the case for width)
  
Created example of dipole with capacity end points for loading, using the grid model

Updated plotting functions a little (gain range)

# V2.0.1
Added azimuth pattern specification and plotting
Fixed .nec file write format issue and nSegs issue in writing sheet model grid
Created example of dipole with nearby sheet
Allowed model to be updated after nec_write & nec_run, to allow easier A/B comparisons (see dipole with sheet example)

# V2.0.0
## Changes to API
If you have been using V1.0.0 with your own model files, you will need to make the following changes:

```
Replace the necbol import statements at the top with:
   from necbol.modeller import NECModel
   from necbol.components import components 
   from necbol.gui import show_wires_from_file

replace
   view_wires(model.nec_in, model.EX_TAG, title = model.model_name)

with
   show_wires_from_file(model.nec_in, model.EX_TAG, title = model.model_name)

replace
   antenna_components = geometry_builder.components()

with
   antenna_components = components()
```
Also note that if you have been using positional arguments for antenna components, the order of some of them has changed in order to group non-length associated arguments together. If you have used named arguments, these should still work. Check the function definitions in components.py in case of issues.

## New components
Added flexi-helix (experimental)

Added dielectric / conductive sheets. (Note that this sheet model has been checked functionally but not quantitavely)

## Minor changes
Tidied up optimiser screen output when using non-tty apps to run the code
   (use the tty=False keyword argument when calling optimiser)

Changed default ground in GE to -1. Corrected docstring (removed 'and conductivity = 0')

Added azimuth pattern plotting and example of dipole with nearby metal / dielectric sheet (V2.0.1)

## Restructuring
Restructured library modules to clarify module purposes, create 'components.py' holding *only* components, and avoid need for passing parameters between nec_wrapper and geometry_builder. Details below.

----------------------------
file "nec_wrapper.py"
-  renamed to "modeller.py"

---------------------------------
file "units.py"
- deleted
- contents added to "modeller.py"

---------------------------------------
file "geometry_builder.py" 
- renamed to "components.py"
- class GeometryObject moved into "modeller.py"
- _cos_sin moved to within GeometryObject and renamed to cos_sin
- _point_should_connect_to_wire moved to within GeometryObject and renamed to point_should_connect_to_wire
- _point_on_object moved to within GeometryObject and renamed to point_on_object

(components.py now contains only the library components definitions)

-----------------------------------
file "wire_viewer.py"
 - renamed to gui.py:

- view_wires(...) renamed to show_wires(...)
- view_nec_input(...) renamed to show_wires_from_file(...)
- parse_nec_wires(...) is incorporated into show_wires_from_file

-----------------------------------
file "optimisers.py" 
- no changes

# V1.0.0 initial MVP

