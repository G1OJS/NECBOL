## Issues noted
Moved to GitHub issues for more visible tracking

## To DO
### Examples
- Turn some of these into case studies with screenshots and narrative

### Wireframe viewer
- Show height above ground on the XY plane
- Highlight loads
- Add warning if lowest part of antenna is below ground
- arrow pointing to specified gain direction
- For these, probably best to have them consciously requested by the user, i.e. passed from gain collection to the plotting function with a kwarg
    - arrow pointing to max gain direction (needs a phi cut)
    - Add vswr

### NEC runner
- Modify "gains" getter to report max gain by default when a Phi cut is specified

### Geometry
- Add a 'bend' method to allow the sheet grids to model rounded edges
- Validate the dielectric sheet model

## Future plans/ideas
- further restructuring to enable load segment deconfliction (ensure nec doesn't silently overwrite loads). Store required loads in NECmodel as variables for later checking instead of just writing the LD card strings to LOADS.
- optimiser
    - polarisation purity
    - current on a certain segment
    - feedline current (needs a feedline object tagged)
    - stretch / warp / sheer the 3D geometry
    - bandwidth
- Add gamma feeds? Does this need a component? Look at adding squalo maybe.
    - this links to adding models for feedline and common mode current minimisation in optimiser.
