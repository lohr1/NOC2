import casadi as ca
import numpy as np
from matplotlib import pyplot as plt

import animation
from dynamics import f_tilde, f
from helpers import smooth_norm
from params import r0, v0, m_wet, max_thrust, m_dry, theta0, theta_dot0, rf, vf, t_f0, thetaf, theta_dotf

from animation import animate_rocket_trajectory

# Trying with large T before time-scaling
TIME_SCALING = True


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
theta_dot = X[5, :]
m = X[6, :]
if TIME_SCALING:
    t_f = X[7, :]
    opti.subject_to(0 < t_f)
    opti.set_initial(t_f, 100)


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

for col_i in range(U.shape[1]):
    # Bounding thrust
    thrust = smooth_norm(U[:, col_i])
    opti.subject_to(thrust <= max_thrust)

    # Forcing mass to decrease
    opti.subject_to(m[col_i] > m[col_i + 1])

# Main booster can only push:
opti.subject_to(U[0, :] >= 0)

# Mass bounds
opti.subject_to(m > m_dry)
opti.subject_to(m < m_wet)


# Initials
opti.subject_to(r[:, 0] == r0)
opti.subject_to(v[:, 0] == v0)
opti.subject_to(theta[:, 0] == theta0)
opti.subject_to(theta_dot[:, 0] == theta_dot0)
opti.subject_to(m[:, 0] == m_wet)

# Finals
opti.subject_to(r[:, -1] == rf)
opti.subject_to(v[:, -1] == vf)
opti.subject_to(theta[-1] == thetaf)
opti.subject_to(theta_dot[-1] == theta_dotf)
#opti.subject_to(r[:, -1] <= ca.vertcat(1, 0, 0))
# opti.subject_to(r[:, -1] >= ca.vertcat(0, 0, 0))
#opti.subject_to(r[0, -1] <= 1)

# Trajectory constraints
#opti.subject_to(r[1, :] >= -500)
opti.subject_to(r[0, :] >= 0)
#opti.subject_to(r[0, :] <= 1500)

opti.subject_to(theta <= np.pi/2)
opti.subject_to(-np.pi/2 <= theta)

opti.subject_to(opti.bounded(-0.2, theta_dot, 0.2))

#opti.subject_to(0 <= r[0, :])
# for c in range(N+1):
#     opti.subject_to(r[0, c] > 600 * (r[1, c] <= 1000) * (r[1, c] >= 750))

#opti.minimize(-m[-1])
#opti.minimize(-m[-1] + r[0, -1] ** 2)
opti.minimize(-m[-1])
#opti.minimize(-m[-1]**2)
#opti.minimize((-m[-1])**3)

#opti.minimize(v[0, -1] ** 2 + r[0, -1] ** 2)
#opti.minimize(-m[-1])
# opti.minimize(ca.power(U, 2))
# opti.minimize(f)

# Generate lin. interpolation guess
X0 = ca.vertcat(
    r0,
    v0,
    theta0,
    theta_dot0,
    m_wet
)
if TIME_SCALING:
    X0 = ca.vertcat(
        X0,
        t_f0
    )

Xf = ca.vertcat(
    rf,
    vf,
    thetaf,
    theta_dotf,
    m_dry
)
if TIME_SCALING:
    Xf = ca.vertcat(
        Xf,
        t_f0
    )

# X guess:
Xg = np.linspace(X0.full().flatten(), Xf.full().flatten(), N + 1)

opti.set_initial(X, Xg.T)

s_opts = {"max_iter": 400}  # To help debugging go faster i.e. to access opti.debug.sol quicker
opti.solver('ipopt', {}, s_opts)

sol = opti.solve()
if TIME_SCALING:
    print(sol.value(t_f[-1]))

# Animate
x = sol.value(r[1, :])
y = sol.value(r[0, :])
theta = sol.value(theta)

animate_rocket_trajectory(x, y, theta)

# %%
#
# Plot z vs x
plt.plot(sol.value(r[1, :]), sol.value(r[0, :]))

# Add labels and title
plt.xlabel('x-pos')
plt.ylabel('Altitude')

# Display the plot
plt.show()



# Plot mass
steps = range(N + 1)
plt.plot(steps, sol.value(m))

# Add labels and title
plt.xlabel('Step')
plt.ylabel('Mass')

# Display the plot
plt.show()