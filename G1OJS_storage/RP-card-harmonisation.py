   def set_gain_point(self, azimuth, elevation):
        theta_start = 90 - elevation
        phi_start = azimuth
        resol_deg = 1
        n_phi = 1
        n_theta = 1
        p_type = 0
        options = 1003
        self.RP_CARD = f"RP {p_type} {n_theta} {n_phi} {options} {theta_start:.2f} {phi_start:.2f} {resol_deg:.2f} {resol_deg:.2f}\n"

    def set_gain_az_arc(self, azimuth_start, azimuth_stop, nPoints, elevation):
        if(nPoints<2):
            nPoints=2
        resol_deg = (azimuth_stop - azimuth_start) / (nPoints-1)
        theta_start = 90 - elevation
        phi_start = azimuth_start
        n_phi = nPoints
        n_theta = 1
        p_type = 0
        options = 1003
        self.RP_CARD = f"RP {p_type} {n_theta} {n_phi} {options} {theta_start:.2f} {phi_start:.2f} {resol_deg:.2f} {resol_deg:.2f}\n"

    def set_gain_3D(self, resol_deg=1): # in development expect errors
        """Request 3D radiation pattern"""
        theta_start = 0.0
        phi_start = 0.0
        if(self.GE_CARD == "GE 0\n"):
            n_theta = int(180.0 / resol_deg) + 1
            theta_start = -180
        else:
            n_theta = int(90.0 / resol_deg) + 1
            theta_start = -90
        phi_start = 0.0
        n_phi = int(360.0 / resol_deg) + 1
        p_type = 0
        options = 1003
        self.RP_CARD = (f"RP {p_type} {n_theta} {n_phi} {options} {theta_start:.2f} {phi_start:.2f} {resol_deg:.2f} {resol_deg:.2f} \n")
