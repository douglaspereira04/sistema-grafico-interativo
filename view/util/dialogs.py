from PyQt5.QtWidgets import QMessageBox, QInputDialog

def show_error_box(message):
    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)

    box.setText(message)
    box.setWindowTitle("Error")

    box.exec_()

def show_warning_box(message):
    box = QMessageBox()
    box.setIcon(QMessageBox.Warning)

    box.setText(message)
    box.setWindowTitle("Warning")

    box.exec_()

def show_input_box(message):
    return QInputDialog.getText(None, 'Input', message)