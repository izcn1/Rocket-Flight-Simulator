import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class RocketSimulatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        self.m_rocket_edit = QLineEdit(self)
        self.thrust_force_edit = QLineEdit(self)
        self.S_edit = QLineEdit(self)
        self.Cd_edit = QLineEdit(self)
        self.duration_edit = QLineEdit(self)

        self.m_rocket_label = QLabel('Kütle (kg):', self)
        self.thrust_force_label = QLabel('Motorun Maximum İtkisi (N):', self)
        self.S_label = QLabel('S (m^2):', self)
        self.Cd_label = QLabel('Cd:', self)
        self.duration_label = QLabel('Simülasyon Süresi (s):', self)

        self.dof_combobox = QComboBox(self)
        self.dof_combobox.addItem("1-DOF")
        self.dof_combobox.addItem("2-DOF")

        self.start_button = QPushButton('Simülasyonu Başlat', self)
        self.start_button.clicked.connect(self.run_simulation)

        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, sharex=True)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.m_rocket_label)
        layout.addWidget(self.m_rocket_edit)
        layout.addWidget(self.thrust_force_label)
        layout.addWidget(self.thrust_force_edit)
        layout.addWidget(self.S_label)
        layout.addWidget(self.S_edit)
        layout.addWidget(self.Cd_label)
        layout.addWidget(self.Cd_edit)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_edit)
        layout.addWidget(QLabel('DOF Seç:', self))
        layout.addWidget(self.dof_combobox)
        layout.addWidget(self.start_button)



        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.setWindowTitle('Roket Uçuş Simülasyonu')
        self.setGeometry(100, 100, 800, 600)

    def run_simulation(self):
        m_rocket = float(self.m_rocket_edit.text())
        thrust_force = float(self.thrust_force_edit.text())
        S = float(self.S_edit.text())
        Cd = float(self.Cd_edit.text())
        simulation_duration = float(self.duration_edit.text())
        selected_dof = self.dof_combobox.currentText()

        if selected_dof == "1-DOF":
            self.ax2.clear()

            time, height = rocket_simulation_1dof(simulation_duration, 0.1, m_rocket, thrust_force, S, Cd)
            self.plot_graph(time, height, 'Roket Simülasyonu - 1DOF', '', 'Yükseklik (m)')

        elif selected_dof == "2-DOF":
            self.ax2.clear()
            time, height, velocity = rocket_simulation_2dof(simulation_duration, 0.1, m_rocket, thrust_force, S, Cd)
            self.plot_graph(time, height, 'Roket Simülasyonu - 2DOF', '', 'Yükseklik (m)')
            self.plot_graph(time, velocity, 'Roket Simülasyonu - 2DOF', 'Zaman (s)', 'Hız (m/s)')

    def plot_graph(self, x, y, title, xlabel, ylabel):
        if "Hız" in ylabel:
            self.ax2.clear()
            self.ax2.plot(x, y)
            self.ax2.set_title(title)
            self.ax2.set_xlabel(xlabel)
            self.ax2.set_ylabel(ylabel)
            self.ax2.grid(True)
        else:
            self.ax1.clear()
            self.ax1.plot(x, y)
            self.ax1.set_title(title)
            self.ax1.set_xlabel(xlabel)
            self.ax1.set_ylabel(ylabel)
            self.ax1.grid(True)

        self.canvas.draw()


def rocket_simulation_1dof(duration, time_step, m_rocket, thrust_force, S, Cd):
    g = 9.81
    thrust_duration = 4
    ro = 1.225
    time_points = np.arange(0, duration, time_step)
    height_points = []

    for t in time_points:
        if t < thrust_duration:
            thrust = thrust_force
        else:
            thrust = 0

        air_speed = 0 if not height_points else height_points[-1] / t
        drag_force = 0.5 * ro * (air_speed ** 2) * S * Cd
        net_force = thrust - m_rocket * g - drag_force

        acceleration = net_force / m_rocket
        velocity = acceleration * time_step
        displacement = velocity * time_step * 100

        if len(height_points) == 0:
            height_points.append(displacement)
        else:
            height_points.append(height_points[-1] + displacement)

        if height_points[-1] < 0:
            height_points[-1] = 0

    return time_points, height_points


def rocket_simulation_2dof(duration, time_step, m_rocket, thrust_force, S, Cd):
    g = 9.81
    thrust_duration = 4

    time_points = np.arange(0, duration, time_step)
    height_points = []
    velocity_points = []

    for t in time_points:
        if t < thrust_duration:
            thrust = thrust_force
        else:
            thrust = 0

        ro = 1.225
        air_speed = 0 if not height_points else height_points[-1] / t
        drag_force = 0.5 * ro * (air_speed ** 2) * S * Cd
        net_force = thrust - m_rocket * g - drag_force

        acceleration = net_force / m_rocket

        velocity = velocity_points[-1] if velocity_points else 0
        velocity += acceleration * time_step
        displacement = velocity * time_step

        if len(height_points) == 0:
            height_points.append(displacement)
        else:
            height_points.append(height_points[-1] + displacement)

        if height_points[-1] < 0:
            height_points[-1] = 0

        velocity_points.append(velocity)

    return time_points, height_points, velocity_points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RocketSimulatorApp()
    window.show()
    sys.exit(app.exec_())
