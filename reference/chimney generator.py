import numpy as np

# Parameters
F = 144.2   # f MHz
W = 0.36    # Chimney width m (along x)
D = 0.42    # Chimney depth m (along y)
H = 1.0     # Chimney height (length) m
B = 8.9     # Base of chimney agl in m   
T = 0.005   # Wall thickness
E = 2.2     # Wall epsilon r
dGwl = 0.02  # Wanted Grid cell size in wavelengths

# calculated parameters
dG = dGwl * 300/F
dG = 0.001* int(dG*1000)
nX = int(W / dG) + 1
nY = int(D / dG) + 1
nZ = int(H / dG) + 1

W = (nX-1)*dG
D = (nY-1)*dG
H = (nZ-1)*dG

E0 = 8.854188 * 1e-12
CD = E0*(E-1)*T

# Start NEC file
nec_lines = []
nec_lines.append("CM Chimney\n")
nec_lines.append("CE\n")

wire_radius = T/2
tag = 777

# Create X panels
for x in [-W/2, W/2]:
    for i in range(1, nY-1):
        x1, y1, z1, x2, y2, z2 = [x, -D/2+i*dG, B+0, x, -D/2+i*dG, B+H]
        nSegs = nZ-1
        nec_lines.append(f"GW {tag} {nSegs} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {wire_radius}\n")
    for i in range(nZ):
        x1, y1, z1, x2, y2, z2 = [x, -D/2, B+i*dG, x, D/2, B+i*dG]
        nSegs = nY-1
        nec_lines.append(f"GW {tag} {nSegs} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {wire_radius}\n")

# Create Y panels
for y in [-D/2, D/2]:
    for i in range(nX):
        x1, y1, z1, x2, y2, z2 = [-W/2+i*dG, y, B+0, -W/2+i*dG, y, B+H]
        nSegs = nZ-1
        nec_lines.append(f"GW {tag} {nSegs} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {wire_radius}\n")
    for i in range(nZ):
        x1, y1, z1, x2, y2, z2 = [-W/2, y, B+i*dG, W/2, y, B+i*dG]
        nSegs = nX-1
        nec_lines.append(f"GW {tag} {nSegs} {x1:.3f} {y1:.3f} {z1:.3f} {x2:.3f} {y2:.3f} {z2:.3f} {wire_radius}\n")


# add capacitive loads to chimney grids
nec_lines.append(f"LD 1 {tag} 0 0 0 0 {CD}\n")

# Write to file
with open("Chimney.nec", "w") as f:
    f.writelines(nec_lines)

print("NEC file 'Chimney.nec' generated.")
