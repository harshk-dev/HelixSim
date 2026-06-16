# HelixSim (V1.0)

### 1. Adjustable Parameters

#### Structural & Geometric Parameters (Drone Core)

* **Total Mass/Weight (m):** Controls the overall weight of the aircraft, directly affecting the gravity vector calculations and the baseline thrust required for flight.
* **Frame Arm Length (L):** Determines the distance from the center of mass to the motors, directly altering the torque moment arms and the structural 3x3 Inertia Tensor.
* **Propeller Length/Diameter (d):** Dictates the aerodynamic surface area, scaling the thrust coefficient ($T = k \cdot \omega^2$) exponentially relative to rotor size.

#### Environmental Parameters (The Physics Sandbox)

* **Steady Wind Velocity & Direction:** Applies a continuous, directional drag force vector against the cross-sectional profile of the drone frame.
* **Wind Gust Frequency/Turbulence:** Introduces stochastic (randomized) force spikes to test the disturbance rejection capabilities of the inner control loop.
* **Local Gravity (g):** Allows modification of the ambient gravitational constant to simulate flight environments on Earth ($9.81 \text{ m/s}^2$), the Moon ($1.62 \text{ m/s}^2$), or Mars ($3.71 \text{ m/s}^2$).
* **Atmospheric Pressure:** Dynamically adjusts the surrounding air density ($\rho$), directly scaling both propeller lift efficiency and translational aerodynamic drag.

#### Electronic & Control Parameters (The "Brain")

* **PID Gains ($K_p, K_i, K_d$):** Fine-tunes the Proportional, Integral, and Derivative feedback loops governing attitude stability and position tracking error correction.
* **Electronic Speed Controller (ESC) Latency:** Simulates the real-world mechanical and electrical time delay (in milliseconds) between a control loop command and actual motor RPM adjustment.
* **Sensor Noise Level ($w$):** Injects Additive White Gaussian Noise (AWGN) into the virtual gyroscope and accelerometer outputs to test state-estimation resilience and $K_d$ derivative spike management.

---

### 2. Simulation Presets

#### Structural Presets

* **Quadcopter:** Allocates flight control forces using a standard 4-motor mixer matrix configuration (X or + configuration).
* **Octocopter:** Reconfigures the C++ backend to utilize an 8-motor coaxial or radial mixer matrix, updating the underlying structural mass distribution and inertia tensors.

#### Trajectory Presets

* **Hover Preset:** Locks the target waypoint to a static 3D coordinate space ($x_0, y_0, z_0$) for baseline validation.
* **Straight Line Preset:** Updates the target destination linearly over a time variable ($t$) based on a constant velocity vector.
* **Circular Orbit Preset:** Feeds time-varying trigonometric parametric equations into the position controller to force the drone into a continuous orbital tracking path of radius $R$.