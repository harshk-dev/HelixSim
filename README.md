# HelixSim 🚁
### Parametric Drone Flight Simulator

A real-time, physics-compliant drone simulator built for the IIT Palakkad internship program. HelixSim lets you dynamically vary drone parameters — propeller length, mass, motor thrust coefficients — and watch the physics respond instantly in a live 3D viewport alongside telemetry charts.

Built with a Python-first MVP architecture. Performance-critical modules are designed for future C++ migration via Pybind11.

---

## Demo

> Quadcopter tracing a circular loop trajectory at 2m radius, 1m altitude.
> *(Screenshot / GIF goes here)*

---

## Features

- **Parametric simulation** — adjust mass, arm length, propeller radius, and thrust coefficients via live sliders; physics recomputes instantly
- **Structural presets** — Quadcopter (4-motor) and Octocopter (8-motor) motor mixing matrices
- **Trajectory presets** — Hover, Straight Line, and Circular Loop, all parameterized over time `t`
- **Cascade PID flight control** — outer position/velocity loop + inner attitude/angular rate loop
- **Live 3D viewport** — Ursina engine renders the drone with correct orientation, arm scaling, and propeller spin
- **Live telemetry charts** — altitude, velocity, and PID error streaming at 60 Hz
- **Physics via PyBullet** — Bullet engine handles rigid-body dynamics; HelixSim applies computed forces each step

---

## Architecture

```
helixsim/
├── main.py                        # Entry point
├── sim/                           # Pure math — future C++ migration target
│   ├── __init__.py
│   ├── drone.py                   # DroneParams dataclass
│   ├── thrust_model.py            # k_T = C_T * ρ * D⁴, per-motor thrust/torque
│   ├── motor_mixing.py            # Quad / Octo mixing matrices
│   └── trajectory.py              # Hover, StraightLine, CircularLoop
├── control/                       # PID control — future C++ migration target
│   ├── __init__.py
│   ├── pid.py                     # Generic PIDController with anti-windup
│   └── flight_controller.py       # Cascade PID (position → attitude → motors)
├── physics/
│   ├── __init__.py
│   └── pybullet_world.py          # PyBullet setup, force application, step
├── ui/
│   ├── __init__.py
│   ├── control_panel.py           # CustomTkinter sliders, dropdowns, start/stop
│   └── telemetry_charts.py        # Matplotlib embedded live charts
├── viz/
│   ├── __init__.py
│   ├── visualizer_base.py         # Abstract base (swap Ursina → ModernGL here)
│   └── ursina_visualizer.py       # Ursina entity hierarchy and update loop
├── assets/
│   └── drone.urdf                 # Drone body description for PyBullet
└── config/
    └── defaults.yaml              # PID gains, sim constants, default params
```

**Data flow:**

```
CTk UI sliders
      │ param writes
      ▼
FlightController  ◄──  TrajectoryPlanner (waypoints)
      │ cascade PID
      ▼
ThrustModel + MotorMixing  →  [F, τ] per motor
      │
      ▼
PyBullet (applyExternalForce / stepSimulation)
      │ DroneState (position, velocity, orientation)
      ▼
      ├──► UrsinaVisualizer (3D viewport, 60 Hz)
      └──► TelemetryCharts (altitude, velocity, PID error)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Physics engine | PyBullet (Bullet3) |
| Flight control | Python (cascade PID) |
| GUI | CustomTkinter |
| Telemetry charts | Matplotlib (embedded) |
| 3D visualization | Ursina (Panda3D backend) |
| Config | PyYAML |
| Linear algebra | NumPy, SciPy |

---

## Installation

### Prerequisites

- Python 3.10+
- Arch Linux (primary target) or any Linux distro

### Steps

```bash
# Clone the repository
git clone https://github.com/harshk-dev/helixsim.git
cd helixsim

# Install Python dependencies
pip install -r requirements.txt

# Run
python main.py
```

### requirements.txt

```
pybullet
customtkinter
matplotlib
ursina
numpy
scipy
pyyaml
```

---

## Usage

1. **Launch** — run `python main.py`. The HelixSim control panel and Ursina 3D viewport open side by side.
2. **Select a structural preset** — choose Quadcopter or Octocopter from the dropdown. The 3D model updates its arm count instantly.
3. **Adjust parameters** — drag sliders for mass, arm length, and propeller radius. The 3D model scales visually in real-time.
4. **Select a trajectory** — choose Hover, Straight Line, or Circular Loop.
5. **Start the simulation** — click ▶ Start. PyBullet begins stepping; the PID controller tracks the trajectory; the 3D viewport and charts update live.
6. **Tune PID gains** — edit `config/defaults.yaml` and restart. No code changes needed.

---

## Physics Model

HelixSim models the drone as a 6-DOF rigid body. Each motor `i` generates thrust and reactive torque:

```
T_i = k_T * ω_i²       (thrust)
Q_i = k_Q * ω_i²       (reactive yaw torque)

k_T = C_T * ρ * D⁴     (thrust coefficient from propeller geometry)
k_Q = C_Q * ρ * D⁵

where D = 2 * prop_radius, ρ = 1.225 kg/m³
```

Net forces and torques are assembled via the motor mixing matrix and passed to PyBullet's `applyExternalForce` and `applyExternalTorque` each simulation step.

---

## Trajectory Presets

All trajectories are parameterized over simulation time `t`:

**Hover:**
```
p(t) = (x₀, y₀, z_hover)
```

**Straight Line:**
```
p(t) = origin + (target − origin) × clamp(t / T_travel, 0, 1)
```

**Circular Loop:**
```
x(t) = cx + R × cos(ω_c × t)
y(t) = cy + R × sin(ω_c × t)
z(t) = z_hover
```

Radius `R` and angular velocity `ω_c` are configurable via the UI.

---

## C++ Migration Roadmap

HelixSim is designed so that performance-critical Python modules can be incrementally replaced with C++ extensions (via Pybind11) without touching the UI, visualizer, or PyBullet integration.

| Priority | Module | Reason |
|---|---|---|
| 1st | `sim/thrust_model.py` | Pure math, easiest port |
| 2nd | `sim/motor_mixing.py` | Matrix ops, maps directly to Eigen |
| 3rd | `control/pid.py` | Tight loop, biggest latency win |
| 4th | `control/flight_controller.py` | Depends on PID being ported first |
| 5th | `physics/pybullet_world.py` | Replace PyBullet with custom RK4 integrator |

Each port adds a `src/` C++ module and a Pybind11 `.so` file. The corresponding Python file becomes a thin import wrapper. Nothing outside that module changes.

---

## Configuration

All tunable constants live in `config/defaults.yaml`:

```yaml
drone:
  mass_kg: 1.0
  arm_length_m: 0.25
  prop_radius_m: 0.1
  num_motors: 4

pid:
  position:
    kp: 1.2
    ki: 0.01
    kd: 0.5
  attitude:
    kp: 6.0
    ki: 0.05
    kd: 0.8

sim:
  physics_hz: 240
  render_hz: 60
  gravity: -9.81

trajectory:
  circle_radius_m: 2.0
  circle_speed_mps: 1.0
  hover_altitude_m: 1.5
```

---

## Project Status

| Phase | Status | Days |
|---|---|---|
| Environment + bridge skeleton | ✅ Complete | 1–5 |
| Physics engine integration | ✅ Complete | 6–12 |
| PID + trajectories + Ursina | 🔄 In progress | 13–19 |
| Presets + validation + polish | ⏳ Upcoming | 20–25 |

---

## Acknowledgements

HelixSim is built as part of the **IIT Palakkad Summer Internship 2026** program.  
Physics engine: [PyBullet / Bullet3](https://pybullet.org)  
3D rendering: [Ursina Engine](https://www.ursinaengine.org)  
GUI: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

## License

MIT License — see `LICENSE` for details.