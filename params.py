import casadi as ca
import numpy as np

REAL_SITUATION = False  # The case of having launched from earth, separated from second stage, and must now land
# Note: REAL_SITUATION did not converge

# Dimensions of rocket rectangle
rocket_height = 41.2  # Falcon 9 first stage height
rocket_width = 3.7  # Falcon 9 first stage diameter

# Dynamics params
g = ca.vertcat([-3.7114, 0])  # on Mars (from Açıkmeşe, Ploen paper)
alpha = 4.53e-4

# Boundary params
max_thrust = 13260  # Newtons
m_wet = 1905  # kg
m_dry = 1505
m_dry = 1000  # example 2

# Initials
r0 = ca.vertcat(1500, 2000)  # meters
r0 = ca.vertcat(2500, 2000)  # example 2

v0 = ca.vertcat(0, 0)  # m/s

theta0 = -np.pi/2  # radians
theta0 = np.pi/2  # example 2
theta_dot0 = 0

# Finals
rf = ca.vertcat(rocket_height / 2, 0)
vf = ca.vertcat(0, 0)
thetaf = 0
theta_dotf = 0

# t_f guess
t_f0 = 100

if REAL_SITUATION:
    # Dynamics params
    g = ca.vertcat([-9.8067, 0])
    alpha = 4.53e-4
    alpha = 0

    # Model parameters (source: https://www.spaceflightinsider.com/hangar/falcon-9/)
    max_thrust = 8227000
    m_dry = 25600
    fuel_mass = 395700
    m_wet = m_dry + fuel_mass

    # Initials
    r0 = ca.vertcat(75000, 5000)  # meters
    v0 = ca.vertcat(1276.741, 1071.313)  # m/s - 6000 km/h total velocity at Main Engine Cutoff/Stage separation in https://www.youtube.com/watch?v=9ekFE2RxBMI
    theta0 = 40 * np.pi / 180  # radians
    theta_dot0 = 0

    # Finals
    rf = ca.vertcat(rocket_height / 2, 0)
    vf = ca.vertcat(0, 0)
    thetaf = 0
    theta_dotf = 0

    # t_f guess
    t_f0 = 400



