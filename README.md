# NECBOL

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

### ⚠️ some function name and module name changes were made at version V2.0.0
If you have been using previous versions with your own python files, you'll need to change the import statements and the name of the wire viewer function.
See the file [CHANGES from V1.0.0.md](https://github.com/G1OJS/NECBOL/blob/22d1231ab0b61628b26277852affff68ede150da/CHANGES%20from%20V1.0.0.md) for details.

## Features

- **Component-based antenna construction**: Easily create antennas using predefined components.
- **Flexible length units**: Specify antenna dimensions in mm, m, cm, ft or in as needed.
- **Automatic wire joining**: Automatically connects wires that intentionally intersect via the connector object, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **Current component library**: Helix, circular arc/loop, rectangular loop, straight wire, straight connector
- **Easy to place**: feedpoint, series RLC load(s), prarallel RLC load(s) specified in ohms, uH and pF
- **Dielectric sheet model**: currently experimental, not validated, built in to a flat sheet geometry component
- **Optimiser**: Optimise VSWR and / or Gain in a specified direction 
- **More coming soon**: See [next steps/future plans](https://github.com/G1OJS/NECBOL/blob/main/TO_DO.md)
- **Extensible design**: It's written in Python, so you can use the core and add your own code
- **Example files**: Simple dipole, Hentenna with reflector with example parameter sweep, Circular version of Skeleton Slot Cube with Optimiser code

![Capture](https://github.com/user-attachments/assets/f8d57095-cbbd-4a02-9e40-2d81520a3799)

## 🛠 Installation

Install using pip: open a command window and type

```
pip install necbol
```
## User Guide
Copies of the files installed by pip are in the [necbol folder](https://github.com/G1OJS/NECBOL/tree/main/necbol)) on this repository. There are several example files intended to highlight different aspects of necbol and different ways of doing similar things. You can copy these examples and modify to see how they work, or start your own from scratch.

**Tip:** Look inside necbol/components.py to see which antenna components and modification methods are currently available. I'm planning to make an automated help file from the comments inside this file (and then the others).

For a quick and basic overview, see the file [example_dipole_with_detailed_comments.py](https://github.com/G1OJS/NECBOL/blob/d22ee40ef966d9abb778667cd5b5979a98ed287b/example_dipole_with_detailed_comments.py) for a minimal explanation of how to use this framework. 

