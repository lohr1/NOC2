import casadi as ca
from helpers import smooth_norm
from params import rocket_height, rocket_width

# Model Parameters
g = ca.vertcat([-3.7114, 0])
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

    # Force on center of mass due to U in each dimension
    # Note: only depends on main thruster u[0]
    # Convention: theta is angle made with vertical line i.e.:
    # straight up -> theta = 0
    # to the right (pos. r[1] dir.) -> theta = pi/2
    u_f = ca.vertcat(
        u[0] * ca.cos(theta),
        u[0] * ca.sin(theta)
    )

    a = g + u_f / m

    # Angular acceleration due to U
    I = (1/12) * m * (rocket_width**2 + rocket_height**2)  # Find ref. for I of rectangle about axis perp to plane
    ang_accel = u[1] * rocket_height/2 / I

    mdot = -alpha * smooth_norm(u)

    xdot = ca.vertcat(
        v[0],
        v[1],
        a[0],
        a[1],
        theta_dot,
        ang_accel,
        mdot
    )

    return xdot

def f_tilde(x, u):
    """This returns f-tilde, i.e. the augmented, time-scaled dynamics"""

    t_f = x[7]

    xdot = ca.vertcat(
        f(x[0:7], u),
        0
    )

    return t_f * xdot

# def f_tilde(x, u):
#     """
#     This returns f-tilde, i.e. the augmented, time-scaled dynamics
#     :param x: 8 dimensional state vector
#     :param u: 3 dimensional control
#     """
#     # Unpack/name var's
#     r = x[0:3]
#     v = x[3:6]
#     m = x[6]
#     t_f = x[7]
#
#     a = g + u / m
#
#     mdot = -alpha * smooth_norm(u)
#
#     xdot = ca.vertcat(
#         v[0],
#         v[1],
#         v[2],
#         a[0],
#         a[1],
#         a[2],
#         mdot,
#         0
#     )
#
#     # Apply time-rescaling
#     xdot = t_f * xdot
#
#     return xdot
#
