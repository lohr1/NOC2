import casadi as ca

# Dimensions of rocket rectangle
rocket_height = 41.2  # Falcon 9 first stage height
rocket_width = 3.7  # Falcon 9 first stage diameter


# Model parameters (inspired by older paper)
max_thrust = 13260  # Newtons
m_wet = 1905  # kg
m_dry = 1505
m_dry = 1000

# max_thrust = 8227000
# m_dry = 25600
# m_wet = m_dry + 395700


# Initials
r0 = ca.vertcat(1500, 2000)  # meters
v0 = ca.vertcat(0, 0)  # m/s
theta0 = 0  # radians
theta_dot0 = 0

# Finals
rf = ca.vertcat(rocket_height / 2, 0)
vf = ca.vertcat(0, 0)
thetaf = 0
theta_dotf = 0

# t_f guess
t_f0 = 100