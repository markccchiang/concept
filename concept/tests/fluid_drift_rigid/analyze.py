# This file is part of CO𝘕CEPT, the cosmological 𝘕-body code in Python.
# Copyright © 2015-2016 Jeppe Mosgaard Dakin.
#
# CO𝘕CEPT is free software: You can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CO𝘕CEPT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CO𝘕CEPT. If not, see http://www.gnu.org/licenses/
#
# The auther of CO𝘕CEPT can be contacted at dakin(at)phys.au.dk
# The latest version of CO𝘕CEPT is available at
# https://github.com/jmd-dk/concept/



# This file has to be run in pure Python mode!

# Standard test imports
import glob, sys, os

# Absolute paths to the directory of this file
this_dir = os.path.dirname(os.path.realpath(__file__))

# Pull in environment variables
for env_var in ('concept_dir', 'this_test'):
    exec('{env_var} = os.environ["{env_var}"]'.format(env_var=env_var))

# Include the concept_dir in the searched paths
sys.path.append(concept_dir)

# Imports from the CO𝘕CEPT code
from commons import *
from snapshot import load

# Read in data from the CO𝘕CEPT snapshots
fluid_components = []
particle_components = []
a = []
for fname in sorted(glob.glob(this_dir + '/output/snapshot_a=*'),
                    key=lambda s: s[(s.index('=') + 1):]):
    snapshot = load(fname, compare_params=False)
    for component in snapshot.components:
        if component.representation == 'fluid':
            fluid_components.append(component)
        elif component.representation == 'particles':
            particle_components.append(component)
    a.append(snapshot.params['a'])
gridsize = fluid_components[0].gridsize
N_snapshots = len(a)
# Sort data chronologically
order = np.argsort(a)
a                   = [a[o]                   for o in order]
fluid_components    = [fluid_components[o]    for o in order]
particle_components = [particle_components[o] for o in order]

# Begin analysis
masterprint('Analyzing {} data ...'.format(this_test))

# Extract ϱ(x) of fluids and y(x) of particles.
# To compare ϱ to y, a scaling is needed.
# Since the x's in ϱ(x) are discretized, but the x's in y(x) are not,
# we interpolate y to the disretized x-values.
x_fluid = asarray([boxsize*i/gridsize for i in range(gridsize)])
ϱ = []
y = []
y_interp = []
for fluid, particles in zip(fluid_components, particle_components):
    ϱ.append(fluid.fluidvars['ϱ'].grid_noghosts[:gridsize, 0, 0])
    y_i = particles.posy.copy()
    A_fluid          = 0.5*(max(ϱ[0]) - min(ϱ[0]))
    offset_fluid     = 0.5*(max(ϱ[0]) + min(ϱ[0]))
    A_particles      = 0.5*(max(y_i)  - min(y_i))
    offset_particles = 0.5*(max(y_i)  + min(y_i))
    y_i -= offset_particles 
    y_i *= A_fluid/A_particles
    y_i += offset_fluid
    y.append(y_i)
    # Interpolation is made by a simple polynomial fit,
    # but with a large order.
    order = 15
    y_interp.append(np.polyval(np.polyfit(particles.posx, y_i, order), x_fluid))

# Plot
fig_file = this_dir + '/result.png'
fig, ax = plt.subplots(N_snapshots, sharex=True, figsize=(8, 3*N_snapshots))
for ax_i, particles, ϱ_i, y_i, y_interp_i, a_i in zip(ax, particle_components, ϱ, y, y_interp, a):
    ax_i.plot(particles.posx, y_i,
              'ro', markerfacecolor='none', markeredgecolor='r',
              label='Particle simulation')
    ax_i.plot(x_fluid, y_interp_i, 'r')
    ax_i.plot(x_fluid, ϱ_i, 'b*', label='Fluid simulation')
    ax_i.set_ylabel('scaled and shifted $y$,\n' + r'$\varrho$ $\mathrm{{[{}\,m_{{\odot}}\,{}^{{-3}}]}}$'
                    .format(significant_figures(1/units.m_sun,
                                                3,
                                                fmt='tex',
                                                incl_zeros=False,
                                                scientific=False,
                                                ),
                            unit_length)
                    )
    ax_i.set_title(r'$a={:.3g}$'.format(a_i))
plt.xlim(0, boxsize)
plt.legend(loc='best').get_frame().set_alpha(0.3)
plt.xlabel(r'$x\,\mathrm{{[{}]}}$'.format(unit_length))
plt.tight_layout()
plt.savefig(fig_file)

# Fluid elements in yz-slices should all have the same ϱ
# and all fluid elements should have the same u = ϱu/ϱ.
tol_fac_ϱ = 1e-6
tol_fac_u = 1e-3
for fluid, a_i in zip(fluid_components, a):
    for fluidscalar in fluid.iterate_fluidscalars():
        varnum = fluidscalar.varnum
        grid = fluidscalar.grid_noghosts[:gridsize, :gridsize, :gridsize]
        if varnum == 0:
            # ϱ
            ϱ_grid = grid
            for i in range(gridsize):
                yz_slice = grid[i, :, :]
                if not isclose(np.std(yz_slice), 0,
                               rel_tol=0,
                               abs_tol=(tol_fac_ϱ*np.std(grid) + machine_ϵ)):
                    masterwarn('Non-uniformities have emerged at a = {} '
                               'in yz-slices of fluid scalar variable {}.\n'
                               'See "{}" for a visualization.'
                               .format(a_i, fluidscalar, fig_file))
                    sys.exit(1)
        elif varnum == 1:
            # ϱu
            u_grid = grid/ϱ_grid
            if not isclose(np.std(u_grid), 0,
                           rel_tol=0,
                           abs_tol=(tol_fac_u*abs(np.mean(u_grid)) + machine_ϵ)):
                masterwarn('Non-uniformities have emerged at a = {} '
                           'in fluid scalar variable {}'
                           .format(a_i, fluidscalar))
                sys.exit(1)

# Compare ϱ to the fluid from the snapshots
tol_fac = 1e-2
for ϱ_i, y_interp_i, a_i in zip(ϱ, y_interp, a):
    if not isclose(np.mean(abs(ϱ_i - y_interp_i)), 0,
                   rel_tol=0,
                   abs_tol=(tol_fac*np.std(ϱ_i) + machine_ϵ)):
        masterwarn('Fluid drift differs from particle drift at a = {:.3g}.\n'
                   'See "{}" for a visualization.'
                   .format(a_i, fig_file))
        sys.exit(1)

# Done analyzing
masterprint('done')
