from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QComboBox, QWidget, QTabWidget, QFormLayout, QPushButton,
                            QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt
import sys
from .telemetry_charts import TelemetryChart
from sim import SimDataManager
from functools import partial
from numpy import array,ndarray

class ControlPanel(QMainWindow):
    def __init__(self,data_manager: SimDataManager):
        super().__init__()
        self.model_presets = ["QuadCopter","OctaCopter"]
        self.trajectory_presets = ["Hover","Straight Line","Circular Loop"]
        self.data_manager = data_manager
        self.setWindowTitle("HelixSim - Control Panel")
        self.resize(1000, 700)
        self.setStyleSheet(self.get_global_theme())

        central_Widget = QWidget()
        self.setCentralWidget(central_Widget)

        main_layout = QVBoxLayout(central_Widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        
        main_layout.addLayout(self.top_layout())
        main_layout.addLayout(self.middle_layout(),stretch=2)
        main_layout.addWidget(self.bottom_layout(),stretch=2)

    def get_global_theme(self):
        return """
        /* --- Global Base & Typography --- */
        * {
            /* Enforce one professional, modern font across EVERY widget */
            font-family: "Roboto", "Segoe UI", "Noto Sans", "Helvetica Neue", sans-serif;
        }

        QWidget {
            background-color: #141414; /* Deep graphite background */
            color: #D4D4D4; /* Soft off-white for high legibility */
            font-size: 13px;
        }

        QMainWindow {
            background-color: #0E0E0E; /* Even darker for the absolute background */
        }

        /* --- Target the Main Heading --- */
        QLabel#mainTitle {
            font-size: 38px; /* Increased massively */
            font-weight: 900; /* Maximum boldness */
            letter-spacing: 8px; /* Wide, cinematic spacing */
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        /* --- Group Boxes --- */
        QGroupBox {
            background-color: #1A1A1A;
            border: 1px solid #2A2A2A;
            border-radius: 4px;
            margin-top: 1.5em;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #FF9800; /* Amber */
        }

        /* --- Input Fields --- */
        QDoubleSpinBox, QComboBox {
            background-color: #222222;
            border: 1px solid #333333;
            border-radius: 3px;
            padding: 4px 8px;
            min-height: 24px;
            selection-background-color: #FF9800;
            selection-color: #000000;
        }
        QDoubleSpinBox:hover, QComboBox:hover {
            border: 1px solid #555555;
        }
        QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #FF9800;
            background-color: #2A2A2A;
        }

        /* Clean up SpinBox Arrows */
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background-color: #2A2A2A;
            border: none;
            width: 16px;
        }
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #3A3A3A;
        }

        /* --- Tabs --- */
        QTabWidget::pane {
            border: 1px solid #2A2A2A;
            background-color: #1A1A1A;
            top: -1px; 
        }
        QTabBar::tab {
            background-color: #141414;
            border: 1px solid #2A2A2A;
            border-bottom: none;
            padding: 8px 20px;
            margin-right: 2px;
            color: #777777;
            font-weight: bold; /* Make unselected tabs slightly punchier */
        }
        QTabBar::tab:selected {
            background-color: #1A1A1A;
            color: #FFFFFF;
            border-top: 2px solid #FF9800; /* Active tab amber line */
        }
        QTabBar::tab:hover:!selected {
            background-color: #222222;
            color: #AAAAAA;
        }

        /* --- Standard Buttons --- */
        QPushButton {
            background-color: #2A2A2A;
            border: 1px solid #3A3A3A;
            border-radius: 3px;
            padding: 6px 16px;
            font-weight: bold;
            color: #D4D4D4;
        }
        QPushButton:hover {
            background-color: #333333;
            border: 1px solid #555555;
        }
        QPushButton:pressed {
            background-color: #FF9800;
            color: #000000;
        }

        /* --- Specific Start Engine Button --- */
        QPushButton#startEngineBtn {
            background-color: #E65100; /* Deep warning orange */
            color: white;
            border: 1px solid #FF9800;
            font-size: 15px; /* Slightly larger text */
            font-weight: 900; /* Extra bold */
            letter-spacing: 2px;
            padding: 12px 24px;
            border-radius: 4px;
        }
        QPushButton#startEngineBtn:hover {
            background-color: #FF6D00; /* Brighter orange on hover */
            border: 1px solid #FFA726;
        }
        QPushButton#startEngineBtn:pressed {
            background-color: #F57C00;
        }
        """

    def top_layout(self):
        layout = QGridLayout()
        
        heading = QLabel('<span style="color: #FF9800;">⬢</span> <span style="color: #FFFFFF;">HELIX</span><span style="color: #FF9800;">SIM</span>')
        heading.setObjectName("mainTitle")

        start_btn = QPushButton()
        start_btn.setText("▶ START ENGINE")
        start_btn.setObjectName("startEngineBtn")
        start_btn.clicked.connect(self._on_start_btn)

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
        model_combo.currentTextChanged.connect(
            self.data_manager.set_structural_preset
            )

        trajectory_label = QLabel("Trajectory")
        trajectory_combo = QComboBox()
        trajectory_combo.addItems(self.trajectory_presets)
        trajectory_combo.currentTextChanged.connect(
            self.data_manager.set_trajectory_preset
        )

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
        mass_spin.valueChanged.connect(partial(
            self._on_change,
            category='struct_param',
            metric='mass'
        ))

        arm_len_spin = QDoubleSpinBox()
        arm_len_spin.setSuffix(" m")
        arm_len_spin.setValue(0.01)
        arm_len_spin.setDecimals(6)
        arm_len_spin.setSingleStep(0.25)
        arm_len_spin.setRange(0.0,100.0)
        arm_len_spin.valueChanged.connect(partial(
            self._on_change,
            category='struct_param',
            metric='arm_length'
        ))

        prop_len_spin = QDoubleSpinBox()
        prop_len_spin.setSuffix(" mm")
        prop_len_spin.setValue(4)
        prop_len_spin.setDecimals(3)
        prop_len_spin.setSingleStep(0.25)
        prop_len_spin.setRange(0.0,1000.0)
        prop_len_spin.valueChanged.connect(partial(
            self._on_change,
            category='struct_param',
            metric='prop_length'
        ))

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
            colname=["X","Y","Z"],
            category="env_param",
            metric_prefix="wind_velocity_"
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
        turb_intensity.valueChanged.connect(partial(
            self._on_change,
            category='env_param',
            metric='turbulence_intensity'
        ))

        # Frequency (How chaotic/fast are the gusts?)
        gust_freq = QDoubleSpinBox()
        gust_freq.setSuffix(" Hz")
        gust_freq.setDecimals(2)
        gust_freq.setSingleStep(0.1)
        gust_freq.setRange(0.0, 20.0)
        gust_freq.setValue(0.0)
        gust_freq.valueChanged.connect(partial(
            self._on_change,
            category='env_param',
            metric='gust_frequency'
        ))

        turb_layout.addRow("Turbulence Intensity:", turb_intensity)
        turb_layout.addRow("Gust Frequency:", gust_freq)
        turbulence_group.setLayout(turb_layout)

        gravity_spin = QDoubleSpinBox()
        gravity_spin.setSuffix(" m/s²")
        gravity_spin.setValue(9.81)
        gravity_spin.setDecimals(3)
        gravity_spin.setSingleStep(0.25)
        gravity_spin.setRange(0.0,100.0)
        gravity_spin.valueChanged.connect(partial(
            self._on_change,
            category='env_param',
            metric='gravity'
        ))

        atmos_pressure_spin = QDoubleSpinBox()
        atmos_pressure_spin.setSuffix(" N/m²")
        atmos_pressure_spin.setValue(1)
        atmos_pressure_spin.setDecimals(3)
        atmos_pressure_spin.setSingleStep(0.25)
        atmos_pressure_spin.setRange(0.0,100.0)
        atmos_pressure_spin.valueChanged.connect(partial(
            self._on_change,
            category='env_param',
            metric='atmospheric_pressure'
        ))

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
            colname=["Kp", "Ki", "Kd"],
            category="control_param",
            metric_prefix="pid_"
        )
        pid_group.setLayout(pid_spin_layout)

        # 1. ESC Latency (Usually between 1ms and 50ms)
        esc_latency_spin = QDoubleSpinBox()
        esc_latency_spin.setSuffix(" ms")
        esc_latency_spin.setDecimals(1)
        esc_latency_spin.setSingleStep(1.0)
        esc_latency_spin.setRange(0.0, 100.0)
        esc_latency_spin.setValue(5.0) # 5ms is a realistic default for DShot ESCs
        esc_latency_spin.valueChanged.connect(partial(
            self._on_change,
            category='control_param',
            metric='esc_latency'
        ))

        # 2. Sensor Noise (Standard Deviation / Amplitude)
        imu_sensor_noise_spin = QDoubleSpinBox()
        imu_sensor_noise_spin.setSuffix(" σ") # Sigma symbol for standard deviation
        imu_sensor_noise_spin.setDecimals(3)
        imu_sensor_noise_spin.setSingleStep(0.05)
        imu_sensor_noise_spin.setRange(0.0, 10.0)
        imu_sensor_noise_spin.setValue(0.1) # A small amount of base noise
        imu_sensor_noise_spin.valueChanged.connect(partial(
            self._on_change,
            category='control_param',
            metric='imu_sensor_noise'
        ))

        layout.addRow(QLabel("PID Gains:"),pid_group)
        layout.addRow(QLabel("ESC/Motor Latency"), esc_latency_spin)
        layout.addRow(QLabel("IMU Sensor Noise"), imu_sensor_noise_spin)

        return tab

    def vector_spin_layout(self,suffix,defult_value,decimals,steps,min,max,colname,category,metric_prefix):
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
            spin.valueChanged.connect(partial(
                self._on_change,
                category=category,
                metric=f"{metric_prefix}{col.lower()}"
            ))

            layout.addRow(col,spin)
            main_layout.addLayout(layout)

        return main_layout

    def bottom_layout(self):
        widget = TelemetryChart()
        return widget
    
    def _on_start_btn(self):
        if self.data_manager.data.run_sim == 0:
            self.data_manager.data.run_sim = 1
        else:
            self.data_manager.data.run_sim = 0
        
    def _on_change(self,change,category,metric):
        if category == "_g":
            target_attr = self.data_manager.data
        else:
            target_attr = getattr(self.data_manager.data,category)

        with self.data_manager.get_lock():
            setattr(target_attr,metric,change)

        # print(f"[CHANGE] {metric} = {getattr(getattr(self.data_manager.data,category),metric)}")
        # print(f"[CHANGE] Struct = {self.data_manager.data.sim_presets.structural_preset}")
        # print(f"[CHANGE] Trajectory = {self.data_manager.data.sim_presets.trajectory_preset}")

if __name__ == "__main__":
    data_manager = SimDataManager('config/defaults.yaml')
    app = QApplication(sys.argv)
    window = ControlPanel(data_manager)
    window.show()
    sys.exit(app.exec())