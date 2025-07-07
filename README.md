# Python Library to run NEC
This is a new work in progress, but already provides:
* Easy way to build antennas using a component library (rods/wires, loops etc)
* Automatic joining of wires that intersect (currently if a wire end lies on another wire)
* Easy setting of frequency, ground, azimuth and elevation of pattern point
* Extendable to sweep and optimise, tabulate and plot
![Capture](https://github.com/user-attachments/assets/de95948a-58b6-4bb3-8367-dc35639638fe)

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
