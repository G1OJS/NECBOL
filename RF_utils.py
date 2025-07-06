
def vswr_from_z(z_in, z0=50):
    gamma = (z_in - z0) / (z_in + z0)
    return (1 + abs(gamma)) / (1 - abs(gamma))
