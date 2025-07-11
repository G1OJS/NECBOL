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


def parse_nec_wires(file_path):
    wires = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith("GW"):
                parts = line.strip().split()
                if len(parts) >= 9:
                    # NEC input is: GW tag seg x1 y1 z1 x2 y2 z2 radius
                    x1, y1, z1 = map(float, parts[3:6])
                    x2, y2, z2 = map(float, parts[6:9])
                    tag = int(parts[1])
                    wires.append(((x1, y1, z1), (x2, y2, z2), tag))
    return wires

def view_nec_input(file_path, ex_tag, color='blue', title = "3D Viewer"):
    wires = parse_nec_wires(file_path)
    view_wires(wires, ex_tag, title, color=color)


def view_wires(wires, ex_tag, title, color='blue'):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    print("Drawing geometry. Please close the geometry window to continue.")
    fig = plt.figure(label = 'Please close this window to continue')
    ax = fig.add_subplot(111, projection='3d')

    for start, end, tag in wires:
        ax.plot(*zip(start, end), color=color if (tag!=ex_tag) else 'red')

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
    
    plt.tight_layout()
    plt.show()

