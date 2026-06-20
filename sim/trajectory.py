import multiprocessing
import sys
import time
import numpy as np
import os

# ==========================================
# PROCESS A: PURE 3D ENGINE (URSINA)
# ==========================================
def run_3d_engine(shared_speed, shared_is_playing):
    # CRITICAL: Ursina must be imported INSIDE this function so it 
    # gets its own dedicated OpenGL context, completely isolated from Qt.
    from ursina import Ursina, Entity, DirectionalLight, camera, color, time as u_time, window

    # Initialize Engine
    app = Ursina(title="HelixSim - 3D Viewport", size=(800, 600))
    window.color = color.rgb(15, 23, 42)

    # Build the Scene
    spinning_cube = Entity(model='cube', color=color.orange, scale=(2, 2, 2))
    DirectionalLight(y=2, z=3, shadows=True)
    camera.position = (0, 3, -10)
    camera.look_at(spinning_cube)

    # THE FIX: Attach the update loop directly to the cube entity
    def spin_update():
        if shared_is_playing.value == 1:
            spinning_cube.rotation_y += shared_speed.value * u_time.dt

    # Tell Ursina to run this function every frame for this specific cube
    spinning_cube.update = spin_update

    app.run()


# ==========================================
# PROCESS B: PURE TELEMETRY DASHBOARD (PYQT6)
# ==========================================
def run_ui_dashboard(shared_speed, shared_is_playing):
    # Import UI libraries strictly inside this process
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                 QHBoxLayout, QLabel, QSlider, QPushButton, QFrame)
    from PyQt6.QtCore import Qt, QTimer
    import pyqtgraph as pg

    class TelemetryStation(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("HelixSim - Command Center")
            self.resize(800, 600)
            self.setStyleSheet("background-color: #0f172a;") # Slate background

            # Data Arrays for the Live Graphs
            self.max_points = 100
            self.time_data = np.zeros(self.max_points)
            self.rpm_data = np.zeros(self.max_points)
            self.start_time = time.time()

            # --- LAYOUT SETUP ---
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QHBoxLayout(central_widget)

            # --- LEFT SIDEBAR ---
            self.sidebar = QFrame()
            self.sidebar.setFixedWidth(250)
            self.sidebar.setStyleSheet("background-color: #1e293b; border-radius: 8px;")
            sidebar_layout = QVBoxLayout(self.sidebar)

            title = QLabel("ENGINE CONTROLS")
            title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            sidebar_layout.addWidget(title)

            # Speed Slider
            self.speed_label = QLabel(f"Rotation Speed: {int(shared_speed.value)}")
            self.speed_label.setStyleSheet("color: white; margin-top: 20px;")
            sidebar_layout.addWidget(self.speed_label)

            self.slider = QSlider(Qt.Orientation.Horizontal)
            self.slider.setMinimum(10)
            self.slider.setMaximum(500)
            self.slider.setValue(int(shared_speed.value))
            self.slider.valueChanged.connect(self.on_slider_move)
            sidebar_layout.addWidget(self.slider)

            # Play/Pause Button
            self.play_btn = QPushButton("▶ START ENGINE")
            self.play_btn.setStyleSheet("""
                QPushButton { background-color: #0ea5e9; color: white; padding: 12px; font-weight: bold; margin-top: 30px;}
                QPushButton:hover { background-color: #0284c7; }
            """)
            self.play_btn.clicked.connect(self.toggle_engine)
            sidebar_layout.addWidget(self.play_btn)
            sidebar_layout.addStretch()

            # --- RIGHT GRAPHS ---
            self.graph_rpm = pg.PlotWidget(title="Live Engine RPM")
            self.graph_rpm.setBackground('#1e293b')
            self.graph_rpm.showGrid(x=True, y=True, alpha=0.3)
            self.graph_rpm.setYRange(0, 600)
            self.curve_rpm = self.graph_rpm.plot(pen=pg.mkPen('#0ea5e9', width=2))

            main_layout.addWidget(self.sidebar)
            main_layout.addWidget(self.graph_rpm, stretch=1)

            # Start the graph update loop (20 FPS)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_telemetry)
            self.timer.start(50)

        # --- UI LOGIC & BRIDGE UPDATES ---
        def on_slider_move(self, val):
            self.speed_label.setText(f"Rotation Speed: {val}")
            shared_speed.value = float(val) # Send to 3D engine

        def toggle_engine(self):
            if shared_is_playing.value == 0:
                shared_is_playing.value = 1
                self.play_btn.setText("⏸ PAUSE ENGINE")
                self.play_btn.setStyleSheet("QPushButton { background-color: #ef4444; color: white; padding: 12px; font-weight: bold; margin-top: 30px;}")
            else:
                shared_is_playing.value = 0
                self.play_btn.setText("▶ START ENGINE")
                self.play_btn.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 12px; font-weight: bold; margin-top: 30px;}")

        def update_telemetry(self):
            if shared_is_playing.value == 0:
                return

            # Shift data left
            self.time_data[:-1] = self.time_data[1:]
            self.rpm_data[:-1] = self.rpm_data[1:]

            # Generate new data point based on the current speed + some random engine noise
            current_time = time.time() - self.start_time
            base_rpm = shared_speed.value
            noise = np.random.normal(0, base_rpm * 0.05) 
            
            self.time_data[-1] = current_time
            self.rpm_data[-1] = base_rpm + noise

            # Draw the new line
            self.curve_rpm.setData(self.time_data, self.rpm_data)

    # Boot the Qt App
    qt_app = QApplication(sys.argv)
    window = TelemetryStation()
    window.show()
    sys.exit(qt_app.exec())


# ==========================================
# MASTER LAUNCHER (THE BRIDGE)
# ==========================================
if __name__ == "__main__":
    # Required for stable Python multiprocessing
    multiprocessing.freeze_support()

    # CRITICAL LINUX FIX: Force strict isolation between processes.
    # This completely eliminates the Wayland/X11 graphics crashes.
    multiprocessing.set_start_method('spawn', force=True)

    # 1. Create the Shared Memory Variables
    # 'd' = double (float), 'i' = integer (boolean flag)
    shared_speed = multiprocessing.Value('d', 150.0) 
    shared_is_playing = multiprocessing.Value('i', 0)

    # 2. Assign the processes
    p_engine = multiprocessing.Process(target=run_3d_engine, args=(shared_speed, shared_is_playing))
    p_ui = multiprocessing.Process(target=run_ui_dashboard, args=(shared_speed, shared_is_playing))

    # 3. Fire them up
    p_engine.start()
    p_ui.start()

    # 4. Graceful Shutdown 
    # Wait for the user to close the UI window, then forcefully kill the 3D engine.
    p_ui.join()
    p_engine.terminate()