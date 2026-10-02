import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QSlider
from PySide6.QtCore import Qt 


class MainWindow(QWidget):
     def __init__(self):
          super().__init__()
 
          self.label = QLabel("Value: 0")
 
          self.slider = QSlider(Qt.Orientation.Horizontal)
          self.slider.setRange(0, 100)
          self.slider.valueChanged.connect(self.slider_changed)

          self.button = QPushButton("Click Me")
          self.button.clicked.connect(self.button_clicked)
          
          layout = QVBoxLayout()
          layout.addWidget(self.label)
          layout.addWidget(self.slider)
          layout.addWidget(self.button)
          
          self.setLayout(layout)       
  

     def slider_changed(self, value):
          self.label.setText(f"value: {value}")

     def button_clicked(self):
          self.label.setText


app = QApplication(sys.argv)

window = MainWindow()

window.show()

sys.exit(app.exec())
