import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, r"C:\Users\drala\Documents\Projects\GitHub\NECBOL")

from necbol.analyser import _write_radiation_pattern, _compute_full_farfield_metrics

def far_field_total(theta, h, R_func, k=2*np.pi, r=1000):
    """
    Far-field E_theta at angle theta due to a dipole over an interface.

    Parameters:
        theta : ndarray of angles 
        h     : dipole height above interface
        R_func: function R(theta) giving reflection coefficient
        k     : wave number (default 2π)
        r     : far-field radius (default 1000λ)

    Returns:
        E_theta : complex field at each theta
    """
    theta = np.radians(theta_deg)
    E0 = (1j * np.sin(theta)) / (4 * np.pi * r)  # Omit I*l, just relative
    phase_direct = np.exp(1j * k * r)
    phase_reflect = np.exp(1j * k * (r + 2 * h * np.cos(theta)))  # Extra path from image

    return E0 * (phase_direct + R_func(theta) * phase_reflect)

def R_fresnel_TM_dielectric_half_space(theta, eps_r):
    """
    Fresnel reflection coefficient for TM (parallel) polarization
    for air-to-dielectric interface, assuming dipole in air.
    
    Parameters:
        theta : array of incidence angles (radians)
        eps_r : relative permittivity of the dielectric

    Returns:
        R : complex reflection coefficient
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    sin_theta_t = sin_theta / np.sqrt(eps_r)
    # Guard against total internal reflection (shouldn't happen here)
    under_root = eps_r - sin_theta**2
    sqrt_term = np.sqrt(under_root + 0j)  # add 0j to allow complex sqrt

    numerator = eps_r * cos_theta - sqrt_term
    denominator = eps_r * cos_theta + sqrt_term
    return numerator / denominator

def R_fresnel_TE_dielectric_half_space(theta, eps_r):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    sqrt_term = np.sqrt(eps_r - sin_theta**2 + 0j)
    numerator = cos_theta - sqrt_term
    denominator = cos_theta + sqrt_term
    return numerator / denominator

def R_dielectric_slab_TM(theta, eps_r, thickness, wavelength=1.0):
    """
    TM-polarized reflection coefficient from a dielectric sheet in free space.

    Parameters:
        theta     : array of incidence angles (radians)
        eps_r     : relative permittivity of sheet
        thickness : sheet thickness in wavelengths (i.e., d/λ)
        wavelength: operating wavelength (default 1.0 for normalization)

    Returns:
        R_slab    : complex reflection coefficient
    """
    k0 = 2 * np.pi / wavelength
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    # Transmitted angle (Snell's law)
    sin_theta_t = sin_theta / np.sqrt(eps_r)
    cos_theta_t = np.sqrt(1 - sin_theta_t**2 + 0j)

    # Fresnel coefficient at interface (TM polarization)
    R12 = (eps_r * cos_theta - cos_theta_t) / (eps_r * cos_theta + cos_theta_t)
    R23 = -R12  # Air on both sides, so symmetry

    # Phase shift through slab
    phi = k0 * thickness * np.sqrt(eps_r - sin_theta**2 + 0j)

    numerator = R12 + R23 * np.exp(2j * phi)
    denominator = 1 + R12 * R23 * np.exp(2j * phi)
    return numerator / denominator 


def plot(dB, theta_deg):
    angle_rad = np.radians(90-theta_deg)
    fig, ax1 = plt.subplots(subplot_kw={'projection': 'polar'})    
    ax1.plot(angle_rad, dB, label='|E_theta| (Magnitude)')
    ax1.set_xlabel('Theta (degrees)')
    ax1.set_ylabel('Magnitude', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)
    ax1.set_ylim(max_dB-30,max_dB)
    plt.title('Far-Field Total E_theta over Dielectric Interface')
    fig.tight_layout()
    plt.show()



theta_deg = np.linspace(0, 180, 181) + .1
h = 0.25  
eps_r = 4.0
E_theta = far_field_total(theta_deg, h, lambda th: R_dielectric_slab_TM(th, 1.001, 0.001, wavelength=1.0))
norm = 10**(-16.7/20)
E_theta =  E_theta / E_theta[88]


pattern = []
for i, t in enumerate(theta_deg):
    pattern_vals = _compute_full_farfield_metrics(E_theta[i], 0)
    pattern_vals.update({'azimuth_deg':0})
    pattern_vals.update({'elevation_deg':90 - t})
    pattern.append(pattern_vals)
    
_write_radiation_pattern(pattern, r"C:\4nec2\out\analytic.out")
