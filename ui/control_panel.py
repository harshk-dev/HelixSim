from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QComboBox, QWidget, QTabWidget, QFormLayout, QPushButton,
                            QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt
import sys
from .telemetry_charts import TelemetryChart

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model_presets = ["QuadCopter","OctaCopter"]
        self.trajectory_presets = ["Hover","Straight Line","Circular Loop"]
        self.setWindowTitle("HelixSim - Control Panel")
        self.resize(1000, 700)

        central_Widget = QWidget()
        self.setCentralWidget(central_Widget)

        main_layout = QVBoxLayout(central_Widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        
        main_layout.addLayout(self.top_layout())
        main_layout.addLayout(self.middle_layout(),stretch=2)
        main_layout.addWidget(self.bottom_layout(),stretch=2)

    def top_layout(self):
        layout = QGridLayout()
        heading = QLabel("HelixSim")
        heading.setStyleSheet("font-size: 24px; letter-spacing: 5px; color: #38bdf8;")

        start_btn = QPushButton()
        start_btn.setText("▶ START ENGINE")

        layout.addWidget(heading,0,0,1,3,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(start_btn,0,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        return layout

    def middle_layout(self):
        layout = QHBoxLayout()

        layout.addWidget(self.preset_group(),stretch=1)
        layout.addWidget(self.param_group(),stretch=2)
        return layout

    def preset_group(self):
        layout = QVBoxLayout()
        group = QGroupBox("Presets")

        model_label = QLabel("Model")
        model_combo = QComboBox()
        model_combo.addItems(self.model_presets)

        trajectory_label = QLabel("Trajectory")
        trajectory_combo = QComboBox()
        trajectory_combo.addItems(self.trajectory_presets)

        layout.addWidget(model_label)
        layout.addWidget(model_combo)
        layout.addWidget(trajectory_label)
        layout.addWidget(trajectory_combo)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def param_group(self):
        layout = QVBoxLayout()
        group = QGroupBox("Adjustable Param")
        tab = QTabWidget()

        tab.addTab(self.struct_tab(),"Structural")
        tab.addTab(self.env_tab(),"Environmental")
        tab.addTab(self.control_tab(),"Control Param")

        layout.addWidget(tab)
        group.setLayout(layout)
        return group

    def struct_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        mass_spin = QDoubleSpinBox()
        mass_spin.setSuffix(" Kg")
        mass_spin.setValue(1)
        mass_spin.setDecimals(6)
        mass_spin.setSingleStep(0.25)
        mass_spin.setRange(0.0,1000.0)

        arm_len_spin = QDoubleSpinBox()
        arm_len_spin.setSuffix(" m")
        arm_len_spin.setValue(0.01)
        arm_len_spin.setDecimals(6)
        arm_len_spin.setSingleStep(0.25)
        arm_len_spin.setRange(0.0,100.0)

        prop_len_spin = QDoubleSpinBox()
        prop_len_spin.setSuffix(" mm")
        prop_len_spin.setValue(4)
        prop_len_spin.setDecimals(3)
        prop_len_spin.setSingleStep(0.25)
        prop_len_spin.setRange(0.0,1000.0)

        layout.addRow(QLabel("Mass:"), mass_spin)
        layout.addRow(QLabel("Arm Length:"), arm_len_spin)
        layout.addRow(QLabel("Propeller Length:"), prop_len_spin)
        return tab

    def env_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        wind_velo_group = QGroupBox()
        wind_velo_spin_layout = self.vector_spin_layout(
            suffix=" m/s",
            defult_value=0,
            decimals=3,
            steps=0.25,
            min=-10000,
            max=10000,
            colname=["X","Y","Z"]
        )
        wind_velo_group.setLayout(wind_velo_spin_layout)

        turbulence_group = QGroupBox()
        turb_layout = QFormLayout()

        # Intensity (How strong is the random gust?)
        turb_intensity = QDoubleSpinBox()
        turb_intensity.setSuffix(" m/s")
        turb_intensity.setDecimals(2)
        turb_intensity.setSingleStep(0.5)
        turb_intensity.setRange(0.0, 50.0)
        turb_intensity.setValue(0.0) # Default to smooth air

        # Frequency (How chaotic/fast are the gusts?)
        gust_freq = QDoubleSpinBox()
        gust_freq.setSuffix(" Hz")
        gust_freq.setDecimals(2)
        gust_freq.setSingleStep(0.1)
        gust_freq.setRange(0.0, 20.0)
        gust_freq.setValue(0.0)

        turb_layout.addRow("Turbulence Intensity (Amplitude):", turb_intensity)
        turb_layout.addRow("Gust Frequency (Chaos rate):", gust_freq)
        turbulence_group.setLayout(turb_layout)

        gravity_spin = QDoubleSpinBox()
        gravity_spin.setSuffix(" m/s²")
        gravity_spin.setValue(9.81)
        gravity_spin.setDecimals(3)
        gravity_spin.setSingleStep(0.25)
        gravity_spin.setRange(0.0,100.0)

        atmos_pressure_spin = QDoubleSpinBox()
        atmos_pressure_spin.setSuffix(" N/m²")
        atmos_pressure_spin.setValue(1)
        atmos_pressure_spin.setDecimals(3)
        atmos_pressure_spin.setSingleStep(0.25)
        atmos_pressure_spin.setRange(0.0,100.0)

        layout.addRow(QLabel("Wind Velocity:"),wind_velo_group)
        layout.addRow(QLabel("Turbulence & Gusts:"),turbulence_group)
        layout.addRow(QLabel("Gravity:"),gravity_spin)
        layout.addRow(QLabel("Atmospheric Pressure:"),atmos_pressure_spin)

        return tab

    def control_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        pid_group = QGroupBox()
        pid_spin_layout = self.vector_spin_layout(
            suffix="",
            defult_value=0,
            decimals=6,
            steps=0.001,
            min=0,
            max=100,
            colname=["Kp", "Ki", "Kd"]
        )
        pid_group.setLayout(pid_spin_layout)

        # 1. ESC Latency (Usually between 1ms and 50ms)
        esc_latency_spin = QDoubleSpinBox()
        esc_latency_spin.setSuffix(" ms")
        esc_latency_spin.setDecimals(1)
        esc_latency_spin.setSingleStep(1.0)
        esc_latency_spin.setRange(0.0, 100.0)
        esc_latency_spin.setValue(5.0) # 5ms is a realistic default for DShot ESCs

        # 2. Sensor Noise (Standard Deviation / Amplitude)
        sensor_noise_spin = QDoubleSpinBox()
        sensor_noise_spin.setSuffix(" σ") # Sigma symbol for standard deviation
        sensor_noise_spin.setDecimals(3)
        sensor_noise_spin.setSingleStep(0.05)
        sensor_noise_spin.setRange(0.0, 10.0)
        sensor_noise_spin.setValue(0.1) # A small amount of base noise

        layout.addRow(QLabel("PID Gains:"),pid_group)
        layout.addRow(QLabel("ESC/Motor Latency"), esc_latency_spin)
        layout.addRow(QLabel("IMU Sensor Noise"), sensor_noise_spin)

        return tab

    def vector_spin_layout(self,suffix,defult_value,decimals,steps,min,max,colname):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        for col in colname:
            layout = QFormLayout()
            spin = QDoubleSpinBox()
            spin.setSuffix(suffix)
            spin.setDecimals(decimals)
            spin.setSingleStep(steps)
            spin.setRange(min,max)
            spin.setValue(defult_value)
            layout.addRow(col,spin)
            main_layout.addLayout(layout)

        return main_layout

    def bottom_layout(self):
        widget = TelemetryChart()
        return widget
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlPanel()
    window.show()
    sys.exit(app.exec())