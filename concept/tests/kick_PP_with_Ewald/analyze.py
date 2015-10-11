# This file is part of CO𝘕CEPT, the cosmological 𝘕-body code in Python.
# Copyright © 2015 Jeppe Mosgaard Dakin.
#
# CO𝘕CEPT is free software: you can redistribute it and/or modify
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
# The auther of CO𝘕CEPT can be contacted at
# jeppe.mosgaard.dakin(at)post.au.dk
# The latest version of CO𝘕CEPT is available at
# https://github.com/jmd-dk/concept/



# This file has to be run in pure Python mode!

# Include the concept_dir in the searched paths and get directory of this file
import sys, os
sys.path.append(os.environ['concept_dir'])
this_dir = os.path.dirname(os.path.realpath(__file__))

# Imports from the CO𝘕CEPT code
from commons import *
from snapshot import GadgetSnapshot

# Determine the number of snapshots from the outputlist file
N_snapshots = len(np.loadtxt(this_dir + '/outputlist'))

# Instantiate a GadgetSnapshot instance which will be reused for all GADGET snapshots
snapshot = GadgetSnapshot()

# Read in data from the CO𝘕CEPT snapshots
a = zeros(N_snapshots)
x0 = zeros(N_snapshots)
x0_std = zeros(N_snapshots)
x1 = zeros(N_snapshots)
x1_std = zeros(N_snapshots)
for i in range(N_snapshots):
    fname = 'snapshot_a={:.2f}'.format(np.loadtxt(this_dir + '/outputlist')[i])
    snapshot.load(this_dir + '/output/' + fname, compare_params=False)
    a[i] = snapshot.params['a']
    x0[i] = np.mean(snapshot.particles.posx[:4])
    x0_std[i] = np.std(snapshot.particles.posx[:4])
    x1[i] = np.mean(snapshot.particles.posx[4:])
    x1_std[i] = np.std(snapshot.particles.posx[4:])

# Read in data from the GADGET snapshots
a_gadget = zeros(N_snapshots)
x0_gadget = zeros(N_snapshots)
x0_std_gadget = zeros(N_snapshots)
x1_gadget = zeros(N_snapshots)
x1_std_gadget = zeros(N_snapshots)
for i in range(N_snapshots):
    snapshot.load(this_dir + '/output/snapshot_gadget_' + '0'*(3-len(str(i))) + str(i), compare_params=False)
    a_gadget[i] = snapshot.params['a']
    x_gadget = snapshot.particles.posx[np.argsort(snapshot.ID)]
    x0_gadget[i] = np.mean(x_gadget[:4])
    x0_std_gadget[i] = np.std(x_gadget[:4])
    x1_gadget[i] = np.mean(x_gadget[4:])
    x1_std_gadget[i] = np.std(x_gadget[4:])

# Plot
fig_file = this_dir + '/result.png'
plt.errorbar(a, x0, yerr=x0_std, fmt='-sr', label='CO$N$CEPT (left)')
plt.errorbar(a, x1, yerr=x1_std, fmt='-Dr', label='CO$N$CEPT (right)')
plt.errorbar(a_gadget, x0_gadget, yerr=x0_std_gadget, fmt='--<b', label='GADGET (left)')
plt.errorbar(a_gadget, x1_gadget, yerr=x1_std_gadget, fmt='-->b', label='GADGET (right)')
plt.legend(loc='best')
plt.xlabel('$a$')
plt.ylabel(r'$x\,\mathrm{[' + units.length + ']}$')
plt.ylim(0, boxsize)
plt.savefig(fig_file)

# Analyze.
# There should be no variance on the x positions.
tol = N_snapshots*100*np.finfo('float32').eps
if np.sum(x0_std_gadget) > tol or np.sum(x1_std_gadget) > tol:
    masterwarn('Unequal x-positions for the 2*4 particles in the GADGET snapshots.\n'
               + 'It is no good to compare the CONCEPT results to these.')
    sys.exit(1)
if np.sum(x0_std) > tol or np.sum(x1_std) > tol:
    masterwarn('Unequal x-positions for the 2*4 particles in the snapshots.\n'
               + 'The symmetric initial conditions has produced nonsymmetric results!')
    sys.exit(1)

# Printout error message for unsuccessful test
tol = 1e-2
if max(np.abs(x0/x0_gadget - 1)) > tol or max(np.abs(x1/x1_gadget - 1)) > tol:
    masterwarn('The results from CONCEPT disagree with those from GADGET.\n'
          + 'See "{}" for a visualization.'.format(fig_file))
    sys.exit(1)

