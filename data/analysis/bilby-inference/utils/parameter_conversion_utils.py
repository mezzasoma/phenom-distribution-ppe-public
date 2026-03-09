
def get_chi_hat_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(chirp_mass, mass_ratio, chi_1, chi_2):
    '''
    Eq. (4) in arXiv:1508.07253 [Khan et al. 2016]. mass_ratio is assumed <= 1.
    '''
    mass_1 = chirp_mass * mass_ratio ** (-3.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    mass_2 = chirp_mass * mass_ratio ** (2.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    symmetric_mass_ratio = mass_ratio * (1.0 + mass_ratio) ** (-2.0)
    chi_eff = (mass_1 * chi_1 + mass_2 * chi_2) / (mass_1 + mass_2)
    chi_PN = chi_eff - (38.0)/(113.0) * symmetric_mass_ratio * (chi_1 + chi_2)
    chi_hat = chi_PN / (1.0 - 76.0 * symmetric_mass_ratio / 113.0)
    return chi_hat

def get_chi_PN_from_chirp_mass_and_mass_ratio_and_chi_1_and_chi_2(chirp_mass, mass_ratio, chi_1, chi_2):
    '''
    Eq. (4) in arXiv:1508.07253 [Khan et al. 2016]. mass_ratio is assumed <= 1.
    '''
    mass_1 = chirp_mass * mass_ratio ** (-3.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    mass_2 = chirp_mass * mass_ratio ** (2.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    symmetric_mass_ratio = mass_ratio * (1.0 + mass_ratio) ** (-2.0)
    chi_eff = (mass_1 * chi_1 + mass_2 * chi_2) / (mass_1 + mass_2)
    chi_PN = chi_eff - (38.0)/(113.0) * symmetric_mass_ratio * (chi_1 + chi_2)
    return chi_PN

def get_chi_eff_from_mass_1_and_mass_2_and_chi_1_and_chi_2(mass_1, mass_2, chi_1, chi_2):
    return (chi_1 * mass_1 + chi_2 * mass_2) / (mass_1 + mass_2)

def get_total_mass_from_chirp_mass_and_mass_ratio(chirp_mass, mass_ratio):
    """
    mass_ratio is assumed <= 1.
    """
    assert mass_ratio <= 1.0, "Error: mass_ratio must be less than or equal to 1.0"
    mass_1 = chirp_mass * mass_ratio ** (-3.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    mass_2 = chirp_mass * mass_ratio ** (2.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    total_mass = mass_1 + mass_2
    return total_mass

def get_mass_1_and_mass_2_from_chirp_mass_and_mass_ratio(chirp_mass, mass_ratio):
    """
    mass_ratio is assumed <= 1.
    """
    mass_1 = chirp_mass * mass_ratio ** (-3.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    mass_2 = chirp_mass * mass_ratio ** (2.0/5.0) * (1.0 + mass_ratio) ** (1.0/5.0)
    return mass_1, mass_2

def get_symmetric_mass_ratio_from_mass_1_and_mass_2(mass_1, mass_2):
    return mass_1 * mass_2 / (mass_1 + mass_2)**2

def get_symmetric_mass_ratio_from_mass_ratio(mass_ratio):
    """
    mass_ratio is assumed <= 1.
    """
    return mass_ratio / (1.0 + mass_ratio) ** 2.0