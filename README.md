# NECBOL

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

I wrote it primarily for my own use for the reasons below, but I think it's good enough now to share so that other people can make use of it.
 - Not having to think about splitting wires into three-way junctions
 - Being able to view the geometry easily & in the same way whether it's in free space at Z=0 or 10m above a specified ground
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

![Capture](https://github.com/user-attachments/assets/1402e307-4db4-4362-afc4-cbeecfe81cee)


## 🛠 Installation

This is an early-stage project without a formal installer yet.

For now, the easiest way to get started is:

1. **Download or clone the repository**:
   ```bash
   git clone https://github.com/G1OJS/NECBOL.git
   cd NECBOL

2. **Use the files in:**
   - nec_lib/ – the main library code
   - examples/ – starting points you can adapt

Open and modify the example scripts to suit your needs.
**Tip:** Look inside nec_lib/geometry_builder.py to see which antenna components are currently available and how to use them. The goal is to make this library self-documenting in the future.

## Example Usage
This is the code that built the example above

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

def build_contraspiral(d_mm, l_mm, main_wire_diameter_mm, helix_sep_mm, cld_mm, cl_alpha, cl_spacing_mm):
    global model


    coupling_loop_wire_diameter_mm = 2.0
    
    bottom_helix = antenna_components.helix(diameter_m = d_mm /1000,
                                     length_m = l_mm /1000,
                                     pitch_m = l_mm /2000,
                                     sense="RH",
                                     wires_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)

    top_helix = antenna_components.helix(diameter_m = d_mm /1000,
                                     length_m = l_mm /1000,
                                     pitch_m = l_mm /2000,
                                     sense="LH",
                                     wires_per_turn=36,
                                     wire_diameter_mm = main_wire_diameter_mm)
    top_helix.translate(0,0, l_mm/1000 + helix_sep_mm/1000)

    link = antenna_components.connector(bottom_helix, 71, 1, top_helix, 0, 0, main_wire_diameter_mm)
    
    coupling_loop = antenna_components.circular_arc(diameter_m = cld_mm /1000,
                                                    arc_phi_deg = 360,
                                                    n_wires=36,
                                                    wire_diameter_mm = coupling_loop_wire_diameter_mm)
    
    model.place_feed(coupling_loop, feed_alpha_object=0)

    cl_offset_z = cl_alpha*l_mm/1000
    cl_offset_x = (d_mm - cld_mm - coupling_loop_wire_diameter_mm - main_wire_diameter_mm)/2000
    cl_offset_x -= cl_spacing_mm/1000
    coupling_loop.translate(cl_offset_x, 0, cl_offset_z)

    model.add(bottom_helix)
    model.add(coupling_loop)
    model.add(top_helix)
    model.add(link)
    


model = NECModel(working_dir="..\\nec_wkg",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)


for i in range(-5, 5):
    antenna_components = geometry_builder.components()
    d_mm = 160.5
    l_mm = 159
    wd_mm = 8
    helix_sep_m = 140
    cld_mm = 78
    cl_spacing_mm = 2
    cl_alpha=0.495
    parameter = cl_alpha *(1 + 0.01 *i)
    cl_alpha = parameter
    model.start_geometry()
    build_contraspiral(d_mm, l_mm, wd_mm, helix_sep_m, cld_mm, cl_alpha, cl_spacing_mm)
    model.write_nec_and_run()
    gains = model.gains()
    vswr = model.vswr()
    print(f"parameter {parameter:.3f}", gains, f"vswr:{vswr:.2f}")

wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title = "G1OJS Contraspiral")

print("Done")

```

## Next steps / future plans
- add more geometry elements
- optimiser
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - stretch / warp / sheer the 3D geometry
- Optimise the circular slot cube
- Add gamma feeds? Does this need a component? Look at adding squalo maybe.
    - this links to adding models for feedline and common mode current minimisation in optimiser.
- Wireframe viewer
    - arrow pointing to specified gain direction
    - arrow pointing to max gain direction (with dBi & maybe F/B)
- Clutter / environment objects
    - dielectric slab (for brick walls, GRP panels etc)
    - other antennas
- Error handling (at least stop if NEC output file indicates a problem)
- Automated A/B compares
    - Over ground vs free space
    - With / without specified feature
- Advanced graphing:
    - A minus B graphs
