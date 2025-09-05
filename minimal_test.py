from PyQt5.QtWidgets import QApplication, QLabel
import sys

print("Minimal PyQt5 test...", flush=True)
app = QApplication(sys.argv)
label = QLabel("Hello, PyQt5!")
label.show()
sys.exit(app.exec_())