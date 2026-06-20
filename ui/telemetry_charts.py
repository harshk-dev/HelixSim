from PyQt6.QtWidgets import QWidget, QHBoxLayout
import pyqtgraph as pg

'''
# ==========================================
        # 3. BOTTOM SECTION (GRAPHS)
        # ==========================================
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(15)

        # RPM Graph
        self.graph_rpm = pg.PlotWidget(title="RPM")
        self.graph_rpm.setBackground('#1e293b')
        self.graph_rpm.showGrid(x=True, y=True, alpha=0.3)
        self.curve_rpm = self.graph_rpm.plot(pen=pg.mkPen('#10b981', width=2)) # Green line
        
        # Altitude Graph
        self.graph_alt = pg.PlotWidget(title="Altitude")
        self.graph_alt.setBackground('#1e293b')
        self.graph_alt.showGrid(x=True, y=True, alpha=0.3)
        self.curve_alt = self.graph_alt.plot(pen=pg.mkPen('#6366f1', width=2)) # Purple line

        graphs_layout.addWidget(self.graph_rpm)
        graphs_layout.addWidget(self.graph_alt)
        
        main_layout.addLayout(graphs_layout, stretch=3) # Graphs get more vertical space
'''

class TelemetryChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(self.rpm_graph())
        layout.addWidget(self.altitude_graph())

    def rpm_graph(self):
        graph = pg.PlotWidget(title="RPM")
        return graph

    def altitude_graph(self):
        graph = pg.PlotWidget(title="Altitude")
        return graph