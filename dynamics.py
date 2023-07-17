import casadi as ca
from helpers import smooth_norm

# Model Parameters
g = ca.vertcat([-3.7114, 0, 0])
alpha = 4.53e-4  # Larger alpha -> losing more mass, since mdot decreases


def f(x, u):
    """
    Without time-scaling
    """

    # Unpack/name var's
    r = x[0:2]
    v = x[2:4]
    theta = x[4]
    theta_dot = x[5]
    m = x[6]

    # Calculate linear accelerations
    u_a = ca.vertcat(
        sin(pi/2 - theta) / u[0],

    )
    a_v = g + u_v / m  # Vertical acceleration
    a_h = 0 + u_h / m  # Horizontal acceleration
    a = g + u / m

    mdot = -alpha * smooth_norm(u)

    xdot = ca.vertcat(
        v[0],
        v[1],
        v[2],
        a[0],
        a[1],
        a[2],
        mdot
    )

    return xdot


def f_tilde(x, u):
    """
    This returns f-tilde, i.e. the augmented, time-scaled dynamics
    :param x: 8 dimensional state vector
    :param u: 3 dimensional control
    """
    # Unpack/name var's
    r = x[0:3]
    v = x[3:6]
    m = x[6]
    t_f = x[7]

    a = g + u / m

    mdot = -alpha * smooth_norm(u)

    xdot = ca.vertcat(
        v[0],
        v[1],
        v[2],
        a[0],
        a[1],
        a[2],
        mdot,
        0
    )

    # Apply time-rescaling
    xdot = t_f * xdot

    return xdot

