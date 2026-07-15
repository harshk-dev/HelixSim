from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QComboBox, QWidget, QTabWidget, QFormLayout, QPushButton,
                            QGridLayout, QDoubleSpinBox, QStackedWidget)
from PyQt6.QtCore import Qt
from .telemetry_charts import TelemetryChart
from sim import SimDataManager
from functools import partial

class ControlPanel(QMainWindow):
    def __init__(self, data_manager: SimDataManager):
        super().__init__()
        self.model_presets = ["QuadCopter", "OctaCopter"]
        self.trajectory_presets = ["Hover", "Straight Line", "Circular Loop"]
        self.camera_modes = ["Follow", "Fixed", "Origin"]
        self.data_manager = data_manager
        self.setWindowTitle("HelixSim - Control Panel")
        self.resize(1000, 750) 
        self.setStyleSheet(self.get_global_theme())

        central_Widget = QWidget()
        self.setCentralWidget(central_Widget)

        main_layout = QVBoxLayout(central_Widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        main_layout.addLayout(self.top_layout())
        main_layout.addLayout(self.middle_layout(), stretch=2)
        main_layout.addWidget(self.bottom_layout(), stretch=2)

    def get_global_theme(self):
        return """
        /* --- Core Theme Variables & Base Style --- */
        * {
            font-family: "Segoe UI", "Inter", "SF Pro Display", -apple-system, sans-serif;
        }

        QWidget {
            background-color: #212124; 
            color: #E2E2E5; 
            font-size: 12px;
        }

        QMainWindow {
            background-color: #18181A; 
        }

        /* --- Main Application Header --- */
        QLabel#mainTitle {
            font-size: 24px; 
            font-weight: 700; 
            letter-spacing: 4px; 
            text-transform: uppercase;
            color: #FFFFFF;
            margin-bottom: 2px;
        }

        /* --- Group Boxes (Panels) --- */
        QGroupBox {
            background-color: #262629;
            border: 1px solid #333336;
            border-radius: 4px;
            margin-top: 24px;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            top: 4px;
            padding: 2px 6px;
            color: #A5A5AA; 
        }

        /* --- Form Inputs & Controls --- */
        QDoubleSpinBox, QComboBox {
            background-color: #1C1C1E;
            border: 1px solid #3A3A3F;
            border-radius: 4px;
            padding: 4px 6px;
            min-height: 22px;
            color: #E2E2E5;
            selection-background-color: #365F91;
            selection-color: #FFFFFF;
        }
        QDoubleSpinBox:hover, QComboBox:hover {
            border: 1px solid #4C4C52;
        }
        QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #3772FF;
            background-color: #18181A;
        }

        /* Industrial Dropdown Styling */
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        QComboBox QAbstractItemView {
            background-color: #1C1C1E;
            border: 1px solid #3A3A3F;
            selection-background-color: #3772FF;
            selection-color: #FFFFFF;
        }

        /* Clean & Precise SpinBox Steps */
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background-color: #262629;
            width: 16px;
            border-left: 1px solid #3A3A3F;
        }
        QDoubleSpinBox::up-button { border-top-right-radius: 3px; }
        QDoubleSpinBox::down-button { border-bottom-right-radius: 3px; border-top: 1px solid #3A3A3F; }
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #333336;
        }

        /* --- Industrial Tab Architecture --- */
        QTabWidget::pane {
            border: 1px solid #333336;
            background-color: #262629;
            top: -1px; 
        }
        QTabBar::tab {
            background-color: #1C1C1E;
            border: 1px solid #333336;
            border-bottom: none;
            padding: 6px 14px;
            margin-right: 2px;
            color: #8E8E93;
            font-weight: 500; 
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        QTabBar::tab:selected {
            background-color: #262629;
            color: #FFFFFF;
            border-bottom: 1px solid #262629;
            border-top: 2px solid #3772FF; 
        }
        QTabBar::tab:hover:!selected {
            background-color: #212124;
            color: #C7C7CC;
        }

        /* --- Interactive Elements --- */
        QPushButton {
            background-color: #2E2E33;
            border: 1px solid #3A3A3F;
            border-radius: 4px;
            padding: 5px 12px;
            font-weight: 500;
            color: #E2E2E5;
        }
        QPushButton:hover {
            background-color: #3A3A40;
            border: 1px solid #4C4C52;
        }
        QPushButton:pressed {
            background-color: #1C1C1E;
            border: 1px solid #3772FF;
        }

        /* --- Critical Action Button (Simulation Engine Execution) --- */
        QPushButton#startEngineBtn {
            background-color: #0E6245; 
            color: #E6FFFA;
            border: 1px solid #107C57;
            font-size: 13px; 
            font-weight: 700; 
            letter-spacing: 1px;
            padding: 8px 18px;
            border-radius: 4px;
        }
        QPushButton#startEngineBtn:hover {
            background-color: #127A57; 
            border: 1px solid #14966B;
        }
        QPushButton#startEngineBtn:pressed {
            background-color: #0A4B35;
        }
        """

    def top_layout(self):
        layout = QGridLayout()
        
        heading = QLabel('<span style="color: #FF9800;">⬢</span> <span style="color: #FFFFFF;">HELIX</span><span style="color: #FF9800;">SIM</span>')
        heading.setObjectName("mainTitle")

        cam_layout = QFormLayout()
        cam_label = QLabel("Camera Mode")
        cam_combo = QComboBox()
        cam_combo.addItems(self.camera_modes)
        cam_combo.currentTextChanged.connect(self.data_manager.set_cam_mode)
        cam_layout.addRow(cam_label,cam_combo)

        start_btn = QPushButton()
        start_btn.setText("▶ START ENGINE")
        start_btn.setObjectName("startEngineBtn")
        start_btn.clicked.connect(self._on_start_btn)

        layout.addWidget(heading, 0, 0, 1, 5, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(cam_label, 0, 4, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(cam_combo, 0, 5, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(start_btn, 0, 6, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        return layout

    def middle_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.preset_group(), stretch=1)
        layout.addWidget(self.param_group(), stretch=3) 
        return layout

    def preset_group(self):
        layout = QVBoxLayout()
        group = QGroupBox("Presets")

        model_label = QLabel("Model")
        model_combo = QComboBox()
        model_combo.addItems(self.model_presets)
        model_combo.currentTextChanged.connect(self.data_manager.set_structural_preset)
        model_combo.currentTextChanged.connect(self._on_setting_change)

        trajectory_label = QLabel("Trajectory")
        trajectory_combo = QComboBox()
        trajectory_combo.addItems(self.trajectory_presets)
        trajectory_combo.currentTextChanged.connect(self.data_manager.set_trajectory_preset)
        trajectory_combo.currentTextChanged.connect(self._on_setting_change)

        self.traj_stacked_widget = QStackedWidget()
        self.traj_stacked_widget.addWidget(self.create_hover_config())
        self.traj_stacked_widget.addWidget(self.create_straight_line_config())
        self.traj_stacked_widget.addWidget(self.create_circular_loop_config())
        trajectory_combo.currentIndexChanged.connect(self.traj_stacked_widget.setCurrentIndex)

        layout.addWidget(model_label)
        layout.addWidget(model_combo)
        layout.addWidget(trajectory_label)
        layout.addWidget(trajectory_combo)
        layout.addWidget(self.traj_stacked_widget) 

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_hover_config(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        pos_group = QGroupBox()
        pos_layout = self.vector_spin_layout(
            suffix=" m", default_values=[0.0, 0.0, 5.0], decimals=2, steps=0.5,
            min_val=-10000, max_val=10000, colname=["X", "Y", "Z"], category="hover_param", metric_prefix="pos_"
        )
        pos_group.setLayout(pos_layout)

        yaw_spin = QDoubleSpinBox()
        yaw_spin.setRange(-360, 360)
        yaw_spin.setValue(0.0)
        yaw_spin.setSuffix(" °")
        yaw_spin.valueChanged.connect(partial(self._on_change,category="hover_param",metric="yaw"))
        
        layout.addRow("Position:",pos_group)
        layout.addRow("Yaw:", yaw_spin)
        return widget

    def create_straight_line_config(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        slope_group = QGroupBox()
        slope_layout = self.vector_spin_layout(
            suffix=" m", default_values=[0.0, 0.0, 5.0], decimals=2, steps=0.5,
            min_val=-10000, max_val=10000, colname=["X", "Y", "Z"], category="straight_param", metric_prefix="slope_"
        )
        slope_group.setLayout(slope_layout)

        intercept_group = QGroupBox()
        intercept_layout = self.vector_spin_layout(
            suffix=" m", default_values=[0.0, 0.0, 5.0], decimals=2, steps=0.5,
            min_val=-10000, max_val=10000, colname=["X", "Y", "Z"], category="straight_param", metric_prefix="intercept_"
        )
        intercept_group.setLayout(intercept_layout)

        yaw_spin = QDoubleSpinBox()
        yaw_spin.setRange(-360, 360)
        yaw_spin.setValue(0.0)
        yaw_spin.setSuffix(" °")
        yaw_spin.valueChanged.connect(partial(self._on_change,category="straight_param",metric="yaw"))

        layout.addRow("Slope:", slope_group)
        layout.addRow("Intercept:", intercept_group)
        layout.addRow("Yaw:", yaw_spin)
        return widget

    def create_circular_loop_config(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        radius_spin = QDoubleSpinBox()
        radius_spin.setRange(0.0, 1000.0)
        radius_spin.setValue(5.0)
        radius_spin.setSuffix(" m")
        radius_spin.valueChanged.connect(partial(self._on_change,category="circular_param",metric="radius"))
        
        height_spin = QDoubleSpinBox()
        height_spin.setRange(-1000.0, 1000.0)
        height_spin.setValue(5.0)
        height_spin.setSuffix(" m")
        height_spin.valueChanged.connect(partial(self._on_change,category="circular_param",metric="height"))
        
        yaw_spin = QDoubleSpinBox()
        yaw_spin.setRange(-360, 360)
        yaw_spin.setValue(0.0)
        yaw_spin.setSuffix(" °")
        yaw_spin.valueChanged.connect(partial(self._on_change,category="circular_param",metric="yaw"))
        
        layout.addRow("Radius:", radius_spin)
        layout.addRow("Height:", height_spin)
        layout.addRow("Yaw:", yaw_spin)
        return widget

    def param_group(self):
        layout = QVBoxLayout()
        group = QGroupBox("Adjustable Parameters")
        tab = QTabWidget()

        tab.addTab(self.struct_tab(), "Structural")
        tab.addTab(self.env_tab(), "Environmental")
        tab.addTab(self.control_tab(), "Control Limits")
        tab.addTab(self.pid_tab(), "PID Tuning") 

        layout.addWidget(tab)
        group.setLayout(layout)
        return group

    def struct_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        mass_spin = QDoubleSpinBox()
        mass_spin.setSuffix(" Kg")
        mass_spin.setValue(1.0)
        mass_spin.setDecimals(3)
        mass_spin.setSingleStep(0.1)
        mass_spin.setRange(0.0, 1000.0)
        mass_spin.valueChanged.connect(partial(self._on_change, category='struct_param', metric='mass'))

        arm_len_spin = QDoubleSpinBox()
        arm_len_spin.setSuffix(" m")
        arm_len_spin.setValue(0.5) 
        arm_len_spin.setDecimals(3)
        arm_len_spin.setSingleStep(0.05)
        arm_len_spin.setRange(0.0, 100.0)
        arm_len_spin.valueChanged.connect(partial(self._on_change, category='struct_param', metric='arm_length'))

        prop_len_spin = QDoubleSpinBox()
        prop_len_spin.setSuffix(" m") 
        prop_len_spin.setValue(0.25)
        prop_len_spin.setDecimals(3)
        prop_len_spin.setSingleStep(0.05)
        prop_len_spin.setRange(0.0, 1000.0)
        prop_len_spin.valueChanged.connect(partial(self._on_change, category='struct_param', metric='prop_length'))

        layout.addRow(QLabel("Mass:"), mass_spin)
        layout.addRow(QLabel("Arm Length:"), arm_len_spin)
        layout.addRow(QLabel("Propeller Length:"), prop_len_spin)
        return tab

    def env_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        wind_velo_group = QGroupBox()
        wind_velo_spin_layout = self.vector_spin_layout(
            suffix=" m/s", default_values=[0.0, 0.0, 0.0], decimals=2, steps=0.5,
            min_val=-10000, max_val=10000, colname=["X", "Y", "Z"], category="env_param", metric_prefix="wind_velocity_"
        )
        wind_velo_group.setLayout(wind_velo_spin_layout)

        turbulence_group = QGroupBox()
        turb_layout = QFormLayout()

        turb_intensity = QDoubleSpinBox()
        turb_intensity.setSuffix(" m/s")
        turb_intensity.setDecimals(2)
        turb_intensity.setSingleStep(0.5)
        turb_intensity.setRange(0.0, 50.0)
        turb_intensity.setValue(0.0) 
        turb_intensity.valueChanged.connect(partial(self._on_change, category='env_param', metric='turbulence_intensity'))

        gust_freq = QDoubleSpinBox()
        gust_freq.setSuffix(" Hz")
        gust_freq.setDecimals(2)
        gust_freq.setSingleStep(0.1)
        gust_freq.setRange(0.0, 20.0)
        gust_freq.setValue(0.0)
        gust_freq.valueChanged.connect(partial(self._on_change, category='env_param', metric='gust_frequency'))

        turb_layout.addRow("Turbulence Intensity:", turb_intensity)
        turb_layout.addRow("Gust Frequency:", gust_freq)
        turbulence_group.setLayout(turb_layout)

        gravity_spin = QDoubleSpinBox()
        gravity_spin.setSuffix(" m/s²")
        gravity_spin.setValue(9.81)
        gravity_spin.setDecimals(3)
        gravity_spin.setSingleStep(0.25)
        gravity_spin.setRange(0.0, 100.0)
        gravity_spin.valueChanged.connect(partial(self._on_change, category='env_param', metric='gravity'))

        atmos_pressure_spin = QDoubleSpinBox()
        atmos_pressure_spin.setSuffix(" N/m²")
        atmos_pressure_spin.setValue(1.0)
        atmos_pressure_spin.setDecimals(3)
        atmos_pressure_spin.setSingleStep(0.25)
        atmos_pressure_spin.setRange(0.0, 100.0)
        atmos_pressure_spin.valueChanged.connect(partial(self._on_change, category='env_param', metric='atmospheric_pressure'))

        layout.addRow(QLabel("Wind Velocity:"), wind_velo_group)
        layout.addRow(QLabel("Turbulence & Gusts:"), turbulence_group)
        layout.addRow(QLabel("Gravity:"), gravity_spin)
        layout.addRow(QLabel("Atmospheric Pressure:"), atmos_pressure_spin)

        return tab

    def control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        rpm_group = QGroupBox("Motor RPM Settings")
        rpm_layout = QFormLayout()

        def create_limit_spin(val, max_val, metric):
            spin = QDoubleSpinBox()
            spin.setRange(0, max_val)
            spin.setDecimals(0)
            spin.setSingleStep(50)
            spin.setValue(val)
            spin.valueChanged.connect(partial(self._on_change, category='control_param', metric=metric))
            return spin
        
        rpm_layout.addRow("Base RPM:", create_limit_spin(3813, 20000, "base_rpm"))
        rpm_layout.addRow("Min RPM:", create_limit_spin(1500, 20000, "min_rpm"))
        rpm_layout.addRow("Max RPM:", create_limit_spin(6500, 20000, "max_rpm"))
        rpm_layout.addRow("Windup Limit:", create_limit_spin(500, 5000, "windup_limit"))
        rpm_group.setLayout(rpm_layout)

        sys_group = QGroupBox("System Latency & Noise")
        sys_layout = QFormLayout()

        esc_latency_spin = QDoubleSpinBox()
        esc_latency_spin.setSuffix(" ms")
        esc_latency_spin.setDecimals(1)
        esc_latency_spin.setSingleStep(1.0)
        esc_latency_spin.setRange(0.0, 100.0)
        esc_latency_spin.setValue(0.0) 
        esc_latency_spin.valueChanged.connect(partial(self._on_change, category='control_param', metric='esc_latency'))

        imu_sensor_noise_spin = QDoubleSpinBox()
        imu_sensor_noise_spin.setSuffix(" σ") 
        imu_sensor_noise_spin.setDecimals(3)
        imu_sensor_noise_spin.setSingleStep(0.05)
        imu_sensor_noise_spin.setRange(0.0, 10.0)
        imu_sensor_noise_spin.setValue(0.0) 
        imu_sensor_noise_spin.valueChanged.connect(partial(self._on_change, category='control_param', metric='imu_sensor_noise'))

        sys_layout.addRow("ESC Latency:", esc_latency_spin)
        sys_layout.addRow("IMU Sensor Noise:", imu_sensor_noise_spin)
        sys_group.setLayout(sys_layout)

        layout.addWidget(rpm_group)
        layout.addWidget(sys_group)
        layout.addStretch()

        return tab

    def pid_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)

        thrust_group = QGroupBox("Thrust PID")
        thrust_layout = QVBoxLayout()
        thrust_layout.addWidget(QLabel("Position (Z):"))
        thrust_layout.addLayout(self.vector_spin_layout("", [1.5, 0.0, 0.0], 2, 0.1, 0, 2000, ["Kp", "Ki", "Kd"], "thrust_pid_param", "pos_"))
        thrust_layout.addWidget(QLabel("Velocity (Z):"))
        thrust_layout.addLayout(self.vector_spin_layout("", [400.0, 10.0, 50.0], 1, 5.0, 0, 2000, ["Kp", "Ki", "Kd"], "thrust_pid_param", "velo_"))
        thrust_group.setLayout(thrust_layout)

        roll_group = QGroupBox("Roll PID")
        roll_layout = QVBoxLayout()
        roll_layout.addWidget(QLabel("Position (Y):"))
        roll_layout.addLayout(self.vector_spin_layout("", [0.15, 0.0, 0.15], 2, 0.05, 0, 2000, ["Kp", "Ki", "Kd"], "roll_pid_param", "pos_"))
        roll_layout.addWidget(QLabel("Angle (Roll):"))
        roll_layout.addLayout(self.vector_spin_layout("", [800.0, 5.0, 350.0], 1, 5.0, 0, 2000, ["Kp", "Ki", "Kd"], "roll_pid_param", "angle_"))
        roll_group.setLayout(roll_layout)

        pitch_group = QGroupBox("Pitch PID")
        pitch_layout = QVBoxLayout()
        pitch_layout.addWidget(QLabel("Position (X):"))
        pitch_layout.addLayout(self.vector_spin_layout("", [0.15, 0.0, 0.15], 2, 0.05, 0, 2000, ["Kp", "Ki", "Kd"], "pitch_pid_param", "pos_"))
        pitch_layout.addWidget(QLabel("Angle (Pitch):"))
        pitch_layout.addLayout(self.vector_spin_layout("", [800.0, 5.0, 350.0], 1, 5.0, 0, 2000, ["Kp", "Ki", "Kd"], "pitch_pid_param", "angle_"))
        pitch_group.setLayout(pitch_layout)

        yaw_group = QGroupBox("Yaw PID")
        yaw_layout = QVBoxLayout()
        yaw_layout.addWidget(QLabel("Angle (Yaw):"))
        yaw_layout.addLayout(self.vector_spin_layout("", [1500.0, 10.0, 200.0], 1, 5.0, 0, 3000, ["Kp", "Ki", "Kd"], "yaw_pid_param", "angle_"))
        yaw_layout.addStretch() 
        yaw_group.setLayout(yaw_layout)

        layout.addWidget(thrust_group, 0, 0)
        layout.addWidget(roll_group, 0, 1)
        layout.addWidget(pitch_group, 1, 0)
        layout.addWidget(yaw_group, 1, 1)

        return tab

    def vector_spin_layout(self, suffix, default_values, decimals, steps, min_val, max_val, colname, category, metric_prefix):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        for i, col in enumerate(colname):
            layout = QFormLayout()
            spin = QDoubleSpinBox()
            spin.setSuffix(suffix)
            spin.setDecimals(decimals)
            spin.setSingleStep(steps)
            spin.setRange(min_val, max_val)
            spin.setValue(default_values[i])
            spin.valueChanged.connect(partial(self._on_change, category=category, metric=f"{metric_prefix}{col.lower()}"))

            layout.addRow(col, spin)
            main_layout.addLayout(layout)

        return main_layout

    def bottom_layout(self):
        self.telemetry = TelemetryChart()
        return self.telemetry
    
    def _on_start_btn(self):
        btn = self.sender()
        if self.data_manager.data.run_sim == 0:
            self.data_manager.data.run_sim = 1
            btn.setText("⏹ STOP ENGINE")
            btn.setStyleSheet("background-color: #8B0000; color: white; border: 1px solid #AA0000;") 
        else:
            self.data_manager.data.run_sim = 0
            btn.setText("▶ START ENGINE")
            btn.setStyleSheet("")

    def _on_setting_change(self):
        self.data_manager.data.setting_change = 1
        print("Setting Changed:", self.data_manager.data.setting_change)

    def _on_change(self, change, category, metric):
        if category == "_g":
            target_attr = self.data_manager.data
        else:
            target_attr = getattr(self.data_manager.data, category)

        with self.data_manager.get_lock():
            setattr(target_attr, metric, change)
        
        self._on_setting_change()
        print(f"[CHANGE] {metric} = {getattr(getattr(self.data_manager.data,category),metric)}")
