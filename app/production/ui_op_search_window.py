# app/production/ui_op_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from app.production import order_operations
from app.utils.date_utils import format_date_for_display

class OPSearchWindow(QWidget):
    op_selected = Signal(int)
    
    def __init__(self, selection_mode=False):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.selection_mode = selection_mode
        self.production_order_window = None
        self.setWindowTitle("Pesquisa de Ordens de Produção")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui()
        self.load_ops()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        # Search Group
        search_group = QGroupBox("Pesquisa")
        layout = QHBoxLayout()
        self.search_field = QComboBox()
        self.search_field.addItems(["ID", "Status"])
        self.search_term = QLineEdit()
        self.search_term.returnPressed.connect(self.load_ops)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.load_ops)
        new_op_button = QPushButton("Nova Ordem de Produção")
        new_op_button.clicked.connect(self.open_new_production_order)
        layout.addWidget(self.search_field)
        layout.addWidget(self.search_term, 1)
        layout.addWidget(search_button)
        if not self.selection_mode:
            layout.addWidget(new_op_button)
        search_group.setLayout(layout)
        self.main_layout.addWidget(search_group)
        # Results Group
        results_group = QGroupBox("Resultados")
        layout = QVBoxLayout()
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Número", "Data Criação", "Data Prevista", "Status"])
        self.table_view.setModel(self.table_model)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setStyleSheet("QTableView::item:selected { background-color: #D3D3D3; color: black; }")
        self.table_view.doubleClicked.connect(self.handle_double_click)
        layout.addWidget(self.table_view)
        results_group.setLayout(layout)
        self.main_layout.addWidget(results_group)

    def load_ops(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        search_term = self.search_term.text()
        search_field = self.search_field.currentText().upper()
        ops = order_operations.list_ops(search_term, search_field)
        for op in ops:
            row = [
                QStandardItem(str(op['ID'])),
                QStandardItem(op.get('NUMERO', '')),
                QStandardItem(format_date_for_display(op.get('DATA_CRIACAO', ''))),
                QStandardItem(format_date_for_display(op.get('DATA_PREVISTA', ''))),
                QStandardItem(op.get('STATUS', ''))
            ]
            self.table_model.appendRow(row)

    def open_new_production_order(self):
        """Opens the production order window for a new order."""
        self.open_production_order_window(op_id=None)

    def handle_double_click(self, model_index):
        """Opens the production order window for the selected order."""
        op_id = int(self.table_model.item(model_index.row(), 0).text())
        if self.selection_mode:
            self.op_selected.emit(op_id)
            self.close()
        else:
            self.open_production_order_window(op_id=op_id)

    def open_production_order_window(self, op_id=None):
        """Opens the production order window, creating a new one if it doesn't exist."""
        from app.production.ui_order_window import ProductionOrderWindow
        if self.production_order_window is None:
            self.production_order_window = ProductionOrderWindow(op_id=op_id)
            self.production_order_window.destroyed.connect(self.on_production_order_window_closed)
            self.production_order_window.show()
        else:
            self.production_order_window.activateWindow()
            self.production_order_window.raise_()

    def on_production_order_window_closed(self):
        """Handles the closing of the production order window."""
        self.production_order_window = None
        self.load_ops()
