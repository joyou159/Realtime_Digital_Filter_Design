import numpy as np
import matplotlib.pyplot as plt

# Create an array of angles from 0 to 2*pi
theta = np.linspace(0, 2*np.pi, 100)

# Parametric equations for the unit circle
x = np.cos(theta)
y = np.sin(theta)

# Location of the zero at z = 1
zero_at_one = np.array([1, 0])

# Plot the unit circle
plt.plot(x, y, label='Unit Circle')

# Mark the zero at z = 1
plt.scatter(*zero_at_one, color='red', label='Zero at z=1')

# Set equal scaling and show the plot
plt.axis('equal')
plt.title('Response of Filter with Zero at z=1')
plt.legend()
plt.grid(True)
plt.show()

print(x, y)
