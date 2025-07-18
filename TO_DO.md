## Issues noted
1. _place_feed_or_load needs extra logic to determine if one of the three new wires has a very small length, in which case just grow the centre segment a little - go back to this and test again
2. It would be a good idea to pre-empt NEC warnings such as segment length< diameter / n etc as these could be explained/handled better
3. Duplicated feed / load specifications may silently produce unexpected results (overwrite, sum etc). Need to revise the way cards are accumulated to capture intent once and then write the appropriate card(s) at the end.
4. Sometimes when nec reports errors, necbol stalls silently - check error trapping

## To DO
### Examples
- Turn some of these into case studies with screenshots and narrative

### Update gain collection
- delete gains
- rewrite  h_gain, v_gain, tot_gain, to call read_radiation_pattern and get gains at single gain az,el from there
- show examples with cost functions based around max_gain, min_gain in specified directions (error traps/warning or auto fix if these
  directions aren't requested
   
### Wireframe viewer
- Show height above ground on the XY plane
- Highlight loads
- Add warning if lowest part of antenna is below ground
- arrow pointing to specified gain direction
- For these, probably best to have them consciously requested by the user, i.e. passed from gain collection to the plotting function with a kwarg
    - arrow pointing to max gain direction (needs a phi cut)
    - Add vswr

### NEC runner
- add object name to end of nec GW line with a comment ' if possible
- Modify "gains" getter to report max gain by default when a Phi cut is specified

### Geometry
- Add a 'bend' method to allow the sheet grids to model rounded edges

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
