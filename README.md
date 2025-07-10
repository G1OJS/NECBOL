# NECBOL

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

I wrote it primarily for my own use for the reasons below, but I think it's good enough now to share so that other people can make use of it.
 - Not having to think about splitting wires into three-way junctions when I need to join one wire to another (e.g. feeding a hentenna)
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
- **Flexible length units**: Specify antenna dimensions in mm, m, cm, ft or in as needed.
- **Automatic wire joining**: Automatically connects wires that intersect, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **Current component library**: Helix, circular arc/loop, rectangular loop, straight wire, straight connector
- **Easy to place**: feedpoint, series RLC load(s), prarallel RLC load(s) specified in ohms, uH and pF
- **Optimiser**: Optimise VSWR and / or Gain in a specified direction 
- **More coming soon**: See next steps/future plans below.
- **Extensible design**: It's written in Python, so you can use the core and add your own code
- **Example antennas**: Hentenna, hentenna with reflector, G1OJS Contraspiral, Circular version of Skeleton Slot Cube

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

## User Guide
See the file minimal_example_dipole_with_detailed_comments.py in the examples folder for a minimal explanation of how to use this framework. 
Browse the other examples as needed, and see the comments in the nec_lib/*.py files which are currently being written. 

## Next steps / future plans
- add more geometry elements
- optimiser
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - stretch / warp / sheer the 3D geometry
- Add gamma feeds? Does this need a component? Look at adding squalo maybe.
    - this links to adding models for feedline and common mode current minimisation in optimiser.
- Wireframe viewer
    - arrow pointing to specified gain direction
    - arrow pointing to max gain direction (with dBi & maybe F/B)
- Clutter / environment objects
    - dielectric slab (for brick walls, GRP panels etc)
    - other antennas
- Automated A/B compares
    - Over ground vs free space
    - With / without specified feature
- Advanced graphing:
    - A minus B graphs
