# app/supplier/ui_supplier_edit_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QPushButton, QTabWidget, QFormLayout, QMessageBox
)
from ..services.supplier_service import SupplierService
from ..ui_utils import show_error_message

class SupplierEditWindow(QWidget):
    def __init__(self, supplier_id=None):
        super().__init__()
        self.supplier_service = SupplierService()
        self.current_supplier_id = supplier_id

        title = f"Editando Fornecedor #{supplier_id}" if supplier_id else "Novo Fornecedor"
        self.setWindowTitle(title)
        self.setGeometry(250, 250, 600, 400)
        self.setup_ui()

        if self.current_supplier_id:
            self.load_supplier_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        self.new_button = QPushButton("Novo")
        self.new_button.clicked.connect(self.clear_form)
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_supplier)
        self.delete_button = QPushButton("Excluir")
        self.delete_button.clicked.connect(self.delete_supplier)
        header_layout.addStretch()
        header_layout.addWidget(self.new_button)
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.delete_button)
        main_layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.setup_identification_tab()
        self.setup_address_tab()

    def setup_identification_tab(self):
        ident_widget = QWidget()
        layout = QFormLayout(ident_widget)
        self.name_input = QLineEdit()
        self.cnpj_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        layout.addRow("Nome:", self.name_input)
        layout.addRow("CNPJ:", self.cnpj_input)
        layout.addRow("Telefone:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        self.tab_widget.addTab(ident_widget, "Identificação")

    def setup_address_tab(self):
        address_widget = QWidget()
        layout = QFormLayout(address_widget)
        self.logradouro_input = QLineEdit()
        self.numero_input = QLineEdit()
        self.complemento_input = QLineEdit()
        self.bairro_input = QLineEdit()
        self.cidade_input = QLineEdit()
        self.uf_input = QLineEdit()
        self.cep_input = QLineEdit()
        layout.addRow("Logradouro:", self.logradouro_input)
        layout.addRow("Número:", self.numero_input)
        layout.addRow("Complemento:", self.complemento_input)
        layout.addRow("Bairro:", self.bairro_input)
        layout.addRow("Cidade:", self.cidade_input)
        layout.addRow("UF:", self.uf_input)
        layout.addRow("CEP:", self.cep_input)
        self.tab_widget.addTab(address_widget, "Endereço")

    def load_supplier_data(self):
        response = self.supplier_service.get_supplier_by_id(self.current_supplier_id)
        if response["success"]:
            supplier = response["data"]
            self.name_input.setText(supplier['NOME'])
            self.cnpj_input.setText(supplier['CNPJ'])
            self.phone_input.setText(supplier['TELEFONE'])
            self.email_input.setText(supplier['EMAIL'])
            self.logradouro_input.setText(supplier['LOGRADOURO'])
            self.numero_input.setText(supplier['NUMERO'])
            self.complemento_input.setText(supplier['COMPLEMENTO'])
            self.bairro_input.setText(supplier['BAIRRO'])
            self.cidade_input.setText(supplier['CIDADE'])
            self.uf_input.setText(supplier['UF'])
            self.cep_input.setText(supplier['CEP'])
        else:
            show_error_message(self, response["message"])

    def save_supplier(self):
        name = self.name_input.text()
        cnpj = self.cnpj_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        address = {
            'logradouro': self.logradouro_input.text(),
            'numero': self.numero_input.text(),
            'complemento': self.complemento_input.text(),
            'bairro': self.bairro_input.text(),
            'cidade': self.cidade_input.text(),
            'uf': self.uf_input.text(),
            'cep': self.cep_input.text()
        }

        if self.current_supplier_id:
            response = self.supplier_service.update_supplier(self.current_supplier_id, name, cnpj, phone, email, address)
        else:
            response = self.supplier_service.add_supplier(name, cnpj, phone, email, address)

        if response["success"]:
            QMessageBox.information(self, "Sucesso", response["message"])
            if not self.current_supplier_id and response.get("data"):
                self.current_supplier_id = response["data"]
                self.setWindowTitle(f"Editando Fornecedor #{self.current_supplier_id}")
        else:
            show_error_message(self, response["message"])

    def delete_supplier(self):
        if not self.current_supplier_id:
            show_error_message(self, "Nenhum fornecedor carregado para excluir.")
            return

        reply = QMessageBox.question(self, "Confirmar Exclusão", "Tem certeza que deseja excluir este fornecedor?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            response = self.supplier_service.delete_supplier(self.current_supplier_id)
            if response["success"]:
                QMessageBox.information(self, "Sucesso", response["message"])
                self.close()
            else:
                show_error_message(self, response["message"])

    def clear_form(self):
        self.current_supplier_id = None
        self.setWindowTitle("Novo Fornecedor")
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        self.tab_widget.setCurrentIndex(0)
