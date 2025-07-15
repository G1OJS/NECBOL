Issues noted
1. _place_feed_or_load needs extra logic to determine if one of the three new wires has a very small length, in which case just grow the centre segment a little
2. It would be a good idea to pre-empt NEC warnings such as segment length< diameter / n etc as these could be explained/handled better
3. parametrise the starting tag of LOADS, and add error trap if main wires encroach. Potentially change the default starting tag for *wires* to say 1000 and put feed and loads below.
4. Sometimes when nec reports errors, necbol stalls silently - check error trapping

To Do
1. Show height above ground on the XY plane in wire viewer, also identify loads.
2. Add warning if lowest part of antenna is below ground.
3. Wireframe viewer - arrow pointing to specified gain direction (possibly also max gain? would need to specify a phi cut rather than single point)
4. Add some more exciting examples - e.g. antennas with other antennas / objects nearby

## Next steps / future plans/ideas
- further restructuring to enable load segment deconfliction (ensure nec doesn't silently overwrite loads). Store required loads in NECmodel as variables for later checking instead of just writing the LD card strings to LOADS.
- optimiser
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - stretch / warp / sheer the 3D geometry
    - bandwidth
- Add gamma feeds? Does this need a component? Look at adding squalo maybe.
    - this links to adding models for feedline and common mode current minimisation in optimiser.
