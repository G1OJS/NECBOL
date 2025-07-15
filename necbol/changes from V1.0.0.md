Changes made

1. Added flexi-helix (simplify this and see if it's worth keeping)

2. Tidied up optimiser screen output when using non-tty apps to run the code
   (use the tty=False keyword argument when calling optimiser)

3. Changed default ground in GE to -1. Corrected docstring (removed 'and conductivity = 0')

4. Added dielectric / conductive sheets.

5. Restructured library modules to clarify module purposes, create 'components.py' holding *only* components, and avoid need for passing parameters between nec_wrapper and geometry_builder

To Do

1. Show height above ground on the XY plane in wire viewer, also identify loads.

2. Add warning if lowest part of antenna is below ground.

 Make an example with copy & rotate, make an aircon duct or something with a 2m loft antenna nearby.



Issues noted
1.    _place_feed_or_load needs extra logic to determine if one of the three new wires has a very small length, in which case just grow the centre segment a little

2. It would be a good idea to pre-empt NEC warnings such as segment length< diameter / n etc as these could be explained/handled better

3. parametrise the starting tag of LOADS, and add error trap if main wires encroach. Potentially change the default starting tag for *wires* to say 1000 and put feed and loads below.
