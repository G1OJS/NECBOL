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
        pattern = _read_radiation_pattern(model.nec_out, model.az_datum_deg, model.el_datum_deg)
        gains_at_point = [d for d in pattern if (abs(d['elevation_deg'] - model.el_datum_deg) < 0.1) and (abs(d['azimuth_deg'] - model.az_datum_deg) < 0.1)][0]
        
    except (RuntimeError, ValueError):
        print("Trying to read gains at {azimuth_deg}, {elevation_deg}")
        raise ValueError(f"Something went wrong reading gains from {nec_out}")

    return gains_at_point


def plot_pattern_gains(model, azimuth_deg = None, elevation_deg = None, components = ['vert_gain_dBi', 'horiz_gain_dBi'], gain_scale_range_dB = 30):
    import matplotlib.pyplot as plt
    import numpy as np

    if(elevation_deg is not None and azimuth_deg is not None):
        Print("Can't plot a 3D pattern, please select azimuth or elevation only")
        return

    if (elevation_deg is None and azimuth_deg is None):
        elevation_deg = model.el_datum_deg

    title = model.model_name

    # Filter data for fixed elevation (theta)
    if(elevation_deg is not None):
        print(f"Plotting gain for elevation = {elevation_deg}")
        pattern_data = _read_radiation_pattern(model.nec_out, azimuth_deg = azimuth_deg, elevation_deg = None)
        
        cut = [d for d in pattern_data if abs(d['elevation_deg'] - elevation_deg) < 0.1]
        angle_deg = [d['azimuth_deg'] for d in cut]
        title += f' elevation = {elevation_deg}°'

    # Filter data for fixed azimuth (phi)
    if(azimuth_deg is not None):
        print(f"Plotting gain for azimuth = {azimuth_deg}")
        pattern_data = _read_radiation_pattern(model.nec_out, azimuth_deg = None, elevation_deg = elevation_deg)
        cut = [d for d in pattern_data if abs(d['azimuth_deg'] - azimuth_deg) < 0.1]
        angle_deg = [d['elevation_deg'] for d in cut]
        title += f' azimuth = {azimuth_deg}°'
 
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    scl_max = -100
    for comp in components:
        gain = [d[comp] for d in cut]
        scl_max = max(scl_max,max(gain))
        angle_rad = np.radians(angle_deg)
        ax.plot(angle_rad, gain, label = comp)
        print(comp, f" max gain: {max(gain)}")
    ax.legend()
    ax.set_title(title)
    ax.grid(True)

    ax.set_rmax(scl_max)
    ax.set_rmin(scl_max - gain_scale_range_dB )
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


def _plot_difference_field(model_A, model_B, **kwargs):
    import copy
    # needs work to check if patterns don't match az, el 1:1 and if model datums are different
    pattern_A = _read_radiation_pattern(model_A.nec_out)
    pattern_B = _read_radiation_pattern(model_B.nec_out)
    model_diff = copy.deepcopy(model_A)
    model_diff.set_name(f"Scattered field {model_A.model_name} minus {model_A.model_name}")
    diff_pattern = _subtract_field_patterns(pattern_A, pattern_B)
    _write_radiation_pattern(diff_pattern, model_diff.nec_out)
    plot_pattern_gains(model_diff, **kwargs)

def _subtract_field_patterns(pat1, pat2):
    Z_theta_1 = _get_complex_component(pat1, 'E_theta')
    Z_theta_2 = _get_complex_component(pat2, 'E_theta')
    Z_phi_1 = _get_complex_component(pat1, 'E_phi')
    Z_phi_2 = _get_complex_component(pat2, 'E_phi')

    output_pattern = []
    for i, d in enumerate(pat1):
        E_theta = Z_theta_1[i] - Z_theta_2[i]
        E_phi = Z_phi_1[i] - Z_phi_2[i]
        diff_dict = _compute_full_farfield_metrics(E_theta, E_phi)
        diff_dict.update({'azimuth_deg':d['azimuth_deg']})
        diff_dict.update({'elevation_deg':d['elevation_deg']})
        output_pattern.append(diff_dict)

    return output_pattern


def _write_radiation_pattern(pattern, file_path):
    field_formats = [
        "8.2f", "9.2f", "11.2f", "8.2f", "8.2f",
        "11.5f", "9.2f", "8s",
        "15.5e", "9.2f", "15.5e", "9.2f"
    ]
    op_keys = [
        'elevation_deg', 'azimuth_deg', 'vert_gain_dBi', 'horiz_gain_dBi', 'total_gain_dBi',
        'axial_ratio_dB', 'tilt_deg', 'sense',
        'E_theta_mag', 'E_theta_phase_deg', 'E_phi_mag', 'E_phi_phase_deg'
    ]

    with open(file_path, "w") as f:
        f.write("                                                - - - RADIATION PATTERNS - - -\n")
        f.write("\n")
        f.write("  - - ANGLES - -           - POWER GAINS -       - - - POLARIZATION - - -    - - - E(THETA) - - -    - - - E(PHI) - - -\n")
        f.write("  THETA     PHI        VERT.   HOR.    TOTAL      AXIAL     TILT   SENSE     MAGNITUDE    PHASE      MAGNITUDE    PHASE \n")
        f.write(" DEGREES  DEGREES       DB      DB      DB        RATIO     DEG.              VOLTS/M    DEGREES      VOLTS/M    DEGREES\n")
        
        for row in pattern:
            line = ""
            for fmt, key in zip(field_formats, op_keys):
                val = row[key]
                if(key == 'elevation_deg'):
                    val = 90-val
                if(key == 'sense'):
                    val = ' '+val
                line += f"{val:{fmt}}"
            f.write(line.rstrip() + "\n")




def _read_radiation_pattern(filepath, azimuth_deg = None, elevation_deg = None):
    """
        Read the radiation pattern into a Python dictionary:
        'azimuth_deg': float,
        'elevation_deg': float,
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
            theta = float(line[1:8])
            phi = float(line[10:17])
            thetas.add(theta)
            phis.add(phi)
            if (elevation_deg is not None and theta != 90 - elevation_deg):
                continue
            if (azimuth_deg is not None and phi != azimuth_deg):
                continue
            data.append({
                'azimuth_deg': phi,
                'elevation_deg': 90 - theta,
                'vert_gain_dBi': float(line[21:28]),
                'horiz_gain_dBi': float(line[29:36]),
                'total_gain_dBi': float(line[37:44]),
                'axial_ratio_dB': float(line[48:55]),
                'tilt_deg': float(line[57:64]),
                'sense': line[65:72].strip(),
                'E_theta_mag': float(line[74:87]),
                'E_theta_phase_deg': float(line[88:96]),
                'E_phi_mag': float(line[98:111]),
                'E_phi_phase_deg': float(line[112:120])
            })

    if (len(data) == 0):
        print(f"Looking for gain at phi = {azimuth_deg}, theta = {90 - elevation_deg} in")
        print(f"Thetas = {thetas}")
        print(f"Phis = {phis}")
        raise EOFError(f"Failed to read needed data in {filepath}. Check for NEC errors.")

    return data




import math
import cmath

def _compute_full_farfield_metrics(E_theta, E_phi):

    # Phase & magnitude
    E_theta_phase_deg = 180*cmath.phase(E_theta)/cmath.pi
    E_phi_phase_deg = 180*cmath.phase(E_phi)/cmath.pi
    E_theta_mag = abs(E_theta)
    E_phi_mag = abs(E_phi)

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
        'vert_gain_dBi': vert_gain_dBi,
        'horiz_gain_dBi': horiz_gain_dBi,
        'total_gain_dBi': total_gain_dBi,
        'axial_ratio_dB': axial_ratio_dB,
        'tilt_deg': polarization_tilt_deg,
        'sense': polarization_sense,
        'E_theta_mag': E_theta_mag,
        'E_theta_phase_deg': E_theta_phase_deg,
        'E_phi_mag': E_phi_mag,
        'E_phi_phase_deg': E_phi_phase_deg,
        'rhcp_gain_dBi': rhcp_gain_dBi,
        'lhcp_gain_dBi': lhcp_gain_dBi
    }


def _get_available_results(model):
    # need to add here whether over full pattern or e.g. azimuth cut
 #   model.max_total_gain = max(d['total_gain_dBi'] for d in pattern_data)
    model.vswr = vswr(model)

    
