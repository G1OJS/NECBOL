# NECBOL

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

## ⚠️ VERSION V2.0.0 has some limited function name and module name changes
If you have been using V1.0.0 with your own python files, you'll need to change the import statements and the name of the wire viewer function.
See the file [CHANGES from V1.0.0.md](https://github.com/G1OJS/NECBOL/blob/22d1231ab0b61628b26277852affff68ede150da/CHANGES%20from%20V1.0.0.md) for details.

## Features

- **Component-based antenna construction**: Easily create antennas using predefined components.
- **Flexible length units**: Specify antenna dimensions in mm, m, cm, ft or in as needed.
- **Automatic wire joining**: Automatically connects wires that intersect, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **Current component library**: Helix, circular arc/loop, rectangular loop, straight wire, straight connector
- **Easy to place**: feedpoint, series RLC load(s), prarallel RLC load(s) specified in ohms, uH and pF
- **Dielectric sheet model**: currently experimental, not validated, built in to a flat sheet geometry component
- **Optimiser**: Optimise VSWR and / or Gain in a specified direction 
- **More coming soon**: See [next steps/future plans](https://github.com/G1OJS/NECBOL/blob/main/TO_DO.md)
- **Extensible design**: It's written in Python, so you can use the core and add your own code
- **Example files**: Simple dipole, Hentenna with reflector with example parameter sweep, Circular version of Skeleton Slot Cube with Optimiser code

![Capture](https://github.com/user-attachments/assets/1402e307-4db4-4362-afc4-cbeecfe81cee)

### ⚠️ **Note:** NECBOL is a very new project, and my first released using pip. Code comments are work in progress, and I have yet to decide how to add a user guide.

## 🛠 Installation

Install using pip: open a command window and type

```
pip install necbol
```

Copies of the files installed by pip are in the folders on this repository - see the Python files example_ ... and modify to suit your needs.
**Tip:** Look inside necbol/components.py to see which antenna components and modification methods are currently available. 

## User Guide
See the file example_minimal_example_dipole_with_detailed_comments.py for a minimal explanation of how to use this framework. 
Browse the other examples as needed, and see the comments in the necbol/*.py files which are currently being written. 

