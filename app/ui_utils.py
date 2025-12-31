# app/ui_utils.py
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox

class NumericTableWidgetItem(QTableWidgetItem):
    """
    A custom QTableWidgetItem that allows for correct numerical sorting in a table.
    """
    def __lt__(self, other):
        try:
            # Attempt to compare items as floats for sorting
            return float(self.text()) < float(other.text())
        except (ValueError, TypeError):
            # Fallback to default string comparison if conversion fails
            return super().__lt__(other)

def show_error_message(parent, message):
    """
    Displays a standardized error message box.
    """
    QMessageBox.critical(parent, "Erro", message)
