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

    fig = plt.figure()
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

