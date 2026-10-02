import sys
from PySide6.QtWidgets import QLineEdit, QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

class MainWindow(QWidget):
     my_signal = Signal(int)

     def __init__(self):
          super().__init__()
          self.my_signal.connect(self.printer)

          self.button = QPushButton("Emmit Signal")
          self.button.clicked.connect(self.emit_signal)

          
          layout = QVBoxLayout()
          layout.addWidget(self.button)

          self.setLayout(layout)

     
     def emit_signal(self):
          self.my_signal.emit(50)
     
     def printer(self, number):
          print(f"the number: {number}")



app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())