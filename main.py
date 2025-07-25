import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from airspace_visualizer import AirspaceVisualizer

if __name__ == "__main__":
    # Geliştirme sırasında hataları daha net görmek için
    print("=== Uygulama Başlatılıyor ===")
    
    app = QApplication(sys.argv)
    window = AirspaceVisualizer()
    
    # Debug mesajı
    print("AirspaceVisualizer yüklendi")

    window.show()
    sys.exit(app.exec_())