from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt

class GradientCalculatorDialog(QDialog):
    def __init__(self, waypoints, parent=None):
        """
        waypoints: List of tuples [(lat, lon), ...]
        """
        super().__init__(parent)
        self.setWindowTitle("Gradient Calculator")
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)  # Pencere boyutunu sabitle
        self.waypoints = waypoints
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(7)  # Daha kompakt görünüm için aralığı daha da azalt
        layout.setContentsMargins(10, 10, 10, 10)  # Kenarlıkları küçült

        # İlk Waypoint seçimi (alt alta)
        first_wp_layout = QHBoxLayout()
        first_wp_layout.addWidget(QLabel("İlk Waypoint:"), 0)
        self.start_combo = QComboBox()
        self.start_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        if self.waypoints:
            self.start_combo.addItems([f"WP{i+1}" for i in range(len(self.waypoints))])
        self.start_combo.currentIndexChanged.connect(self.on_waypoint_selection_changed)  # Otomatik güncelleme
        first_wp_layout.addWidget(self.start_combo, 1)
        layout.addLayout(first_wp_layout)

        # Son Waypoint seçimi (alt alta)
        last_wp_layout = QHBoxLayout()
        last_wp_layout.addWidget(QLabel("Son Waypoint:"), 0)
        self.end_combo = QComboBox()
        self.end_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        if self.waypoints:
            self.end_combo.addItems([f"WP{i+1}" for i in range(len(self.waypoints))])
            if len(self.waypoints) > 1:
                self.end_combo.setCurrentIndex(len(self.waypoints)-1)
        self.end_combo.currentIndexChanged.connect(self.on_waypoint_selection_changed)  # Otomatik güncelleme
        last_wp_layout.addWidget(self.end_combo, 1)
        layout.addLayout(last_wp_layout)

        # Initial altitude
        alt_layout = QHBoxLayout()
        alt_layout.addWidget(QLabel("Başlangıç İrtifası:"), 0)
        self.altitude_edit = QLineEdit()
        self.altitude_edit.setPlaceholderText("ft")
        self.altitude_edit.setText("30000")  # Varsayılan değer: 30000 ft
        self.altitude_edit.setMaximumWidth(100)  # Genişliği sınırla
        self.altitude_edit.textChanged.connect(self.on_input_changed)  # Otomatik güncelleme
        alt_layout.addWidget(self.altitude_edit, 1)
        layout.addLayout(alt_layout)

        # Gradient input (% olarak sabit)
        grad_layout = QHBoxLayout()
        grad_layout.addWidget(QLabel("Alçalma Oranı (%):"), 0)
        self.gradient_spin = QDoubleSpinBox()
        self.gradient_spin.setRange(0.1, 10.0)
        self.gradient_spin.setSingleStep(0.1)
        self.gradient_spin.setValue(3.0)
        self.gradient_spin.setMaximumWidth(80)  # Genişliği sınırla
        self.gradient_spin.valueChanged.connect(self.on_input_changed)  # Otomatik güncelleme
        grad_layout.addWidget(self.gradient_spin, 1)
        # Birim seçenekleri kaldırıldı, sadece % kullanılacak
        self.gradient_unit_combo = QComboBox()  # Geriye dönük uyumluluk için gizli olarak tutalım
        self.gradient_unit_combo.addItems(["% (yüzde)", "ft/NM"])
        self.gradient_unit_combo.hide()  # Arayüzden gizle
        layout.addLayout(grad_layout)

        # İrtifa birimi kaldırıldı, her zaman ft kullanılacak
        self.alt_unit_combo = QComboBox()  # Geriye dönük uyumluluk için gizli olarak tutalım
        self.alt_unit_combo.addItems(["ft", "m"])
        self.alt_unit_combo.hide()  # Arayüzden gizle

        # Calculate button
        self.calc_btn = QPushButton("Hesapla")
        self.calc_btn.clicked.connect(self.calculate_gradient)
        self.calc_btn.setMaximumWidth(120)  # Buton genişliğini sınırla
        calc_btn_layout = QHBoxLayout()
        calc_btn_layout.addStretch()
        calc_btn_layout.addWidget(self.calc_btn)
        calc_btn_layout.addStretch()
        layout.addLayout(calc_btn_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Waypoint", "Mesafe (NM)", "İrtifa"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Tabloyu kompakt hale getir
        self.results_table.verticalHeader().setVisible(False)  # Satır başlıklarını gizle
        self.results_table.setAlternatingRowColors(True)  # Alternatif satır renkleri
        self.results_table.setMinimumHeight(150)  # Minimum yükseklik
        self.results_table.setMaximumHeight(200)  # Maksimum yükseklik
        self.results_table.horizontalHeader().setMinimumSectionSize(50)  # Minimum sütun genişliği
        self.results_table.horizontalHeader().setDefaultSectionSize(80)  # Varsayılan sütun genişliği
        self.results_table.verticalHeader().setDefaultSectionSize(20)  # Varsayılan satır yüksekliği (daha kompakt)
        layout.addWidget(self.results_table)
        
        # Pencere boyutunu sınırla ve daha kompakt hale getir
        self.setMinimumWidth(350)
        self.setMaximumWidth(380)
        self.setFixedSize(280, 300)  # Sabit boyut
        
        # Yeterli waypoint yoksa butonları devre dışı bırak
        self.update_ui_state()

    def calculate_gradient(self):
        try:
            # En az iki waypoint olmalı
            if len(self.waypoints) < 2:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Yetersiz Waypoint", "Gradient hesaplayabilmek için en az 2 waypoint gerekli.")
                return
                
            start_idx = self.start_combo.currentIndex()
            end_idx = self.end_combo.currentIndex()
            if start_idx == end_idx:
                raise ValueError("İlk ve son waypoint farklı olmalı.")
            if start_idx > end_idx:
                indices = list(range(start_idx, end_idx-1, -1))
            else:
                indices = list(range(start_idx, end_idx+1))
            
            # Başlangıç yüksekliği boşsa hata ver
            if not self.altitude_edit.text():
                raise ValueError("Lütfen başlangıç irtifasını girin.")

            initial_alt = float(self.altitude_edit.text())
            grad_val = self.gradient_spin.value()
            # grad_unit artık kullanılmıyor, her zaman % olarak işlem yapılacak
            alt_unit = "ft"  # Sabit ft birimi

            # Mesafeleri hesapla
            from utils import calculate_distance
            points = [self.waypoints[i] for i in indices]
            segment_distances = []
            for i in range(len(points)-1):
                d = calculate_distance(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
                segment_distances.append(d)
            cum_distances = [0]
            for d in segment_distances:
                cum_distances.append(cum_distances[-1] + d)

            # % değeri doğrudan ft/NM'e çevir
            grad_ft_per_nm = grad_val * 100  # 1% = 100 ft/NM

            # Her waypoint için irtifa hesapla
            altitudes = []
            for dist in cum_distances:
                alt = initial_alt - grad_ft_per_nm * dist
                altitudes.append(alt)

            # Sonuçları tabloya yaz
            self.results_table.setRowCount(len(indices))
            for i, idx in enumerate(indices):
                self.results_table.setItem(i, 0, QTableWidgetItem(f"WP{idx+1}"))
                self.results_table.setItem(i, 1, QTableWidgetItem(f"{cum_distances[i]:.2f}"))
                self.results_table.setItem(i, 2, QTableWidgetItem(f"{altitudes[i]:.0f} ft"))
            
            # Otomatik olarak son satıra kaydır
            if len(indices) > 0:
                # Son satır ve sütunu seç
                last_row = len(indices) - 1
                self.results_table.scrollToItem(self.results_table.item(last_row, 0))
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Hata", str(e))

    def set_waypoints(self, waypoints):
        """Waypoint listesini güncelle ve UI'yi yenile"""
        self.waypoints = waypoints
        # ComboBox'ları güncelle
        self.start_combo.clear()
        self.end_combo.clear()
        if self.waypoints:
            self.start_combo.addItems([f"WP{i+1}" for i in range(len(self.waypoints))])
            self.end_combo.addItems([f"WP{i+1}" for i in range(len(self.waypoints))])
            if len(self.waypoints) > 1:
                self.end_combo.setCurrentIndex(len(self.waypoints)-1)
        # Sonuç tablosunu temizle
        self.results_table.setRowCount(0)
        
        # UI durumunu güncelle
        self.update_ui_state()
        
        # Yeterli waypoint varsa otomatik hesapla
        if len(self.waypoints) >= 2 and self.altitude_edit.text():
            self.calculate_gradient()

    def update_ui_state(self):
        if len(self.waypoints) < 2:
            self.calc_btn.setEnabled(False)
        else:
            self.calc_btn.setEnabled(True)
            
    def on_waypoint_selection_changed(self):
        """Waypoint seçimi değiştiğinde otomatik olarak hesapla"""
        # İki kombo da değer içeriyorsa ve farklı değerler seçiliyse hesapla
        if self.start_combo.count() > 0 and self.end_combo.count() > 0:
            if self.start_combo.currentIndex() != self.end_combo.currentIndex() and self.altitude_edit.text():
                self.calculate_gradient()
                
    def on_input_changed(self):
        """İrtifa veya alçalma oranı değiştiğinde otomatik olarak hesapla"""
        # Gerekli koşullar sağlanıyorsa hesapla
        if (len(self.waypoints) >= 2 and 
            self.start_combo.currentIndex() != self.end_combo.currentIndex() and 
            self.altitude_edit.text()):
            try:
                # Sayısal bir değer girildiğinden emin ol
                float(self.altitude_edit.text())
                self.calculate_gradient()
            except ValueError:
                # Sayısal olmayan bir değer girilirse hesaplama yapma
                pass 