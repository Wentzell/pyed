
""" 
Exact diagonalization and single- and two-particle Green's function calculator for Triqs operator expressions.

Author: Hugo U. R. Strand (2017), hugo.strand@gmail.com
"""

# ----------------------------------------------------------------------

import itertools
import numpy as np

# ----------------------------------------------------------------------

from pytriqs.gf import MeshImTime, MeshProduct, MeshPoint, Idx

# ----------------------------------------------------------------------

from pyed.CubeTetras import CubeTetrasMesh, enumerate_tau3
from pyed.SquareTriangles import SquareTrianglesMesh, enumerate_tau2
from pyed.SparseExactDiagonalization import SparseExactDiagonalization
from pyed.SparseMatrixFockStates import SparseMatrixRepresentation

# ----------------------------------------------------------------------
class TriqsExactDiagonalization(object):
    
    """ Exact diagonalization for Triqs operator expressions. """

    # ------------------------------------------------------------------
    def __init__(self, H, fundamental_operators, beta):

        self.beta = beta
        self.rep = SparseMatrixRepresentation(fundamental_operators)
        self.ed = SparseExactDiagonalization(
            self.rep.sparse_matrix(H), beta)

    # ------------------------------------------------------------------
    def get_expectation_value(self, op):
        return self.ed.get_expectation_value(self.rep.sparse_matrix(op))

    # ------------------------------------------------------------------
    def get_free_energy(self):
        return self.ed.get_free_energy()
    def get_partition_function(self):
        return self.ed.get_partition_function()
    def get_density_matrix(self):
        return self.ed.get_density_matrix()
    def get_ground_state_energy(self):
        return self.ed.get_ground_state_energy()
        
    # ------------------------------------------------------------------
    def set_g2_tau(self, g_tau, op1, op2):

        assert( type(g_tau.mesh) == MeshImTime )
        assert( self.beta == g_tau.mesh.beta )
    
        op1_mat = self.rep.sparse_matrix(op1)
        op2_mat = self.rep.sparse_matrix(op2)        

        tau = np.array([tau.value for tau in g_tau.mesh])
 
        g_tau.data[:] = \
            self.ed.get_tau_greens_function_component(
                tau, op1_mat, op2_mat)

        self.set_tail(g_tau, op1_mat, op2_mat)
        
    # ------------------------------------------------------------------
    def set_g2_iwn(self, g_iwn, op1, op2):

        assert( self.beta == g_iwn.mesh.beta )
    
        op1_mat = self.rep.sparse_matrix(op1)
        op2_mat = self.rep.sparse_matrix(op2)        

        iwn = np.array([iwn.value for iwn in g_iwn.mesh])
        
        g_iwn.data[:] = \
            self.ed.get_frequency_greens_function_component(
                iwn, op1_mat, op2_mat, self.xi(g_iwn.mesh))

        self.set_tail(g_iwn, op1_mat, op2_mat)

    # ------------------------------------------------------------------
    def set_tail(self, g, op1_mat, op2_mat):

        tail = g.tail

        raw_tail = self.ed.get_high_frequency_tail_coeff_component(
            op1_mat, op2_mat, self.xi(g.mesh), Norder=tail.order_max)

        for idx in xrange(tail.order_max):
            tail[idx+1] = raw_tail[idx]

    # ------------------------------------------------------------------
    def xi(self, mesh):
        if mesh.statistic == 'Fermion': return -1.0
        elif mesh.statistic == 'Boson': return +1.0
        else: raise NotImplementedError

    # ------------------------------------------------------------------
    def set_g3_tau(self, g3_tau, op1, op2, op3):
        
        op1_mat = self.rep.sparse_matrix(op1)
        op2_mat = self.rep.sparse_matrix(op2)        
        op3_mat = self.rep.sparse_matrix(op3)

        ops_mat = np.array([op1_mat, op2_mat, op3_mat])

        for idxs, taus, perm, perm_sign in SquareTrianglesMesh(g3_tau):

            ops_perm_mat = ops_mat[perm + [2]]
            taus_perm = np.array(taus).T[perm]

            data = self.ed.get_timeordered_two_tau_greens_function(
                taus_perm, ops_perm_mat)

            for idx, d in zip(idxs, data):
                g3_tau[Idx(idx[0]), Idx(idx[1])][:] = perm_sign * d

    # ------------------------------------------------------------------
    def set_g40_tau(self, g40_tau, g_tau):

        assert( type(g_tau.mesh) == MeshImTime )
        #assert( g_tau.target_shape == g40_tau.target_shape )

        for t1, t2, t3 in g40_tau.mesh:
            g40_tau[t1, t2, t3] = \
                g_tau(t1-t2)*g_tau(t3.value) - g_tau(t1.value)*g_tau(t3-t2)
    
    # ------------------------------------------------------------------
    def set_g4_tau(self, g4_tau, op1, op2, op3, op4):

        op1_mat = self.rep.sparse_matrix(op1)
        op2_mat = self.rep.sparse_matrix(op2)        
        op3_mat = self.rep.sparse_matrix(op3)
        op4_mat = self.rep.sparse_matrix(op4)        

        ops_mat = np.array([op1_mat, op2_mat, op3_mat, op4_mat])

        for idxs, taus, perm, perm_sign in CubeTetrasMesh(g4_tau):

            ops_perm_mat = ops_mat[perm + [3]]
            taus_perm = np.array(taus).T[perm]

            data = self.ed.get_timeordered_three_tau_greens_function(
                taus_perm, ops_perm_mat)

            for idx, d in zip(idxs, data):
                g4_tau[MeshPoint(*idx)] = perm_sign * d

    # ------------------------------------------------------------------
   
# ----------------------------------------------------------------------
