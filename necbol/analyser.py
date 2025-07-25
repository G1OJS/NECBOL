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


def vswr(model, Z0 = 50):
    """
        Return the antenna VSWR at the feed point assuming a 50 ohm system
        Or another value if specified
    """
    try:
        with open(model.nec_out) as f:
            while "ANTENNA INPUT PARAMETERS" not in f.readline():
                pass
            for _ in range(4):
                l = f.readline()
            if model.verbose:
                print("Z line:", l.strip())
            r = float(l[60:72])
            x = float(l[72:84])
    except (RuntimeError, ValueError):
        raise ValueError(f"Something went wrong reading input impedance from {nec_out}")

    z_in = r + x * 1j
    gamma = (z_in - Z0) / (z_in + Z0)
    return (1 + abs(gamma)) / (1 - abs(gamma))

def get_gains_at_gain_point(model):
    try:
        pattern = read_radiation_pattern(model.nec_out, model.az_datum_deg, model.el_datum_deg)
        gains_at_point = [d for d in pattern if (abs(d['elevation_deg'] - model.el_datum_deg) < 0.1) and (abs(d['azimuth_deg'] - model.az_datum_deg) < 0.1)][0]
        
    except (RuntimeError, ValueError):
        print("Trying to read gains at {azimuth_deg}, {elevation_deg}")
        raise ValueError(f"Something went wrong reading gains from {nec_out}")

    return gains_at_point

def read_radiation_pattern(filepath, azimuth_deg = None, elevation_deg = None):
    """
        Read the radiation pattern into a Python dictionary:
        'az_deg': float,
        'el_deg': float,
        'vert_gain_dBi': float,
        'horiz_gain_dBi': float,
        'total_gain_dBi': float,
        'axial_ratio_dB': float,
        'tilt_deg': float,
        'sense': string,
        'E_theta_mag': float,
        'E_theta_phase_deg': float,
        'E_phi_mag': float,
        'E_phi_phase_deg': float
    """
    data = []
    thetas = set()
    phis = set()
    in_data = False
    start_lineNo = 1e9
    with open(filepath) as f:
        lines = f.readlines()
    for lineNo, line in enumerate(lines):
        if ('RADIATION PATTERNS' in line):
            in_data = True
            start_lineNo = lineNo + 5

        if (lineNo > start_lineNo and line=="\n"):
            in_data = False
            
        if (in_data and lineNo >= start_lineNo):
            theta = float(line[0:9])
            phi = float(line[9:18])
            thetas.add(theta)
            phis.add(phi)
            if (elevation_deg is not None and theta != 90 - elevation_deg):
                continue
            if (azimuth_deg is not None and phi != azimuth_deg):
                continue
            data.append({
                'azimuth_deg': phi,
                'elevation_deg': 90 - theta,
                'vert_gain_dBi': float(line[18:28]),
                'horiz_gain_dBi': float(line[28:36]),
                'total_gain_dBi': float(line[36:45]),
                'axial_ratio_dB': float(line[45:55]),
                'tilt_deg': float(line[55:63]),
                'sense': line[63:72].strip(),
                'E_theta_mag': float(line[72:87]),
                'E_theta_phase_deg': float(line[87:96]),
                'E_phi_mag': float(line[96:111]),
                'E_phi_phase_deg': float(line[111:119])
            })

    if (len(data) == 0):
        print(f"Looking for gain at phi = {azimuth_deg}, theta = {90 - elevation_deg} in")
        print(f"Thetas = {thetas}")
        print(f"Phis = {phis}")
        raise EOFError(f"Failed to read needed data in {filepath}. Check for NEC errors.")
    return data


def _read_radiation_pattern(filepath, azimuth_deg = None, elevation_deg = None):

    """
        Read the radiation pattern into a Python dictionary:
        'az_deg': float,
        'el_deg': float,
        'E_theta_mag': float,
        'E_theta_phase_deg': float,
        'E_phi_mag': float,
        'E_phi_phase_deg': float
        'vert_gain_dBi': float,
        'horiz_gain_dBi': float,
        'total_gain_dBi': float,
        'rhcp_gain_dBi': float,
        'lhcp_gain_dBi': float,
        'axial_ratio_dB': float,
    """
    
    data = []
    thetas = set()
    phis = set()
    in_data = False
    start_lineNo = 1e9
    with open(filepath) as f:
        lines = f.readlines()
    for lineNo, line in enumerate(lines):
        if ('RADIATION PATTERNS' in line):
            in_data = True
            start_lineNo = lineNo + 5

        if (lineNo > start_lineNo and line=="\n"):
            in_data = False
            
        if (in_data and lineNo >= start_lineNo):
            theta = float(line[0:9])
            phi = float(line[9:18])
            thetas.add(theta)
            phis.add(phi)
            if (elevation_deg is not None and theta != 90 - elevation_deg):
                continue
            if (azimuth_deg is not None and phi != azimuth_deg):
                continue
            data.append({
                'azimuth_deg': phi,
                'elevation_deg': 90 - theta,
                'vert_gain_dBi': float(line[18:28]),
                'horiz_gain_dBi': float(line[28:36]),
                'total_gain_dBi': float(line[36:45]),
                'axial_ratio_dB': float(line[45:55]),
                'tilt_deg': float(line[55:63]),
                'sense': line[63:72].strip(),
                'E_theta_mag': float(line[72:87]),
                'E_theta_phase_deg': float(line[87:96]),
                'E_phi_mag': float(line[96:111]),
                'E_phi_phase_deg': float(line[111:119])
            })

    if (len(data) == 0):
        print(f"Looking for gain at phi = {azimuth_deg}, theta = {90 - elevation_deg} in")
        print(f"Thetas = {thetas}")
        print(f"Phis = {phis}")
        raise EOFError(f"Failed to read needed data in {filepath}. Check for NEC errors.")
    return data



def plot_total_gain(model):
    """
        This is a very basic plot routine providing polar and rectangular plots
        with gain range covering 40 dB max to min.
        Later versions of necbol will include more customisable plot functions
        and the ability to save output data in a suitable format for onward analysis
    """
    import matplotlib.pyplot as plt
    import numpy as np

    pattern_data = read_radiation_pattern(model.nec_out, elevation_deg = model.el_datum_deg)
    elevation_deg = model.el_datum_deg
    component = 'total_gain_dBi' 
        
    # Filter data for fixed elevation 
    print(f"Plotting gain for elevation = {elevation_deg}")
    az_cut = [d for d in pattern_data if abs(d['elevation_deg'] - model.el_datum_deg) < 0.1]

    # Extract azimuth (phi) and gain
    az_deg = [d['azimuth_deg'] for d in az_cut]
    gain_db = [d[component] for d in az_cut]
    max_gain = np.max(gain_db)

    title = f'{component} at elevation = {elevation_deg}° for {model.model_name}'

    az_rad = np.radians(az_deg)
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(az_rad, gain_db, label=title)
    ax.set_title(title)
    ax.grid(True)
    ax.set_rmax(max_gain)
    ax.set_rmin(max_gain-40)
    ax.set_rlabel_position(90)

    plt.show()


def plot_pattern_gains(pattern_data, azimuth_deg = None, elevation_deg = None, components = ['gain_total_dBi']):
    import matplotlib.pyplot as plt
    import numpy as np
        
    # Filter data for fixed elevation (theta)
    if(elevation_deg is not None):
        print(f"Plotting gain for elevation = {elevation_deg}")
        cut = [d for d in pattern_data if abs(d['elevation_deg'] - elevation_deg) < 0.1]
        angle_deg = [d['azimuth_deg'] for d in cut]
        title = f'elevation = {elevation_deg}°'

    # Filter data for fixed azimuth (phi)
    if(azimuth_deg is not None):
        print(f"Plotting gain for azimuth = {azimuth_deg}")
        cut = [d for d in pattern_data if abs(d['azimuth_deg'] - azimuth_deg) < 0.1]
        angle_deg = [d['elevation_deg'] for d in cut]
        title = f'azimuth = {azimuth_deg}°'
 
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    angle_rad = np.radians(angle_deg)
    v_gain_db = [d['vert_gain_dBi'] for d in cut]
    h_gain_db = [d['horiz_gain_dBi'] for d in cut]
    ax.plot(angle_rad, v_gain_db, label=title)
    ax.plot(angle_rad, h_gain_db, label=title)
    ax.set_title(title)
    ax.grid(True)
    
    vmax = max(v_gain_db)
    hmax = max(h_gain_db)

    print(vmax,hmax)
    pmax = max(vmax,hmax)
    
    ax.set_rmax(pmax)
    ax.set_rmin(pmax-40)
    ax.set_rlabel_position(90)

    # Enable interactive mode for non-blocking plotting
    plt.ion()

    # Display the plot window in non-blocking mode
    plt.show(block=False)


#==================================================================
# Internal functions
#==================================================================

import numpy as np
import copy

def _get_complex_component(pat_data, component):
    m = np.array([d[component + '_mag'] for d in pat_data])
    p = np.radians([d[component + '_phase_deg'] for d in pat_data])
    Z = m * np.exp(1j * p)
    return Z


def _plot_difference_field(model1, model2):
    # needs work to check if patterns don't match az, el 1:1 and if model datums are different
    pattern1 = read_radiation_pattern(model1.nec_out)
    pattern2 = read_radiation_pattern(model2.nec_out)
    diff = _subtract_field_patterns(pattern1, pattern2)
    plot_pattern_gains(diff, elevation_deg = model.el_datum_deg)

def _subtract_field_patterns(pat1, pat2):
    Z_theta_1 = _get_complex_component(pat1, 'E_theta')
    Z_theta_2 = _get_complex_component(pat2, 'E_theta')
    Z_phi_1 = _get_complex_component(pat1, 'E_phi')
    Z_phi_2 = _get_complex_component(pat2, 'E_phi')

    output_pattern = []
    for i, d in enumerate(pattern1):
        E_theta = Z_theta_1[i] - Z_theta_2[i]
        E_phi = Z_phi_1[i] - Z_phi_2[i]
        output_pattern.append(_compute_full_farfield_metrics(E_theta, E_phi))

    return output_pattern

import math
import cmath

def _compute_full_farfield_metrics(E_theta, E_phi):

    # Total field magnitude squared
    total_power = abs(E_theta)**2 + abs(E_phi)**2
    total_gain_dBi = 10 * math.log10(total_power) if total_power > 0 else -math.inf

    # RHCP and LHCP components
    E_rhcp = (E_theta - 1j * E_phi) / math.sqrt(2)
    E_lhcp = (E_theta + 1j * E_phi) / math.sqrt(2)

    rhcp_power = abs(E_rhcp)**2
    lhcp_power = abs(E_lhcp)**2

    rhcp_gain_dBi = 10 * math.log10(rhcp_power) if rhcp_power > 0 else -math.inf
    lhcp_gain_dBi = 10 * math.log10(lhcp_power) if lhcp_power > 0 else -math.inf

    # Axial ratio in dB
    max_pol_power = max(rhcp_power, lhcp_power)
    min_pol_power = min(rhcp_power, lhcp_power)
    if min_pol_power == 0:
        axial_ratio_dB = float('inf')
    else:
        axial_ratio_dB = 10 * math.log10(max_pol_power / min_pol_power)

    # Polarization sense
    if axial_ratio_dB == float('inf'):
        polarization_sense = "Linear"
    elif rhcp_power > lhcp_power:
        polarization_sense = "RHCP"
    else:
        polarization_sense = "LHCP"

    # Polarization ellipse tilt (major axis orientation in θ–φ plane)
    delta = math.radians(E_theta_phase_deg - E_phi_phase_deg)
    if E_theta_mag != 0 and E_phi_mag != 0:
        tilt_rad = 0.5 * math.atan2(
            2 * E_theta_mag * E_phi_mag * math.cos(delta),
            E_theta_mag**2 - E_phi_mag**2
        )
        polarization_tilt_deg = math.degrees(tilt_rad)
    else:
        polarization_tilt_deg = 0.0

    # Vertical and horizontal gain projections
    #   - vertical polarization corresponds to E_theta
    #   - horizontal polarization corresponds to E_phi
    # (this is the convention used in 4NEC2's output)

    vert_power = abs(E_theta)**2
    horiz_power = abs(E_phi)**2

    vert_gain_dBi = 10 * math.log10(vert_power) if vert_power > 0 else -math.inf
    horiz_gain_dBi = 10 * math.log10(horiz_power) if horiz_power > 0 else -math.inf

    return {
        'E_theta_mag': E_theta_mag,
        'E_theta_phase_deg': E_theta_phase_deg,
        'E_phi_mag': E_phi_mag,
        'E_phi_phase_deg': E_phi_phase_deg,
        'total_gain_dBi': total_gain_dBi,
        'vert_gain_dBi': vert_gain_dBi,
        'horiz_gain_dBi': horiz_gain_dBi,
        'rhcp_gain_dBi': rhcp_gain_dBi,
        'lhcp_gain_dBi': lhcp_gain_dBi,
        'axial_ratio_dB': axial_ratio_dB,
        'polarization_tilt_deg': polarization_tilt_deg,
        'polarization_sense': polarization_sense
    }


    
