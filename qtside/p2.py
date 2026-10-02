import sys
from PySide6.QtWidgets import QLineEdit, QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("My first app")

main_layout = QVBoxLayout()

row1 = QHBoxLayout()
row1.addWidget(QLabel("Name: "))
row1.addWidget(QLineEdit())

row2 = QHBoxLayout()
row2.addWidget(QLabel("Age: "))
row2.addWidget(QLineEdit())

main_layout.addLayout(row1)
main_layout.addLayout(row2)

window.setLayout(main_layout)
window.show()

sys.exit(app.exec())

