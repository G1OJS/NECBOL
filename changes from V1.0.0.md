
## Restructuring
Restructured library modules to clarify module purposes, create 'components.py' holding *only* components, and avoid need for passing parameters between nec_wrapper and geometry_builder

If you have been using V1.0.0 with your own model files, you will need to make the following changes:

Replace the necbol import statements at the top with:
from necbol.modeller import NECModel
from necbol.components import components 
from necbol.gui import show_wires_from_file

replace 	view_wires(model.nec_in, model.EX_TAG, title = model.model_name)
with 		show_wires_from_file(model.nec_in, model.EX_TAG, title = model.model_name)


## New components
Added flexi-helix (experimental)

Tidied up optimiser screen output when using non-tty apps to run the code
   (use the tty=False keyword argument when calling optimiser)

Changed default ground in GE to -1. Corrected docstring (removed 'and conductivity = 0')

Added dielectric / conductive sheets.

## Detailed changes

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

