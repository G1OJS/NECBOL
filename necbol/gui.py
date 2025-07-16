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

def show_wires(wires, ex_tag, title, color='blue'):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    print("Drawing geometry. Please close the geometry window to continue.")
    fig = plt.figure()
 #   fig.canvas.manager.set_window_title('Please close this window to continue')
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
    

def show_wires_from_file(file_path, ex_tag, color='blue', title = "3D Viewer"):
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
    show_wires(wires, ex_tag, title, color=color)


def plot_gain(pattern_data, elevation_deg, component, polar=True):
    import matplotlib.pyplot as plt
    import numpy as np

    # Filter data for fixed elevation (theta)
    theta_cut = 90 - elevation_deg
    az_cut = [d for d in pattern_data if abs(d['theta'] - theta_cut) < 0.1]

    # Sort by phi (just in case)
    az_cut.sort(key=lambda d: d['phi'])

    # Extract azimuth (phi) and gain
    phi_deg = [d['phi'] for d in az_cut]
    gain_db = [d[component] for d in az_cut]

    title = f'{component} at elevation = {elevation_deg}°'

    if polar:
        phi_rad = np.radians(phi_deg)
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.plot(phi_rad, gain_db, label=title)
        ax.set_title(title)
        ax.grid(True)
        ax.set_theta_zero_location("N")  # 0° at top
        ax.set_theta_direction(-1)       # clockwise
        ax.set_rlabel_position(90)
        ax.legend(loc='lower right')
    else:
        plt.figure(figsize=(8, 4))
        plt.plot(phi_deg, gain_db, label=title)
        plt.xlabel('Azimuth φ (degrees)')
        plt.ylabel('Gain (dB)')
        plt.title('')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

    plt.show()




