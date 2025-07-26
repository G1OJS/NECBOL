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

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import copy

def show_wires_from_file(model, n_strands = 8, color = 'darkgoldenrod', alpha = 0.3):
    """
        Opens the specified nec input file (*.nec) and reads the geometry,
        then displays the geometry in a 3D projection. The feed is highligted in red.
        Loads are highlighted in green.
    """
    model_tmp = copy.deepcopy(model)
    model_tmp.wires = []
    with open(model.nec_in, 'r') as f:
        for line in f:
            if line.startswith("GW"):
                parts = line.strip().split()
                if len(parts) >= 9:
                    # NEC input is: GW tag seg x1 y1 z1 x2 y2 z2 radius
                    x1, y1, z1 = map(float, parts[3:6])
                    x2, y2, z2 = map(float, parts[6:9])
                    tag = int(parts[1])
                    radius = parts[9]
                    model_tmp.wires.append(((x1, y1, z1), (x2, y2, z2), tag, radius))
    _show_wires(model_tmp, n_strands, color, alpha)


def _show_wires(model, n_strands, color, alpha):

    print("Drawing geometry. Please close the geometry window to continue.")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    title = "Geometry for " + model.model_name

    s,c = _trig(n_strands)

    for start, end, tag, radius in model.wires:
        wire_color = color
        if (tag == model.EX_tag):
            wire_color = 'red'
        if (tag in [load['iTag'] for load in model.LOADS]):
            wire_color = 'green'
        _render_wire(ax, start, end, radius, s,c, color = wire_color, alpha=alpha)

    plt.draw()  # ensure autoscale limits are calculated

    # Get axis limits
    xlim, ylim, zlim = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    mids = [(lim[0] + lim[1]) / 2 for lim in (xlim, ylim, zlim)]
    spans = [lim[1] - lim[0] for lim in (xlim, ylim, zlim)]
    max_range = max(spans)

    # Set equal range around each midpoint
    ax.set_xlim(mids[0] - max_range/2, mids[0] + max_range/2)
    ax.set_ylim(mids[1] - max_range/2, mids[1] + max_range/2)
    ax.set_zlim(mids[2] - max_range/2, mids[2] + max_range/2)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    if (model.vswr is not None):
        fig.figure.text(0.02,0.05,f"Vswr: {model.vswr:.2f} ")
    if (model.max_total_gain is not None):
        fig.figure.text(0.02,0.1,f"Max total gain: {model.max_total_gain:.2f} dBi")
    
    plt.tight_layout()

    plt.show()
    



def _trig(n_strands):
    if(n_strands <2):
        return([0],[0]) # dummy values not used
    angles = np.linspace(0, 2*np.pi, n_strands, endpoint=False)
    cosines = np.cos(angles)
    sines = np.sin(angles)
    return sines, cosines

def _fast_perpendicular(v, threshold=100):
    vx, vy, vz = abs(v[0]), abs(v[1]), abs(v[2])
    if threshold * vz > vx and threshold * vz > vy:
        # v is nearly aligned with z-axis; project to XZ
        u = np.array([-v[2], 0.0, v[0]])
    else:
        # project to XY
        u = np.array([-v[1], v[0], 0.0])
    return u 

def _render_wire(ax, start, end, radius, sines,cosines, color, alpha):
    if(len(sines) <2):
        s = start
        e = end
        ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color=color, alpha = alpha)
        return
    
    axis = np.array(end) - np.array(start)
    fast_perp = _fast_perpendicular(axis)
    ortho_perp = np.cross(axis, fast_perp)  # axis × u
    u = (float(radius) * fast_perp) / np.linalg.norm(fast_perp)
    v = (float(radius) * ortho_perp) / np.linalg.norm(ortho_perp)
    # Generate strand offsets by rotating u around axis
    for i, s in enumerate(sines):
        offset = s * u + cosines[i]* v
        s = np.array(start) + offset
        e = np.array(end) + offset
        ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color=color, alpha = alpha)





