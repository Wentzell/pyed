# ----------------------------------------------------------------------

import itertools
import numpy as np

# ----------------------------------------------------------------------

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------

from pytriqs.gf import Gf
from pytriqs.archive import HDFArchive
#from pytriqs.plot.mpl_interface import oplot

# ----------------------------------------------------------------------

from pyed.CubeTetras import zero_outer_planes_and_equal_times
            
# ----------------------------------------------------------------------
def plot_2d_g(ax, g2_tau, **kwargs):

    data = g2_tau.data[:, :, 0, 0, 0, 0]
    x = np.arange(data.shape[-1])
    X, Y = np.meshgrid(x, x)
    ax.plot_wireframe(X, Y, data.real, **kwargs)
    
# ----------------------------------------------------------------------
if __name__ == '__main__':
    
    A = HDFArchive('data_ed.h5', 'r')

    # ------------------------------------------------------------------
    # -- Single-particle Green's function
    
    g_tau = A['G_tau']
    tau = np.array([tau for tau in g_tau.mesh])

    plt.figure(figsize=(3.25, 2))
    tau = [ tau for tau in g_tau.mesh ]
    plt.plot(tau, g_tau.data[:, 0, 0], '.-g', alpha=0.5)
    plt.xlabel(r'$\tau$')
    plt.ylabel(r'$G(\tau)$')
    plt.tight_layout()
    #oplot(g_tau)
    plt.savefig('figure_g_tau.pdf')
    
    # ------------------------------------------------------------------
    # -- Two-particle Green's function
    g4_tau = A['G2_tau']
    g40_tau = A['G20_tau']

    zero_outer_planes_and_equal_times(g4_tau)
    zero_outer_planes_and_equal_times(g40_tau)
    #np.testing.assert_array_almost_equal(g4_tau.data, g40_tau.data)

    fig = plt.figure(figsize=(3.25*2, 2.5))
    subp = [1, 3, 1]
    
    # -- All slice planes
    for i1, i2 in itertools.combinations(range(3), 2):

        frac_cut = 3
        cut_idx = int(np.round(1./frac_cut * g4_tau.data.shape[0]))
        plane_slice = [cut_idx]*3
        plane_slice[i1], plane_slice[i2] = all, all
        time_labels = [r'$\tau_1$', r'$\tau_2$', r'$\tau_3$']
        xlabel, ylabel = time_labels[i1], time_labels[i2]
        title = time_labels[list(set(range(3)).difference(set([i1, i2])))[0]] + r'$=\beta/%i$' % frac_cut
        
        
        ax = fig.add_subplot(*subp, projection='3d')
        subp[-1] += 1

        plot_2d_g(ax, g4_tau[plane_slice],
                  label=r'$G^{(4)}(\tau_1, \tau_2, \tau_3)$', alpha=0.5, color='b', lw=0.5, clip_on=False)

        plot_2d_g(ax, g40_tau[plane_slice],
                  label=r'$G^{(4)}_0(\tau_1, \tau_2, \tau_3)$', alpha=0.5, color='g', lw=0.5, clip_on=False)

        ax.set_xlabel(xlabel, labelpad=-8)
        ax.set_ylabel(ylabel, labelpad=-8)
        #ax.set_zlabel(r'$G(\tau_1, \tau_2, \tau_3)$', labelpad=-8)
        ax.set_title(title, loc='left', fontdict=dict(fontsize=10))
 
        #ax.set_zlim([-0.15, 0.15])
        ax.set_zlim([-0.09, 0.09])

        for ticks in [ax.xaxis.get_major_ticks(),
                      ax.yaxis.get_major_ticks(),
                      ax.zaxis.get_major_ticks()]:
            for tick in ticks:
                tick.label.set_fontsize(6)
                tick.set_pad(-2)
            
    plt.legend(ncol=1, frameon=True, loc='best')
    plt.tight_layout()
    plt.savefig('figure_g2_tau.pdf')

    plt.show()
    
# ----------------------------------------------------------------------
