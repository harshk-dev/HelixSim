from PyQt6.QtWidgets import QWidget, QHBoxLayout
import pyqtgraph as pg

'''
# ==========================================
        # 3. BOTTOM SECTION (GRAPHS)
        # ==========================================
        from PyQt6.QtWidgets import QWidget, QHBoxLayout
import pyqtgraph as pg

class TelemetryChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Remove margins so it aligns perfectly with the layout stretches in the main window
        layout.setContentsMargins(0, 0, 0, 0) 

        # Create the RPM graph with the Amber accent color
        self.graph_rpm, self.curve_rpm = self.create_styled_graph(
            title="Motor RPM", 
            line_color="#FF9800",  # Industrial Amber
            y_label="RPM"
        )
        
        # Create the Altitude graph with a contrasting Cyan color
        self.graph_alt, self.curve_alt = self.create_styled_graph(
            title="Altitude (Z-Axis)", 
            line_color="#00E5FF",  # High-visibility Cyan
            y_label="Meters"
        )

        layout.addWidget(self.graph_rpm)
        layout.addWidget(self.graph_alt)

    def create_styled_graph(self, title, line_color, y_label):
        """Helper method to generate perfectly themed graphs."""
        graph = pg.PlotWidget()
        
        # 1. Background & Grid
        graph.setBackground('#1A1A1A') # Matches the QGroupBox background
        graph.showGrid(x=True, y=True, alpha=0.15) # Subtle grid lines
        
        # 2. Title Styling
        graph.setTitle(title, color='#FF9800', size='12pt', bold=True)
        
        # 3. Axis Labels
        label_styles = {"color": "#AAAAAA", "font-size": "12px", "font-weight": "bold"}
        graph.setLabel("left", y_label, **label_styles)
        graph.setLabel("bottom", "Time (s)", **label_styles)
        
        # 4. Axis Lines and Tick Text Styling
        for axis_name in ['left', 'bottom']:
            axis = graph.getAxis(axis_name)
            axis.setPen(pg.mkPen(color='#3A3A3A', width=2))   # The physical axis line
            axis.setTextPen(pg.mkPen(color='#777777'))        # The numbers on the axis
        
        # 5. Create the data curve (the line itself)
        # Using a slightly thicker width for high visibility on dark backgrounds
        pen = pg.mkPen(color=line_color, width=2)
        curve = graph.plot([], [], pen=pen)
        
        return graph, curve

    # --- Methods to update the data from your physics engine ---
    
    def update_rpm(self, time_data, rpm_data):
        """Pass arrays of time and RPM data to update the line."""
        self.curve_rpm.setData(time_data, rpm_data)

    def update_altitude(self, time_data, alt_data):
        """Pass arrays of time and Altitude data to update the line."""
        self.curve_alt.setData(time_data, alt_data)
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