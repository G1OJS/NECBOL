# Python Library to run NEC
This is a new work in progress, but already provides:
* Easy way to build antennas using a component library (rods/wires, helices, loops etc)
* **Automatic joining of wires that intersect** (currently if a wire end lies on another wire)
* **Easily add a connector *from* object1-place1 *to* object2-place2**
* Easy setting of frequency, ground, azimuth and elevation of pattern point
* As the above is Python, write your own code to always show both over ground and free space etc
* Extendable to sweep and optimise, tabulate and plot

![Capture](https://github.com/user-attachments/assets/c83263d2-cdf4-41bd-961c-ca787555a9e0)

Next steps / future plans
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
