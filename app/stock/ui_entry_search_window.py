# app/stock/ui_entry_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from app.services.stock_service import StockService

class EntrySearchWindow(QWidget):
    entry_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.stock_service = StockService()
        self.edit_window = None

        self.setWindowTitle("Pesquisa de Entradas de Insumo")
        self.setGeometry(150, 150, 800, 600)

        self.main_layout = QVBoxLayout(self)
        self.create_search_group()
        self.create_results_group()
        self.load_entries()

    def create_search_group(self):
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()

        self.search_field_combo = QComboBox()
        self.search_field_combo.addItems(["ID", "Fornecedor", "Nº Nota", "Status"])

        self.search_text = QLineEdit()
        self.search_text.returnPressed.connect(self.load_entries)

        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.load_entries)

        new_button = QPushButton("Nova Entrada")
        new_button.clicked.connect(self.open_new_entry_window)

        search_layout.addWidget(self.search_field_combo)
        search_layout.addWidget(self.search_text, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_button)
        search_group.setLayout(search_layout)

        self.main_layout.addWidget(search_group)

    def create_results_group(self):
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()

        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Data Entrada", "Fornecedor", "Nº Nota", "Valor Total", "Status"])
        self.table_view.setModel(self.table_model)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setStyleSheet("QTableView::item:selected { background-color: #D3D3D3; color: black; }")
        self.table_view.doubleClicked.connect(self.handle_double_click)

        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group)

    def load_entries(self):
        search_type_text = self.search_field_combo.currentText()
        search_content = self.search_text.text()
        self.table_model.removeRows(0, self.table_model.rowCount())

        response = self.stock_service.list_entries(search_content, search_type_text)

        if not response["success"]:
            print(f"UI Error: {response['message']}")
            return

        for entry in response["data"]:
            row = [
                QStandardItem(str(entry['ID'])),
                QStandardItem(entry['DATA_ENTRADA']),
                QStandardItem(entry['FORNECEDOR']),
                QStandardItem(entry['NUMERO_NOTA']),
                QStandardItem(f"{entry['VALOR_TOTAL']:.2f}" if entry['VALOR_TOTAL'] else "0.00"),
                QStandardItem(entry['STATUS'])
            ]
            self.table_model.appendRow(row)

    def handle_double_click(self, model_index):
        entry_id = int(self.table_model.item(model_index.row(), 0).text())
        self.show_edit_window(entry_id)

    def open_new_entry_window(self):
        self.show_edit_window(entry_id=None)

    def show_edit_window(self, entry_id):
        from app.stock.ui_entry_edit_window import EntryEditWindow
        if self.edit_window is None:
            self.edit_window = EntryEditWindow(entry_id=entry_id, parent=self)
            self.edit_window.destroyed.connect(self.on_edit_window_closed)
            self.edit_window.show()
        else:
            self.edit_window.activateWindow()
            self.edit_window.raise_()

    def on_edit_window_closed(self):
        self.edit_window = None
        self.load_entries()
