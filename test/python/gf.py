# ----------------------------------------------------------------------

import itertools
import numpy as np

# ----------------------------------------------------------------------

from triqs_tprf.tight_binding import TBLattice

from triqs_tprf.lattice import lattice_dyson_g0_wk, lattice_dyson_g0_fk
from triqs_tprf.lattice import lattice_dyson_g_wk, lattice_dyson_g_fk
from triqs_tprf.lattice import lindhard_chi00

from triqs_tprf.gw import bubble_PI_wk
from triqs_tprf.gw import dynamical_screened_interaction_W
from triqs_tprf.gw import gw_sigma
from triqs_tprf.gw import g0w_sigma

from triqs.gf import Gf, MeshImFreq, MeshReFreq
from triqs.gf.mesh_product import MeshProduct

# ----------------------------------------------------------------------

def test_gf_Matsubara():
    nw = 100
    nk = 8
    norb = 2
    beta = 10.0
    V = 5.0
    mu = 0.0
    
    # Tight-binding
    t = -1.0 * np.eye(norb)
    
    t_r = TBLattice(
        units = [(1, 0, 0)],
        hopping = {
            (+1,) : t,
            (-1,) : t,
            },
        orbital_positions = [(0,0,0)]*norb,
        )
    
    kmesh = t_r.get_kmesh(n_k=(nk, 1, 1))
    e_k = t_r.fourier(kmesh)
    
    kmesh = e_k.mesh
    wmesh = MeshImFreq(beta, 'Fermion', nw)

    # Test setup bare Gf
    print("  -> bare Matsubara Gf")
    g0_wk = lattice_dyson_g0_wk(mu=mu, e_k=e_k, mesh=wmesh)

    g0_wk_ref = Gf(mesh=MeshProduct(wmesh, kmesh), target_shape=[norb]*2)
    for w in wmesh:
        for k in kmesh:
            #g0_wk_ref[w,k] = 1.0 / (w.value - e_k[k] + mu)
            g0_wk_ref[w,k] = np.linalg.inv( (w.value + mu)*np.eye(norb) - e_k[k] )

    np.testing.assert_array_almost_equal(g0_wk.data[:], g0_wk_ref.data[:])

    # Get self-energy
    V_k = Gf(mesh=kmesh, target_shape=[norb]*4)
    V_k.data[:] = V
    PI_wk = bubble_PI_wk(g0_wk)
    W_wk = dynamical_screened_interaction_W(PI_wk, V_k)
    sigma_wk = gw_sigma(W_wk, g0_wk)

    # Test setup dressed Gf
    print("  -> dressed Matsubara Gf")
    g_wk = lattice_dyson_g_wk(mu=mu, e_k=e_k, sigma_wk=sigma_wk)
    g_wk_ref = Gf(mesh=MeshProduct(wmesh, kmesh), target_shape=[norb]*2)
    for w in wmesh:
        for k in kmesh:
            #g_wk_ref[w,k] = 1.0 / (w.value - e_k[k] + mu - sigma_wk[w,k])
            g_wk_ref[w,k] = np.linalg.inv( (w.value + mu)*np.eye(norb) - e_k[k] - sigma_wk[w,k] )
    
    np.testing.assert_array_almost_equal(g_wk.data[:], g_wk_ref.data[:])

    


def test_gf_realfreq():
    nw = 100
    wmin = -5.0
    wmax = 5.0
    nk = 8
    norb = 2
    beta = 10.0
    V = 5.0
    mu = 0.0
    delta = 0.01
    
    # Tight-binding
    t = -1.0 * np.eye(norb)
    
    t_r = TBLattice(
        units = [(1, 0, 0)],
        hopping = {
            (+1,) : t,
            (-1,) : t,
            },
        orbital_positions = [(0,0,0)]*norb,
        )
    
    kmesh = t_r.get_kmesh(n_k=(nk, 1, 1))
    e_k = t_r.fourier(kmesh)
    
    kmesh = e_k.mesh
    fmesh = MeshReFreq(wmin, wmax, nw)

    # Test setup bare Gf
    print("  -> bare real-freq. Gf")
    g0_fk = lattice_dyson_g0_fk(mu=mu, e_k=e_k, mesh=fmesh, delta=delta)
    g0_fk_ref = Gf(mesh=MeshProduct(fmesh, kmesh), target_shape=[norb]*2)
    for f in fmesh:
        for k in kmesh:
            #g0_fk_ref[f,k] = 1.0 / (f.value + 1.0j*delta - e_k[k] + mu)
            g0_fk_ref[f,k] = np.linalg.inv( (f.value + 1.0j*delta + mu)*np.eye(norb) - e_k[k] )

    np.testing.assert_array_almost_equal(g0_fk.data[:], g0_fk_ref.data[:])

    # Get self-energy
    V_k = Gf(mesh=kmesh, target_shape=[norb]*4)
    V_k.data[:] = V
    PI_fk = lindhard_chi00(e_k=e_k, mesh=fmesh, beta=beta, mu=mu, delta=delta)
    W_fk = dynamical_screened_interaction_W(PI_fk, V_k)
    sigma_fk = g0w_sigma(mu=mu, beta=beta, e_k=e_k, mesh=fmesh, W_fk=W_fk, v_k=V_k, delta=delta)

    # Test setup dressed Gf
    print("  -> dressed real-freq. Gf")
    g_fk = lattice_dyson_g_fk(mu=mu, e_k=e_k, sigma_fk=sigma_fk, delta=delta)
    g_fk_ref = Gf(mesh=MeshProduct(fmesh, kmesh), target_shape=[norb]*2)
    for f in fmesh:
        for k in kmesh:
            #g_fk_ref[f,k] = 1.0 / (f.value + 1.0j*delta - e_k[k] + mu - sigma_fk[f,k])
            g_fk_ref[f,k] = np.linalg.inv( (f.value + 1.0j*delta + mu)*np.eye(norb) - e_k[k] - sigma_fk[f,k] )
    
    np.testing.assert_array_almost_equal(g_fk.data[:], g_fk_ref.data[:])


if __name__ == "__main__":
    test_gf_Matsubara()
    test_gf_realfreq()




