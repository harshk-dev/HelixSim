from PyQt6.QtWidgets import QWidget, QHBoxLayout
import pyqtgraph as pg
import numpy as np
from collections import deque
import time

class TelemetryChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        self.max_points = 1500
        self.start_time = time.time()

        self.time_buffer = deque(maxlen=self.max_points)
        self.alt_buffer = deque(maxlen=self.max_points)
        
        self.rpm_buffers = [deque(maxlen=self.max_points) for _ in range(4)]

        layout.addWidget(self.init_rpm_graph())
        layout.addWidget(self.init_altitude_graph())

    def init_rpm_graph(self):
        self.rpm_widget = pg.PlotWidget(title="Motor Outputs (RPM)")
        self.rpm_widget.setBackground('#262629')
        self.rpm_widget.showGrid(x=True, y=True, alpha=0.15)
        self.rpm_widget.addLegend(offset=(10, 10), labelTextColor="#D4D4D4")
        
        colors = [(55, 114, 255), (16, 124, 87), (230, 81, 0), (255, 152, 0)]
        labels = ['Front Left', 'Front Right', 'Back Left', 'Back Right']
        
        self.rpm_curves = []
        for i in range(4):
            pen = pg.mkPen(color=colors[i], width=2)
            curve = self.rpm_widget.plot(pen=pen, name=labels[i])
            self.rpm_curves.append(curve)
            
        self.rpm_widget.setLabel('bottom', 'Time', units='s', **{'color': '#A5A5AA'})
        self.rpm_widget.setLabel('left', 'Velocity', units='RPM', **{'color': '#A5A5AA'})
        return self.rpm_widget

    def init_altitude_graph(self):
        self.alt_widget = pg.PlotWidget(title="Z-Axis Telemetry (Altitude)")
        self.alt_widget.setBackground('#262629')
        self.alt_widget.showGrid(x=True, y=True, alpha=0.15)
        
        pen = pg.mkPen(color=(226, 226, 229), width=2)
        self.alt_curve = self.alt_widget.plot(pen=pen)
        
        self.alt_widget.setLabel('bottom', 'Time', units='s', **{'color': '#A5A5AA'})
        self.alt_widget.setLabel('left', 'Height', units='m', **{'color': '#A5A5AA'})
        return self.alt_widget

    def update_telemetry(self, current_alt: float, current_rpms: np.ndarray):
        current_time = time.time() - self.start_time
        
        try:
            scalar_alt = float(np.asarray(current_alt).item())
            if np.isnan(scalar_alt) or np.isinf(scalar_alt): 
                scalar_alt = 0.0
        except (ValueError, TypeError):
            scalar_alt = 0.0

        flat_rpms = np.asarray(current_rpms).flatten()
        
        self.time_buffer.append(current_time)
        self.alt_buffer.append(scalar_alt)
        
        for i in range(4):
            val = 0.0
            if i < len(flat_rpms):
                try:
                    val = float(flat_rpms[i].item())
                    if np.isnan(val) or np.isinf(val):
                        val = 0.0
                except (ValueError, TypeError):
                    pass
            self.rpm_buffers[i].append(val)

        times_array = np.array(self.time_buffer, dtype=float)
        self.alt_curve.setData(times_array, np.array(self.alt_buffer, dtype=float))
        
        for i in range(4):
            self.rpm_curves[i].setData(times_array, np.array(self.rpm_buffers[i], dtype=float))