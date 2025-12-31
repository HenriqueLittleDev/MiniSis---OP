# app/supplier/ui_supplier_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from ..services.supplier_service import SupplierService
from ..ui_utils import show_error_message
from .ui_supplier_edit_window import SupplierEditWindow

class SupplierSearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()
        self.edit_window = None
        self.setWindowTitle("Pesquisa de Fornecedores")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por nome...")
        self.search_input.returnPressed.connect(self.load_suppliers)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.load_suppliers)
        new_button = QPushButton("Novo")
        new_button.clicked.connect(self.open_new_supplier_window)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_button)
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        results_group = QGroupBox("Fornecedores Cadastrados")
        results_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Nome", "CNPJ", "Telefone", "Email"])
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setColumnHidden(0, True)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.doubleClicked.connect(self.open_edit_supplier_window)
        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

    def load_suppliers(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        response = self.supplier_service.get_all_suppliers()
        if response["success"]:
            for supplier in response["data"]:
                row = [
                    QStandardItem(str(supplier['ID'])),
                    QStandardItem(supplier['NOME']),
                    QStandardItem(supplier['CNPJ']),
                    QStandardItem(supplier['TELEFONE']),
                    QStandardItem(supplier['EMAIL'])
                ]
                self.table_model.appendRow(row)
        else:
            show_error_message(self, response["message"])

    def open_new_supplier_window(self):
        self.show_edit_window(supplier_id=None)

    def open_edit_supplier_window(self, model_index):
        supplier_id = int(self.table_model.item(model_index.row(), 0).text())
        self.show_edit_window(supplier_id=supplier_id)

    def show_edit_window(self, supplier_id):
        if self.edit_window and self.edit_window.isVisible():
            self.edit_window.activateWindow()
            self.edit_window.raise_()
            return

        self.edit_window = SupplierEditWindow(supplier_id=supplier_id)
        self.edit_window.destroyed.connect(self.on_edit_window_closed)
        self.edit_window.show()

    def on_edit_window_closed(self):
        self.edit_window = None
        self.load_suppliers()
