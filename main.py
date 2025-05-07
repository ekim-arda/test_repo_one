import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from airspace_visualizer import AirspaceVisualizer
import math

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AirspaceVisualizer()
    window.show()
    sys.exit(app.exec_())
