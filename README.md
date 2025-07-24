# NECBOL [![PyPI Downloads](https://static.pepy.tech/badge/necbol)](https://pepy.tech/projects/necbol)

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine.

#### ⚠️ this repository may be ahead of the latest stable version: for the latest stable version, install from pip 
 - this may also mean that the examples here might not run correctly with the pip installed version, but this should be very temporary 

## Features

- **Component-based antenna construction**: Easily create antennas using predefined components.
- **Flexible length units**: Specify antenna dimensions in mm, m, cm, ft or in as needed.
- **Automatic wire joining**: Automatically connects wire ends to other wires, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **Current component library**: Helix, circular arc/loop, rectangular loop, straight wire, straight connector
- **Easy to place**: feedpoint, series RLC load(s), prarallel RLC load(s) specified in ohms, uH and pF
- **Easy to define meshed grids** which can also be joined edge to edge to create box structures (see the [car model](https://github.com/G1OJS/NECBOL/blob/main/example_handheld_in_a_car.py))
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
Documentation is work in progress. In the meantime:

* For a quick and basic overview, see the file [example_dipole_with_detailed_comments.py](https://github.com/G1OJS/NECBOL/blob/d22ee40ef966d9abb778667cd5b5979a98ed287b/example_dipole_with_detailed_comments.py) for a minimal explanation of how to use this framework.

* There are several more example files in the [examples folder](https://github.com/G1OJS/NECBOL/tree/main/examples) intended to highlight different aspects of necbol and different ways of doing similar things. You can copy these examples and modify to see how they work, or start your own from scratch.

* Automated documentation is [here](https://g1ojs.github.io/NECBOL/user_functions.html)
  
* Copies of the files installed by pip are in the [necbol folder](https://github.com/G1OJS/NECBOL/tree/main/necbol) on this repository. 
