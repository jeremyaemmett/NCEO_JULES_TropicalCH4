import numpy as np
import matplotlib.pyplot as plt


def radial_scale(theta, s, a=1.0, b=1.0, growth_rate=0.0, phase=0.0):

    base_radius = np.sqrt((a*np.cos(s))**2 + (b*np.sin(s)**2))
    growth = np.exp(growth_rate*theta)
    modulation = 1 + growth_rate*np.sin(s+phase)

    #return base_radius * growth * modulation
    return(base_radius)


def shell_model(theta, s, A=2.0, alpha=5.0, beta=2.0, phi=0.0, Omega=0.0, mu=0.0, D=1.0):

    cot_alpha = 1 / np.tan(alpha)
    exp_factor = np.exp(theta * cot_alpha)

    r = radial_scale(theta, s)

    cos = np.cos
    sin = np.sin

    ze = r*exp_factor*sin(s+phi)

    x2 = (A* sin(beta) * cos(theta) + r*cos(s+phi) * cos(theta + Omega)) * exp_factor
    y2 = (A* sin(beta) * sin(theta) + r*cos(s+phi) * sin(theta + Omega)) * exp_factor
    z2 = (-A*cos(beta) + r*sin(s+phi)) * exp_factor

    x = D*(x2 - ze*sin(mu)*sin(theta + Omega))
    y = D*(y2 + ze*sin(mu)*cos(theta + Omega))
    z =(-A * cos(beta) + r*sin(s+phi) * cos(mu)) * exp_factor

    return x, y, z

theta = np.linspace(0, 6*np.pi, 1000)
s = np.linspace(0.0*2*np.pi, 1.0*2*np.pi, 1000)
TH, S = np.meshgrid(theta, s)

X, Y, Z = shell_model(TH, S)

fig = plt.figure(figsize=(5, 3.5))
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z, cmap='managua', linewidth=0, antialiased=True, alpha=1.0)

ax.set_facecolor('black')

ax.set_axis_off()
ax.set_aspect('equal')

plt.show()

