#!/usr/bin/env python
""" Ambiguity.py : Python equivalent of ambiguity_1.m
Author : Tooring Analytics
"""

import numpy as np
import numpy.matlib as npml
import scipy.sparse
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


# inputs
DEFAULT_SIGNAL = np.ones((1, 51))


def dmpdat(s, e):
    """ Dump a data structure with its name & shape.
    Params:
    -------
    s: str. The name of the structure
    e: expression. An expression to dump. Implicitly assumes e is
    array_like
    """
    print("%s:" % s)
    print(e)
    print("%s.shape:" % s)
    print(e.shape)
    print("-------------------------------------------")


def brk(s, e):
    """ Used for debugging, just break the script, dumping data.
    """
    dmpdat(s, e)
    exit(-1)


def ambiguity(u_basic=DEFAULT_SIGNAL,
              fcode=True,
              f_basic=None,
              F=0,
              K=0,
              T=0,
              N=0,
              sr=0,
              plot1_file=None,
              plot2_file=None,
              plot_format="svg"):
    """ Entry point for translated code.
    Params:
    -------
    u_basic: numpy.ndarray or array-like. Input signal.
    fcode: bool True if frequency coding allowed, false otherwise
    f_basic: numpy.ndarray or array-like. Frequency coding in
    units of 1/tb (row vector of same length)
    F: int. Maximal Doppler shift for ambiguity in plot
    [in units of 1/Mtb] (e.g. 1)
    K: int. Number of Doppler grid points for calculation (e.g. 100)
    T: float. Maximal Delay for ambiguity plot [in units of Mtb]
    N: int. Number of delay grid points on each side (e.g. 100)
    sr: int/float. Over sampling ratio (>=1) (e.g. 10)
    plot1_file: str. Name of file where first plot will be stored
    plot2_file: str. Name of file where second plot will be stored
    plot_format: str. Output format for plot. (e.g. 'svg', 'png', 'pdf'
     etc. Check matplotlib docs for supported formats.)
    """

    # Initialization

    m_basic = np.amax(u_basic.shape)
    u = None

    # Ambiguity implementation

    df = float(F) / float(K) / float(m_basic)
    r = np.ceil(sr * (N + 1) / float(T) / float(m_basic))

    if r == 1:
        dt = 1
        m = m_basic
        uamp = np.abs(u_basic)
        phas = np.multiply(uamp, 0)
        phas = np.angle(u_basic)
        if fcode:
            phas = np.add(phas, np.multiply(2 * np.pi, np.cumsum(f_basic)))
        uexp = np.exp(1.0j * phas)
        u = np.multiply(uamp, uexp)
    else:
        dt = 1 / r
        ud = np.diag(u_basic[0])
        ao = np.ones((r, m_basic))
        m = m_basic * r
        u_basic = np.reshape(np.dot(ao, ud), (1, m))
        uamp = np.abs(u_basic)
        phas = np.angle(u_basic)
        u = u_basic
        if fcode:
            ff = np.diag(f_basic.flatten())

            coef = 2 * np.pi * dt
            vecprod = np.dot(ao, ff)
            vecprod_reshaped = np.reshape(vecprod.T, (1, m))
            cumsummed = np.cumsum(vecprod_reshaped)
            add_term = np.multiply(coef, cumsummed)
            phas = np.add(add_term, phas)

            comprod = 1.0j * phas
            uexp = np.exp(comprod)

            u = np.multiply(uamp, uexp)

    t = np.array([np.arange(0, r * m_basic) / r])

    tscale1 = np.hstack((
                        np.hstack((
                                   np.array([[0]]),
                                   np.array([np.arange(0, r * m_basic)])
                                  )),
                        np.array([[r * m_basic - 1]])
                        )) / r

    diff = np.diff(phas)

    nanarray = np.array([[np.nan]])
    temp = np.hstack((nanarray, diff))
    dphas = np.multiply(temp, float(r) / 2. / np.pi)


    fig_1 = plt.figure(1)

    plt.clf()
    plt.hold(False)

    plt.subplot(3, 1, 1)
    zerovec = np.array([[0]])
    abs_uamp = np.abs(uamp)
    ar1 = np.hstack((zerovec, abs_uamp))
    ar2 = np.hstack((ar1, zerovec))
    plt.plot(tscale1[0], ar2[0], c="r", linewidth=1.5)

    plt.subplot(3, 1, 2)
    plt.plot(t[0], phas[0], c="r", linewidth=1.5)
    # plt.axis(np.array([-np.inf, np.inf, -np.inf, np.inf]))
    plt.ylabel(' $Phase [rad]$ ')

    plt.subplot(3, 1, 3)
    plt.plot(t[0], (dphas * np.ceil(np.amax(t)))[0], c="r", linewidth=1.5)
    # plt.axis(np.array([-np.inf, np.inf, -np.inf, np.inf]))
    plt.xlabel(' $\\itt/t_b$ ')
    plt.ylabel(' $\\itf*Mt_b$ ')

    if plot1_file is not None:
        plt.savefig(plot1_file, format=plot_format)

    dtau = np.ceil(T * m) * dt / N

    tau = np.round(np.dot(np.array([np.arange(0., N+1., 1.)]), dtau / dt)) * dt


    f = np.array([np.dot(np.arange(0., K+1, 1.), df)])
    f = np.hstack((-1 * np.fliplr(f), f))

    Tm = np.ceil(np.dot(T, m)).astype(int)
    m_plus_Tm = int(m + Tm)
    uT = np.conj(u)
    mat1 = scipy.sparse.spdiags(uT.flatten(),
                                0,
                                m_plus_Tm,
                                m,
                                format="csc")

    zTm = np.zeros((1, Tm))
    u_padded = np.hstack((np.hstack((zTm, u)), zTm))
    cidx = np.array([np.arange(0, int(m + Tm))]).astype(int)

    ridx = np.round(tau / dt).T.astype(int)


    # Use repmat instead of the explicit Tony's Trick in the matlab code
    ar1 = npml.repmat(cidx, N + 1, 1)
    ar2 = npml.repmat(ridx, 1, m + Tm)
    index = np.add(ar1, ar2)

    u_padded_rep = np.array([ u_padded[0,colindex] for colindex in index])

    mat2 = scipy.sparse.csc_matrix(u_padded_rep)

    uu_pos = mat2.dot(mat1)
    uu_pos = uu_pos.tocsr()

    e = np.exp(np.multiply(-1j * 2. * np.pi, np.dot(f.T, t)))

    # By rules of matrix transposition:
    # np.dot(a,b).T = np.dot(b.T, a.T)
    # Let a = e, and
    # let b = uu_pos.conj(),
    # Then,
    # np.dot(e, uu_pos.conj()).T = uu_pos.conj().transpose(True).dot(e.T)
    # hence, np.dot(e, uu_pos.conj()) =
    # uu_pos.conj().transpose(True).dot(e.T).transpose(True)

    uu_pos_dash = uu_pos.transpose(True).conj()
    uu_pos_dash_trans = uu_pos_dash.transpose(True)
    e_sparse = scipy.sparse.csc_matrix(e)
    e_trans = e_sparse.transpose(True)
    e_dot_uu_pos_dash = (uu_pos_dash_trans.dot(e_trans)).transpose(True)

    a_pos = np.abs(e_dot_uu_pos_dash.toarray())

    a_pos = a_pos / np.amax(np.amax(a_pos))

    a_slice1 = a_pos[0:K+1, :]
    conj_a_slice1 = np.conj(a_slice1)
    flipud_conj = np.flipud(conj_a_slice1)
    a_slice2 = a_pos[K+1:2*K+2, :]
    fliplr_a_slice2 = np.fliplr(a_slice2)
    a = np.hstack((flipud_conj, fliplr_a_slice2))

    fliplr_tau = -1 * np.fliplr(tau)
    delay = np.hstack((fliplr_tau, tau))

    f_k = f[:, K + 1:2*K+2]

    maxT = np.ceil(np.amax(t))

    freq = np.multiply(f_k, maxT)

    delay_slice1 = delay[0, 0:N]
    delay_slice2 = delay[0, N+1:2*N]
    delay = np.array([np.hstack((delay_slice1, delay_slice2))])

    idx1 = np.arange(0, N)
    idx2 = np.arange(N+1, 2*N)
    a_cols = np.hstack((idx1, idx2))
    a = a[:, a_cols]

    (amf, amt) = a.shape

    # We use matplotlib's built-in colormaps, so no use for this.
    # cm = np.zeros((64, 3))
    # cm[:,2] = np.reshape(np.ones((64, 1)), (64,))

    fig_2 = plt.figure(2)

    plt.clf()

    plt.hold(False)

    ax3d = plt.subplot(111, projection='3d')

    x_coords = delay
    y_coords = np.hstack((np.zeros((1, 1)), freq)).T
    mesh_z = np.vstack((np.zeros((1, amt)), a))
    (mesh_x, mesh_y) = np.meshgrid(x_coords, y_coords)

    # If you want a wireframe, just uncomment the line
    # below, and comment the line that plots the surface.

    # ax3d.plot_wireframe(mesh_x, mesh_y, mesh_z)

    ax3d.plot_surface(mesh_x, mesh_y, mesh_z,
                      linewidth=0, cmap=cm.coolwarm)

    plt.hold(True)

    x_coords = delay
    y_coords = np.array([[0, 0]]).T
    surface_z = np.vstack((np.zeros((1, amt)), a[0]))
    (surface_x, surface_y) = np.meshgrid(x_coords, y_coords)

    ax3d.plot_surface(surface_x, surface_y, surface_z,
                      linewidth=0, cmap=cm.Blues)

    # Initialize the camera position. Matplotlib has a
    # different default orientation that matlab, so
    # elev & azimuth are adjusted accordingly.
    ax3d.view_init(elev=50., azim=-135)  # (-40, 50)

    # ax3d.axis([-1 * np.inf, np.inf, -1 * np.inf, np.inf, 0, 1])

    ax3d.set_xlabel(' $ \\tau/\\itt_b$ ',
                    fontsize=12)
    ax3d.set_ylabel(' $\\it\\nu * \\itMt_b$ ',
                    fontsize=12)
    ax3d.set_zlabel(' $|\\it\\chi(\\it\\tau,\\it\\nu)|$ ',
                    fontsize=12)

    plt.hold(False)

    if plot2_file is not None:
        plt.savefig(plot2_file, format=plot_format)

    return True