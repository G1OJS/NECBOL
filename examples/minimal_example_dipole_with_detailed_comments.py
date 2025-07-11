"""
This file is part of the "NECBOL Plain Language Python NEC Runner"
Copyright (c) 2025 Alan Robinson G1OJS

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
  This is a minimal example of how to use the NECBOL library to model an antenna,
  with comments explaining how the NECBOL interface works.
"""

# These first lines are necessary at the moment because NECBOL is not a package installed using pip install
# They insert the location of this file into the system path so that the nec_wkg directory can be made in
# an adjacent folder
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# These lines import NECBOL from the folder nec_lib, which should be in the same folder as this file
from nec_lib.nec_wrapper import NECModel
from nec_lib import geometry_builder
from nec_lib import wire_viewer

# Start an antenna model called model (it can be called anything acceptable as a Python variable),
# specifying where the working folder should be made, and where the nec executable is on your system
model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "Vertical Dipole",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)

# These lines set the basic parameters for the model
# Wire conductivity. Can be omitted if perfect conductivity is OK to assume
model.set_wire_conductivity(sigma = 58000000)
# Frequency in MHz
model.set_frequency(MHz = 144.2)
# Frequency in azimuth and elevation of gain point (leave at 0,0 if you only want vswr)
model.set_gain_point(azimuth = 0, elevation = 3)
# Ground type. Currently limited to simple choices. If eps_r = 1 and sigma = 0, or if you omit this line,
# nec is told to use no ground. Othewise you should set the origin height so that the antenna reference
# point X,Y,Z = (0,0,0) is set to be the specified distance above ground.
# You can specify this in m, mm, cm, in, or ft (e.g. origin_height_ft = 30.33)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0) 

# Get a 'copy' of the geometry builder class called antenna_components (again, you can change this name if desired)
antenna_components = geometry_builder.components()

# Tell the nec interface to clear any existing geometries and start a new one
# This clears only geometry definitions, not the definitions made above
# It's a mandatory line even if there is no existing geometry to clear because it initilises various things
model.start_geometry()

# Define your antenna structure. Here you must use named arguments (length =, wire_diameter =)
# but the _mm can be replaced by _m, _cm, _ft, _in if you want to work in other unit systems,
# and you can mix and match if needed (length_ft = 13.5, wire_diameter_cm = 1.3)
# NOTE - although it seems like a lot of work to get to this point, you've now defined a lot of
# parameters that won't change as your antenna definition grows from the single line below
# into some complicated antenna definitions, and the idea is that that is as easy as doing this next line:
dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)

# Now tell the nec interface where you're going to feed the antenna from
# This line says you want to feed on the geometry object called dipole,
# on the first wire in that structure, and halfway along that wire
# If you know about nec segmentation, this automatically inserts a segment
# to contain the feed, resulting in the previously 1-wire geometry object becoming a
# three wire object with all wires segmentes using the same segment length (currently hard coded to lambda / 40
# If you *don't* know about nec segmentation, one goal of this project is that you shouldn't *need* to know.
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)

# Add the dipole (and its feed definition) to the model - in a sense this says
# "I've done defining the dipole, please add it to the model"
model.add(dipole)

# now write all of the above definitions into the nec input file
model.write_nec()
# now ask nec to analyse the nec input file and produce a nec output file
model.run_nec()
# get gains (H, V and Total) and vswr(calculated from impedance) from the nec output file
gains = model.gains()
vswr = model.vswr()
# print the results
print(gains, f"vswr:{vswr:.2f}")

# show the geometry (if desired, you can do this immediately following model.write_nec(),
# but you'll have to close the geometry window if you want anything to happen afterwards)
wire_viewer.view_nec_input(model.nec_in, model.EX_TAG, title=model.model_name)


