# app/supplier/ui_supplier_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from app.services.supplier_service import SupplierService

class SupplierSearchWindow(QWidget):
    supplier_selected = Signal(dict)

    def __init__(self, selection_mode=False, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.supplier_service = SupplierService()
        self.edit_window = None
        self.selection_mode = selection_mode

        title = "Selecionar Fornecedor" if selection_mode else "Pesquisa de Fornecedor"
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 800, 600)

        self.main_layout = QVBoxLayout(self)
        self.create_search_group()
        self.create_results_group()
        self.load_suppliers()

    def create_search_group(self):
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()

        self.search_field_combo = QComboBox()
        self.search_field_combo.addItems(["Nome Fantasia", "ID", "Razão Social", "CNPJ", "Cidade"])

        self.search_text = QLineEdit()
        self.search_text.returnPressed.connect(self.load_suppliers)

        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.load_suppliers)

        new_button = QPushButton("Novo Fornecedor")
        new_button.clicked.connect(self.open_new_supplier_window)

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
        self.table_model.setHorizontalHeaderLabels(["ID", "Nome Fantasia", "Razão Social", "CNPJ", "Telefone", "Email", "Cidade", "UF"])
        self.table_view.setModel(self.table_model)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setStyleSheet("QTableView::item:selected { background-color: #D3D3D3; color: black; }")
        self.table_view.doubleClicked.connect(self.handle_double_click)

        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group)

    def load_suppliers(self):
        search_type_text = self.search_field_combo.currentText()
        search_content = self.search_text.text()
        self.table_model.removeRows(0, self.table_model.rowCount())

        if search_content:
            response = self.supplier_service.search_suppliers(search_type_text, search_content)
        else:
            response = self.supplier_service.get_all_suppliers()

        if not response["success"]:
            print(f"UI Error: {response['message']}")
            return

        for supplier in response["data"]:
            row = [
                QStandardItem(str(supplier['ID'])),
                QStandardItem(supplier['NOME_FANTASIA']),
                QStandardItem(supplier['RAZAO_SOCIAL']),
                QStandardItem(supplier['CNPJ']),
                QStandardItem(supplier['TELEFONE']),
                QStandardItem(supplier['EMAIL']),
                QStandardItem(supplier['CIDADE']),
                QStandardItem(supplier['UF'])
            ]
            self.table_model.appendRow(row)
            row_index = self.table_model.rowCount() - 1
            self.table_model.item(row_index, 0).setData(supplier)

    def handle_double_click(self, model_index):
        supplier_data = self.table_model.item(model_index.row(), 0).data()
        if self.selection_mode:
            self.supplier_selected.emit(supplier_data)
            self.close()
        else:
            self.open_edit_supplier_window(supplier_data['ID'])

    def open_new_supplier_window(self):
        self.show_edit_window(supplier_id=None)

    def open_edit_supplier_window(self, supplier_id):
        self.show_edit_window(supplier_id=supplier_id)

    def show_edit_window(self, supplier_id):
        from app.supplier.ui_supplier_edit_window import SupplierEditWindow
        if self.edit_window is None:
            self.edit_window = SupplierEditWindow(supplier_id=supplier_id, parent=self)
            self.edit_window.destroyed.connect(self.on_edit_window_closed)
            self.edit_window.show()
        else:
            self.edit_window.activateWindow()
            self.edit_window.raise_()

    def on_edit_window_closed(self):
        self.edit_window = None
        self.load_suppliers()
