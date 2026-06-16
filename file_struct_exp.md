## HelixSim — File & Folder Breakdown

---

### `main.py` — The Wiring File

This is the **only** file that imports from every other module. It doesn't contain any logic of its own — its sole job is to instantiate all the pieces and connect them together at startup.

```python
# What main.py roughly does:
params  = DroneParams(...)           # from sim/
world   = PyBulletWorld(params)      # from physics/
ctrl    = FlightController(params)   # from control/
viz     = UrsinaVisualizer(params)   # from viz/
panel   = ControlPanel(...)          # from ui/

# Then kicks off the render loop and physics thread
```

If something needs to talk to something else, `main.py` is where that connection is made. No other file reaches across module boundaries.

---

### `sim/` — Pure Math, Zero Dependencies

This is the most important folder to keep clean. **Nothing in here imports PyBullet, Ursina, CustomTkinter, or anything external.** It's just Python and NumPy. This is also the first folder you'll port to C++ later.

| File | Role |
|---|---|
| `__init__.py` | Makes `sim/` a Python package so you can write `from sim.drone import DroneParams` |
| `drone.py` | A single dataclass holding all drone configuration: mass, arm length, propeller radius, number of motors. This object gets passed around everywhere as the single source of truth for current parameters |
| `thrust_model.py` | Contains the equation `k_T = C_T * ρ * D⁴`. Takes a `DroneParams` object, returns per-motor thrust and reactive torque values. Nothing else — just the math |
| `motor_mixing.py` | The mixing matrix. Given desired total thrust + roll/pitch/yaw torques, it calculates what RPM each individual motor needs to spin at. Has two implementations: one for Quadcopter (4-motor cross/X layout) and one for Octocopter (8-motor) |
| `trajectory.py` | Three classes — `HoverTrajectory`, `StraightLineTrajectory`, `CircularLoopTrajectory` — each with a `position_at(t)` method that returns the desired XYZ position at simulation time `t`. The flight controller calls these every tick to know where the drone should be |

---

### `control/` — The Brain

Also pure math, no external dependencies. This is what makes the drone fly autonomously rather than just fall.

| File | Role |
|---|---|
| `__init__.py` | Makes `control/` a package |
| `pid.py` | A single generic `PIDController` class. Takes `kp`, `ki`, `kd` gains and an output limit. Has an `update(setpoint, measurement, dt)` method and anti-windup logic. Completely reusable — the flight controller creates six instances of this (one per control axis) |
| `flight_controller.py` | The cascade PID brain. Every simulation tick it: (1) asks `trajectory.py` where the drone should be, (2) runs the outer position PID loop to compute a desired attitude, (3) runs the inner attitude PID loop to compute desired motor torques, (4) calls `motor_mixing.py` to convert torques into individual motor RPMs, (5) returns the final `[F, τ]` force/torque vectors that get handed to PyBullet |

---

### `physics/` — The Only File That Touches PyBullet

This folder is deliberately thin. It is a **wrapper around PyBullet**, nothing more.

| File | Role |
|---|---|
| `__init__.py` | Makes `physics/` a package |
| `pybullet_world.py` | Handles everything PyBullet-specific: connecting to the physics server, loading `drone.urdf`, setting gravity, calling `applyExternalForce()` and `applyExternalTorque()` with the values from the flight controller, stepping the simulation with `stepSimulation()`, and reading back position + orientation via `getBasePositionAndOrientation()`. Returns a `DroneState` dict/dataclass that everything else consumes |

When you eventually replace PyBullet with your own C++ RK4 integrator, **you rewrite only this one file**. The flight controller, visualizer, and UI don't know or care what's doing the integration.

---

### `ui/` — What the User Sees and Touches

Only imports `DroneParams` and `DroneState`. Never imports from `viz/` or `physics/`.

| File | Role |
|---|---|
| `__init__.py` | Makes `ui/` a package |
| `control_panel.py` | The CustomTkinter dark-mode window. Contains all the sliders (mass, arm length, prop radius), dropdowns (Quad/Octo preset, trajectory preset), and Start/Stop buttons. When a slider moves, it updates the `DroneParams` object and signals `main.py` — it does **not** directly call the physics engine |
| `telemetry_charts.py` | A Matplotlib figure embedded inside the CTk window via `FigureCanvasTkAgg`. Has three rolling line charts: altitude vs time, velocity vs time, PID error vs time. Gets fed the latest `DroneState` every frame via a `push(state)` method and redraws using `draw_idle()` so it doesn't block the UI |

---

### `viz/` — What the 3D Viewport Renders

Only imports `DroneParams` and `DroneState`. Never imports from `ui/` or `physics/`.

| File | Role |
|---|---|
| `__init__.py` | Makes `viz/` a package |
| `visualizer_base.py` | An abstract base class (ABC) with four method stubs: `initialize()`, `update(state)`, `apply_params(params)`, `shutdown()`. This is your **future-proofing contract**. The rest of the codebase only ever holds a reference of type `DroneVisualizerBase` — it never knows which rendering engine is active |
| `ursina_visualizer.py` | Implements `DroneVisualizerBase` using Ursina. Creates a hierarchy of Ursina entities: a root entity for the drone body, child entities for each arm, and flat disc entities for each propeller. Every frame, `update(state)` sets the root entity's position and rotation from the `DroneState` quaternion, and spins the propeller discs proportional to motor RPMs. `apply_params(params)` rescales arm lengths and propeller sizes when sliders change |

To swap Ursina for ModernGL later, you write `moderngl_visualizer.py` implementing the same ABC, then change **one line** in `main.py`. Nothing else in the codebase changes.

---

### `assets/` — Static Files

| File | Role |
|---|---|
| `drone.urdf` | A URDF (Unified Robot Description Format) XML file describing the drone's physical shape to PyBullet — the body box dimensions, mass, inertia tensor, and link geometry for the arms. PyBullet reads this at startup to create the rigid body. Ursina does **not** use this file; it builds its own visual geometry from primitives |

---

### `config/` — Tuning Without Code Changes

| File | Role |
|---|---|
| `defaults.yaml` | All magic numbers live here: PID gains (`kp`, `ki`, `kd` for position and attitude loops), default drone parameters, simulation frequency (240 Hz physics, 60 Hz render), gravity constant, default trajectory parameters (circle radius, hover altitude). During calibration week you'll be editing only this file — no Python changes needed |

---

### The Key Principle Across All of It

Every folder knows less than the one above it:

```
main.py          knows about everything
    │
    ├── ui/      knows DroneParams + DroneState only
    ├── viz/     knows DroneParams + DroneState only
    ├── control/ knows DroneParams + DroneState only
    ├── physics/ knows DroneParams + DroneState + PyBullet
    └── sim/     knows nothing except NumPy
```

`DroneParams` and `DroneState` are the two objects that flow through the entire system. Everything else is implementation detail hidden behind its own folder boundary.