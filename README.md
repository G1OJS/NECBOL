# NECBOL

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

I wrote it primarily for my own use for the reasons below, but I think it's good enough now to share so that other people can make use of it.
 - Not having to think about splitting wires into three-way junctions
 - Being able to re-use components easily (almost in the style of copy, paste, rotate, move, connect)
 - Being able to comment out entire components like loops, helices etc with one or two comment symbols
 - Being able to add and remove 'environment' components like dielectric slabs and conductive sheets, cylinders etc
 - Creating a core "NEC runner" to which I can add:
     - code to optimise/sweep any parameter set based on any target parameter (gain, VSWR, segment current, feedline common mode current ....)
     - bespoke plotting such as delta (B minus A) and resolving into custom polarisation definitions
     - whatever else I think of

## Features

- **Component-based antenna construction**: Easily create antennas using predefined components.
- **Automatic wire joining**: Automatically connects wires that intersect, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **More coming soon**: See next steps/future plans below.
- **Extensible design**: It's written in Python, so you can use the core and add your own code

### ⚠️ **Note:** NECBOL is a very new project and the API is likely to change significantly in upcoming versions. Please expect some instability. And, note that I still have a lot to learn about Python and especially GitHub processes.

![Capture](https://github.com/user-attachments/assets/c83263d2-cdf4-41bd-961c-ca787555a9e0)

## Example Usage
This is the code that built the example above

```python
from nec_lib.nec_model import NECModel
from nec_lib import geometry_builder
from nec_lib import rf_utils
from nec_lib import wire_viewer

def build_contraspiral(d_mm, l_mm, main_wire_diameter_mm, helix_sep_mm, cld_mm, cl_alpha, cl_spacing_mm):
    global model


    coupling_loop_wire_diameter_mm = 2.0
    
    bottom_helix = antenna_components.helix(diameter_mm = d_mm,
                                     length_mm=l_mm,
                                     pitch_mm = l_mm/2,
                                     sense="RH",
                                     segments_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)

    top_helix = antenna_components.helix(diameter_mm = d_mm,
                                     length_mm=l_mm,
                                     pitch_mm = l_mm/2,
                                     sense="LH",
                                     segments_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)
    top_helix.translate(0,0, l_mm/1000 + helix_sep_mm/1000)

    link = antenna_components.connector(bottom_helix,71.99,top_helix,0,main_wire_diameter_mm)
    
    coupling_loop = antenna_components.circular_loop_with_feedpoint(diameter_mm = cld_mm,
                                                                    segments=36,
                                                                    wire_diameter_mm = coupling_loop_wire_diameter_mm)

    cl_offset_z = cl_alpha*l_mm/1000
    cl_offset_x = (d_mm - cld_mm - coupling_loop_wire_diameter_mm - main_wire_diameter_mm)/2000
    cl_offset_x -= cl_spacing_mm/1000
    coupling_loop.translate(cl_offset_x, 0, cl_offset_z)

    model.add(bottom_helix)
    model.add(coupling_loop)
    model.add(top_helix)
    model.add(link)

```

## Next steps / future plans
- add more geometry elements
- look at adding a wires class
- optimiser
    - gain in a certain direction
    - vswr
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - target antenna parameters plus stretch / warp / sheer the 3D geometry
- Clutter / environment objects
    - dielectric slab (for brick walls, GRP panels etc)
    - other antennas
- Error handling (at least stop if NEC output file indicates a problem)
- Automated A/B compares
    - Over ground vs free space
    - With / without specified feature
- Advanced graphing:
    - A minus B graphs
