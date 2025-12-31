# app/stock/ui_entry_edit_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QHeaderView, QTableWidget, QTableWidgetItem,
    QLabel, QDateEdit, QAbstractItemView, QDoubleSpinBox
)
from PySide6.QtCore import QDate, Qt
from . import entry_operations
from ..item.ui_search_window import SearchWindow
from ..ui_utils import NumericTableWidgetItem

class EntryEditWindow(QWidget):
    def __init__(self, entry_id=None):
        super().__init__()
        self.current_entry_id = entry_id
        self.search_item_window = None

        title = f"Editando Entrada #{entry_id}" if entry_id else "Nova Entrada de Insumo"
        self.setWindowTitle(title)
        self.setGeometry(250, 250, 800, 700)
        self.setup_ui()

        if self.current_entry_id:
            self.load_entry_data()
        else:
            self.new_entry()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)

        # Botões do Cabeçalho
        header_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_entry)
        self.finalize_button = QPushButton("Finalizar Entrada")
        self.finalize_button.clicked.connect(self.finalize_entry)
        header_layout.addStretch()
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.finalize_button)
        self.main_layout.addLayout(header_layout)

        # Formulário Principal
        form_group = QGroupBox("Dados da Nota de Entrada")
        form = QFormLayout()
        self.entry_id_display = QLabel("(Nova)")
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        self.supplier_input = QLineEdit()
        self.note_number_input = QLineEdit()
        self.status_display = QLabel("Em Aberto")

        form.addRow("ID da Entrada:", self.entry_id_display)
        form.addRow("Data da Entrada:", self.date_input)
        form.addRow("Fornecedor:", self.supplier_input)
        form.addRow("Número da Nota:", self.note_number_input)
        form.addRow("Status:", self.status_display)
        form_group.setLayout(form)
        self.main_layout.addWidget(form_group)

        # Itens da Nota
        items_group = QGroupBox("Insumos da Nota")
        items_layout = QVBoxLayout()
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["ID Insumo", "Descrição", "Un.", "Quantidade", "Valor Unit.", "Valor Total"])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setColumnHidden(0, True)
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.items_table.cellChanged.connect(self.update_total_value)
        items_layout.addWidget(self.items_table)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Adicionar Insumo...")
        add_button.clicked.connect(self.open_item_search)
        remove_button = QPushButton("Remover Insumo")
        remove_button.clicked.connect(self.remove_item)
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        items_layout.addLayout(buttons_layout)

        items_group.setLayout(items_layout)
        self.main_layout.addWidget(items_group)

    def new_entry(self):
        self.current_entry_id = None
        self.setWindowTitle("Nova Entrada de Insumo")
        self.entry_id_display.setText("(Nova)")
        self.date_input.setDate(QDate.currentDate())
        self.supplier_input.clear()
        self.note_number_input.clear()
        self.status_display.setText("Em Aberto")
        self.items_table.setRowCount(0)
        self.set_read_only(False)

    def save_entry(self):
        date = self.date_input.date().toString("yyyy-MM-dd")
        supplier = self.supplier_input.text()
        note_number = self.note_number_input.text()

        items = []
        for row in range(self.items_table.rowCount()):
            items.append({
                'id_insumo': int(self.items_table.item(row, 0).text()),
                'quantidade': float(self.items_table.item(row, 3).text()),
                'valor_unitario': float(self.items_table.item(row, 4).text())
            })

        if self.current_entry_id:
            # Atualizar mestre e itens
            entry_operations.update_entry_master(self.current_entry_id, date, supplier, note_number)
            entry_operations.update_entry_items(self.current_entry_id, items)
            QMessageBox.information(self, "Sucesso", "Nota de entrada atualizada.")
        else:
            # Criar nova entrada e depois adicionar itens
            new_id = entry_operations.create_entry(date, supplier, note_number)
            if new_id:
                self.current_entry_id = new_id
                entry_operations.update_entry_items(new_id, items)
                self.setWindowTitle(f"Editando Entrada #{new_id}")
                self.entry_id_display.setText(str(new_id))
                QMessageBox.information(self, "Sucesso", f"Nota de entrada #{new_id} criada.")
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível criar a nota de entrada.")

    def load_entry_data(self):
        details = entry_operations.get_entry_details(self.current_entry_id)
        if details:
            master = details['master']
            self.entry_id_display.setText(str(master['ID']))
            self.date_input.setDate(QDate.fromString(master['DATA_ENTRADA'], "yyyy-MM-dd"))
            self.supplier_input.setText(master.get('FORNECEDOR', ''))
            self.note_number_input.setText(master.get('NUMERO_NOTA', ''))
            self.status_display.setText(master.get('STATUS', ''))

            self.items_table.setRowCount(0)
            for item in details['items']:
                self.add_item_to_table(item, is_loading=True)

            if master.get('STATUS') == 'Finalizada':
                self.set_read_only(True)

    def open_item_search(self):
        if self.search_item_window and self.search_item_window.isVisible():
            self.search_item_window.activateWindow()
            return
        self.search_item_window = SearchWindow(selection_mode=True, item_type_filter=['Insumo', 'Ambos'])
        self.search_item_window.item_selected.connect(self.add_item_from_search)
        self.search_item_window.show()

    def add_item_from_search(self, item_data):
        # Verificar se o item já está na tabela
        for row in range(self.items_table.rowCount()):
            if int(self.items_table.item(row, 0).text()) == item_data['ID']:
                QMessageBox.warning(self, "Atenção", "Este insumo já está na lista.")
                return

        item = {
            'ID_INSUMO': item_data['ID'],
            'DESCRICAO': item_data['DESCRICAO'],
            'SIGLA': item_data['SIGLA'],
            'QUANTIDADE': 1.0,
            'VALOR_UNITARIO': 0.0
        }
        self.add_item_to_table(item)

    def add_item_to_table(self, item, is_loading=False):
        self.items_table.blockSignals(True)
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        self.items_table.setItem(row, 0, QTableWidgetItem(str(item['ID_INSUMO'])))
        self.items_table.setItem(row, 1, QTableWidgetItem(item['DESCRICAO']))
        self.items_table.setItem(row, 2, QTableWidgetItem(item['SIGLA']))
        self.items_table.setItem(row, 3, NumericTableWidgetItem(str(item['QUANTIDADE'])))
        self.items_table.setItem(row, 4, NumericTableWidgetItem(f"{item['VALOR_UNITARIO']:.2f}"))

        total = item['QUANTIDADE'] * item['VALOR_UNITARIO']
        self.items_table.setItem(row, 5, NumericTableWidgetItem(f"{total:.2f}"))

        # Apenas Descrição e Unidade não são editáveis
        self.items_table.item(row, 1).setFlags(self.items_table.item(row, 1).flags() & ~Qt.ItemIsEditable)
        self.items_table.item(row, 2).setFlags(self.items_table.item(row, 2).flags() & ~Qt.ItemIsEditable)
        self.items_table.item(row, 5).setFlags(self.items_table.item(row, 5).flags() & ~Qt.ItemIsEditable)

        self.items_table.blockSignals(False)
        if not is_loading:
            self.update_total_value()

    def remove_item(self):
        rows = self.items_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um insumo para remover.")
            return
        for index in sorted([r.row() for r in rows], reverse=True):
            self.items_table.removeRow(index)
        self.update_total_value()

    def update_total_value(self, row=None, column=None):
        if row is None or column not in [3, 4]: return # Atualiza apenas se qtd ou vlr unit. mudar

        self.items_table.blockSignals(True)
        try:
            quantity = float(self.items_table.item(row, 3).text())
            unit_price = float(self.items_table.item(row, 4).text())
            total = quantity * unit_price
            self.items_table.setItem(row, 5, NumericTableWidgetItem(f"{total:.2f}"))
        except (ValueError, TypeError):
             self.items_table.setItem(row, 5, NumericTableWidgetItem("0.00"))
        self.items_table.blockSignals(False)

    def set_read_only(self, read_only):
        """Ativa/desativa o modo somente leitura para a janela."""
        self.date_input.setReadOnly(read_only)
        self.supplier_input.setReadOnly(read_only)
        self.note_number_input.setReadOnly(read_only)
        self.items_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers if read_only else QAbstractItemView.DoubleClicked
        )
        self.save_button.setDisabled(read_only)
        self.finalize_button.setDisabled(read_only)
        # Os botões de adicionar/remover itens também devem ser desabilitados
        self.items_table.parent().findChild(QPushButton, "Adicionar Insumo...").setDisabled(read_only)
        self.items_table.parent().findChild(QPushButton, "Remover Insumo").setDisabled(read_only)

    def finalize_entry(self):
        if not self.current_entry_id:
            QMessageBox.warning(self, "Atenção", "Salve a nota de entrada antes de finalizá-la.")
            return

        reply = QMessageBox.question(
            self, "Confirmar Finalização",
            "Você tem certeza que deseja finalizar esta entrada?\n"
            "Esta ação atualizará o estoque e o custo dos insumos e não poderá ser desfeita.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Salva quaisquer alterações pendentes antes de finalizar
            self.save_entry()
            success, message = entry_operations.finalize_entry(self.current_entry_id)
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.load_entry_data() # Recarrega para refletir o novo status e modo read-only
            else:
                QMessageBox.critical(self, "Erro ao Finalizar", message)
