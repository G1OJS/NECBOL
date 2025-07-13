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
import mpl_toolkits.mplot3d

def parse_model_text(model):

    wires = []
    for line in model.model_text.splitlines():
        print(line)
        if line.startswith("GW"):
            parts = line.strip().split()
            if len(parts) >= 9:
                # NEC input is: GW tag seg x1 y1 z1 x2 y2 z2 radius
                x1, y1, z1 = map(float, parts[3:6])
                x2, y2, z2 = map(float, parts[6:9])
                tag = int(parts[1])
                wires.append(((x1, y1, z1), (x2, y2, z2), tag))
    return wires

def add(model, antenna_components):
    print("add")
    
    w = antenna_components.wire_Z(length_mm = 2000, wire_diameter_mm = 1.0)
    model.add(w)


def draw_nec(model):
    global plt,fig, ax

    print("draw")
    fig.clear()
    ax = fig.add_subplot(111, projection='3d')
    wires = parse_model_text(model)
    for start, end, tag in wires:
        print("draw wire")
        ax.plot(*zip(start, end), color='blue' if (tag!=model.EX_TAG) else 'red')
    plt.draw()  # ensure autoscale limits are calculated
    xlim, ylim, zlim = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    mids = [(lim[0] + lim[1]) / 2 for lim in (xlim, ylim, zlim)]
    spans = [lim[1] - lim[0] for lim in (xlim, ylim, zlim)]
    max_range = max(spans)
    ax.set_xlim(mids[0] - max_range/2, mids[0] + max_range/2)
    ax.set_ylim(mids[1] - max_range/2, mids[1] + max_range/2)
    ax.set_zlim(mids[2] - max_range/2, mids[2] + max_range/2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.ion()
    plt.show()
    plt.draw()

    return plt


def build(model, antenna_components, title):
    from matplotlib.backend_bases import MouseButton
    global plt,fig
    label=""
    fig = plt.figure(label)
    plt = draw_nec(model)
    ends = [None, None]

    
    def on_move(event):

        pass

    def on_click(event):
        if event.button is MouseButton.RIGHT:
            if event.inaxes:
                s = ax.format_coord(event.xdata, event.ydata)
                p=get_plane_coords(s)
                if(p):
                    if(ends[0]):
                        ends[1]=p
                        ax.plot([ends[0][0],ends[1][0]],[ends[0][1],ends[1][1]],[ends[0][2],ends[1][2]])
                        ends[0] = None
                    else:
                        ends[0]=p
                    print(ends)
                    
            #add(model, antenna_components)
            #plt=draw_nec(model)

    binding_id = plt.connect('motion_notify_event', on_move)
    plt.connect('button_press_event', on_click)
        
def get_plane_coords(s):
    s=s.split(",")
    if('elevation' in s[0]):
        return None
    xyz=[0,0,0]
    for valstr in s:
        if('pane' in valstr):
            continue
        ordinate = valstr.split("=")[0].strip()
        i = ['x','y','z'].index(ordinate)
        
        xyz[i]=float(valstr.split("=")[1].replace('−','-'))
    if(xyz[1]==0):
        xyz[1]=1
    return xyz



