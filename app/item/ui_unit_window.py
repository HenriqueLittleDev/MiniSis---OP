# app/item/ui_unit_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QPushButton, QTableView, QHeaderView, QAbstractItemView, QMessageBox,
    QDialog, QFormLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from app.item.unit_service import UnitService
from app.utils.ui_utils import show_error_message

class UnitEditDialog(QDialog):
    def __init__(self, parent=None, unit_id=None, name="", abbreviation=""):
        super().__init__(parent)
        self.unit_id = unit_id
        self.setWindowTitle("Editar Unidade" if unit_id else "Nova Unidade")

        layout = QFormLayout(self)
        self.name_input = QLineEdit(name)
        self.abbreviation_input = QLineEdit(abbreviation)
        layout.addRow(QLabel("Nome:"), self.name_input)
        layout.addRow(QLabel("Sigla:"), self.abbreviation_input)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)
        layout.addRow(buttons_layout)

    def get_data(self):
        return self.name_input.text(), self.abbreviation_input.text()

class UnitWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.unit_service = UnitService()
        self.setWindowTitle("Cadastro de Unidades de Medida")
        self.setGeometry(200, 200, 500, 400)
        self.setup_ui()
        self.load_units()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()
        new_button = QPushButton("Nova")
        new_button.clicked.connect(self.open_new_dialog)
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(self.open_edit_dialog)
        delete_button = QPushButton("Excluir")
        delete_button.clicked.connect(self.delete_unit)
        buttons_layout.addStretch()
        buttons_layout.addWidget(new_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        main_layout.addLayout(buttons_layout)

        results_group = QGroupBox("Unidades Cadastradas")
        results_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Nome", "Sigla"])
        self.table_view.setModel(self.table_model)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.setColumnHidden(0, True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.doubleClicked.connect(self.open_edit_dialog)

        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

    def load_units(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        response = self.unit_service.get_all_units()
        if response["success"]:
            for unit in response["data"]:
                row = [
                    QStandardItem(str(unit['ID'])),
                    QStandardItem(unit['NOME']),
                    QStandardItem(unit['SIGLA'])
                ]
                self.table_model.appendRow(row)
        else:
            show_error_message(self, "Erro", response["message"])

    def open_new_dialog(self):
        dialog = UnitEditDialog(self)
        if dialog.exec():
            name, abbreviation = dialog.get_data()
            response = self.unit_service.add_unit(name, abbreviation)
            if response["success"]:
                self.load_units()
            else:
                show_error_message(self, "Erro", response["message"])

    def open_edit_dialog(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma unidade para editar.")
            return

        row = selected_rows[0].row()
        unit_id = int(self.table_model.item(row, 0).text())
        name = self.table_model.item(row, 1).text()
        abbreviation = self.table_model.item(row, 2).text()

        dialog = UnitEditDialog(self, unit_id, name, abbreviation)
        if dialog.exec():
            new_name, new_abbreviation = dialog.get_data()
            response = self.unit_service.update_unit(unit_id, new_name, new_abbreviation)
            if response["success"]:
                self.load_units()
            else:
                show_error_message(self, "Erro", response["message"])

    def delete_unit(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione uma unidade para excluir.")
            return

        row = selected_rows[0].row()
        unit_id = int(self.table_model.item(row, 0).text())
        name = self.table_model.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a unidade '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            response = self.unit_service.delete_unit(unit_id)
            if response["success"]:
                self.load_units()
            else:
                show_error_message(self, "Erro", response["message"])
