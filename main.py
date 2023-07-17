import casadi as ca
import numpy as np
from matplotlib import pyplot as plt

from dynamics import f_tilde, f
from helpers import smooth_norm
from animate import animate_trajectory

# Trying with large T before time-scaling
TIME_SCALING = True

# Model parameters (inspired by older paper)
max_thrust = 13260  # Newtons
m_dry = 1505  # kg
m_wet = 1905
r0 = ca.vertcat(1500, 2000)  # meters
v0 = ca.vertcat(0, 0)  # m/s

opti = ca.Opti()

N = 100  # Control intervals
if not TIME_SCALING:
    T = 30  # Total time (seconds)

# State
if TIME_SCALING:
    X_n = 8
else:
    X_n = 7

X = opti.variable(X_n, N + 1)

# Convention: First coord is altitude
r = X[0:2, :]
v = X[2:4, :]
theta = X[4, :]
omega = X[5, :]
m = X[6, :]
if TIME_SCALING:
    t_f = X[7, :]
    opti.subject_to(0 < t_f)
    opti.set_initial(t_f, 100)

opti.set_initial(r[:, 0], r0)
opti.set_initial(v[:, 0], v0)
opti.set_initial(m, m_wet)

# Controls
U = opti.variable(2, N)
u1 = U[0, :]  # Force applied by main booster - Always in direction of rocket!!!
u2 = U[1, :]  # Force applied by side boosters - Always perpendicular to rocket, applied at the very end

# Guess initial thrust
#opti.set_initial(U[0, :], 0.5 * max_thrust)

# Dynamics
x = ca.MX.sym('x', (X_n, 1))
u = ca.MX.sym('u', (2, 1))
if TIME_SCALING:
    xdot = f_tilde(x, u)
else:
    xdot = f(x, u)
f = ca.Function('f', [x, u], [xdot])

# Create gap-closing constraints with RK4
if TIME_SCALING:
    dt = 1 / N
else:
    dt = T / N
for k in range(N):
    k1 = f(X[:, k], U[:, k])
    k2 = f(X[:, k] + dt / 2 * k1, U[:, k])
    k3 = f(X[:, k] + dt / 2 * k2, U[:, k])
    k4 = f(X[:, k] + dt * k3, U[:, k])
    x_next = X[:, k] + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    opti.subject_to(X[:, k + 1] == x_next)

# Set model constraints

# Bounding thrust:
for col_i in range(U.shape[1]):
    thrust = smooth_norm(U[:, col_i])
    opti.subject_to(thrust <= max_thrust)
    # norm is always positive already

    # Forcing mass to decrease
    opti.subject_to(m[col_i] > m[col_i + 1])

# Thrust can only work against g:
opti.subject_to(U[0, :] >= 0)

# Mass bounds
opti.subject_to(m > m_dry)
opti.subject_to(m < m_wet)


# Initials
opti.subject_to(m[:, 0] == m_wet)
opti.subject_to(r[:, 0] == r0)
opti.subject_to(v[:, 0] == v0)

# Finals
opti.subject_to(r[:, -1] == ca.vertcat(0, 0, 0))
opti.subject_to(v[:, -1] == ca.vertcat(0, 0, 0))
#opti.subject_to(r[:, -1] <= ca.vertcat(1, 0, 0))
# opti.subject_to(r[:, -1] >= ca.vertcat(0, 0, 0))
#opti.subject_to(r[0, -1] <= 1)

# Trajectory constraints
opti.subject_to(0 <= r[0, :])
for c in range(N+1):
    opti.subject_to(r[0, c] > 600 * (r[1, c] <= 1000) * (r[1, c] >= 750))

#opti.minimize(-m[-1])
#opti.minimize(-m[-1] + r[0, -1] ** 2)
#opti.minimize(-m[-1])
#opti.minimize(-m[-1]**2)
#opti.minimize((-m[-1])**3)

#opti.minimize(v[0, -1] ** 2 + r[0, -1] ** 2)
opti.minimize(-m[-1])
# opti.minimize(ca.power(U, 2))
# opti.minimize(f)

s_opts = {"max_iter": 400}  # To help debugging go faster i.e. to access opti.debug.sol quicker
opti.solver('ipopt', {}, s_opts)

sol = opti.solve()
if TIME_SCALING:
    print(sol.value(t_f[-1]))