Issues noted
1.    _place_feed_or_load needs extra logic to determine if one of the three new wires has a very small length, in which case just grow the centre segment a little

2. It would be a good idea to pre-empt NEC warnings such as segment length< diameter / n etc as these could be explained/handled better

3. parametrise the starting tag of LOADS, and add error trap if main wires encroach. Potentially change the default starting tag for *wires* to say 1000 and put feed and loads below.

To Do
1. Show height above ground on the XY plane in wire viewer, also identify loads.

2. Add warning if lowest part of antenna is below ground.

3. Make an example with copy & rotate, make an aircon duct or something with a 2m loft antenna nearby.


## Next steps / future plans/ideas
- add more geometry elements
- change GE default to 0 / -1 rather than 0 / +1
- tidy up optimiser text output when not using tty
- optimiser
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - stretch / warp / sheer the 3D geometry
    - bandwidth
- Add gamma feeds? Does this need a component? Look at adding squalo maybe.
    - this links to adding models for feedline and common mode current minimisation in optimiser.
- Wireframe viewer
    - arrow pointing to specified gain direction
    - arrow pointing to max gain direction (with dBi & maybe F/B)
- Clutter / environment objects
    - dielectric slab (for brick walls, GRP panels etc)
    - other antennas
