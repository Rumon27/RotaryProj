import sys 
from PySide6.QtWidgets import (
     QApplication,
     QWidget,
     QLabel,
     QLineEdit,
     QVBoxLayout,
     QPushButton
)


class MainWindow(QWidget):
     def __init__(self):
          super().__init__()
          
          str = ""
          
          self.label = QLabel("Name will appear here")
          
          self.input = QLineEdit()
          self.input.setPlaceholderText("Enter Name")
          self.input.textChanged.connect(self.text_changed)
          
          self.button = QPushButton("Enter")
          self.button.clicked.connect(self.button_clicked)
          
          layout = QVBoxLayout()

          layout.addWidget(self.label)
          layout.addWidget(self.input)
          layout.addWidget(self.button)

          self.setLayout(layout)
          
          

     def text_changed(self, text):
          self.str = text 
          
     def button_clicked(self):
          self.label.setText(f"{self.str}")



app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())