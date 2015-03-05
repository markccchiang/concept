# This module defines all physical units used by the rest of the code
import cython
from numpy import pi

# The following is chosen as the base units:
# Length: 1*kpc
# Time:   1*Gyr
# Mass:   10**10*m_sun
# Note that the base unit of velocity is then just about 1 km/s
kpc = 1
Gyr = 1
m_sun = 1e-10

# Other prefixes of the base length, time and mass
pc = 1e-3*kpc
Mpc = 1e+6*pc
Gpc = 1e+9*pc
yr = 1e-9*Gyr
kyr = 1e+3*yr
Myr = 1e+6*yr
km_sun = 1e+3*m_sun
Mm_sun = 1e+6*m_sun
Gm_sun = 1e+9*m_sun

# SI units
AU = pi/648000*pc
m = AU/149597870700
cm = 1e-2*m
km = 1e+3*m
s = yr/31557600  # Here yr is supposed to be a Julian year
kg = m_sun/1.989e+30
g = 1e-3*kg
