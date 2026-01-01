# app/item/ui_edit_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QHeaderView, QTabWidget,
    QTableWidget, QTableWidgetItem, QLabel, QDoubleSpinBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from app.services.item_service import ItemService
from app.ui_utils import NumericTableWidgetItem

class EditWindow(QWidget):
    def __init__(self, item_id=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.item_service = ItemService()
        self.current_item_id = item_id
        self.has_unsaved_changes = False

        self.setWindowTitle(f"Editando Item #{item_id}" if item_id else "Novo Item")
        self.setGeometry(200, 200, 700, 600)

        self.main_layout = QVBoxLayout(self)
        self.create_header_buttons()
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.create_main_tab()
        self.create_composition_tab()
        self.populate_units_combobox()
        self.load_item_data()

        self.type_combo.currentTextChanged.connect(self.toggle_composition_tab)
        self.search_window = None

        self.description_input.textChanged.connect(self._set_unsaved_changes)
        self.type_combo.currentIndexChanged.connect(self._set_unsaved_changes)
        self.unit_combo.currentIndexChanged.connect(self._set_unsaved_changes)

    def _set_unsaved_changes(self):
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.setWindowTitle(self.windowTitle() + "*")

    def closeEvent(self, event):
        if self.has_unsaved_changes:
            # For simplicity, we will just discard changes without asking
            print("Aviso: Janela fechada com alterações não salvas. As alterações foram descartadas.")
            event.accept()
        else:
            event.accept()

    def create_header_buttons(self):
        header_layout = QHBoxLayout()
        new_button = QPushButton("Novo")
        new_button.clicked.connect(self.new_item)
        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_item)
        delete_button = QPushButton("Excluir")
        delete_button.clicked.connect(self.delete_item)
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close)
        header_layout.addStretch()
        header_layout.addWidget(new_button)
        header_layout.addWidget(save_button)
        header_layout.addWidget(delete_button)
        header_layout.addWidget(close_button)
        self.main_layout.addLayout(header_layout)

    def create_main_tab(self):
        main_widget = QWidget()
        layout = QFormLayout(main_widget)
        self.description_input = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Insumo", "Produto", "Ambos"])
        self.unit_combo = QComboBox()
        layout.addRow("Descrição:", self.description_input)
        layout.addRow("Tipo de Item:", self.type_combo)
        layout.addRow("Unidade:", self.unit_combo)
        self.tab_widget.addTab(main_widget, "Principal")

    def create_composition_tab(self):
        self.composition_widget = QWidget()
        layout = QVBoxLayout(self.composition_widget)
        self.selected_material = None
        edit_group = QGroupBox("Insumo")
        edit_group_layout = QVBoxLayout(edit_group)
        input_layout = QHBoxLayout()
        self.material_display = QLineEdit()
        self.material_display.setPlaceholderText("Selecione um insumo...")
        self.material_display.setReadOnly(True)
        input_layout.addWidget(self.material_display, 6)
        self.quantity_spinbox = QDoubleSpinBox()
        self.quantity_spinbox.setRange(0.0, 99999.99)
        self.quantity_spinbox.setDecimals(4)
        input_layout.addWidget(self.quantity_spinbox, 2)
        self.unit_label = QLabel("Un.")
        self.unit_label.setFixedWidth(40)
        input_layout.addWidget(self.unit_label)
        search_button = QPushButton("Buscar...")
        search_button.clicked.connect(self.open_material_search)
        input_layout.addWidget(search_button)
        edit_group_layout.addLayout(input_layout)
        self.add_update_button = QPushButton("Adicionar Insumo")
        self.add_update_button.clicked.connect(self.add_update_composition_item)
        edit_group_layout.addWidget(self.add_update_button)
        layout.addWidget(edit_group)
        self.composition_table = QTableWidget()
        self.composition_table.setColumnCount(6)
        self.composition_table.setHorizontalHeaderLabels(["ID Insumo", "Descrição", "Qtd", "Un.", "Custo Unit.", "Custo Total"])
        self.composition_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.composition_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.composition_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.composition_table.setColumnHidden(0, True)
        self.composition_table.verticalHeader().setVisible(False)
        self.composition_table.setSortingEnabled(True)
        self.composition_table.setStyleSheet("QTableView::item:selected { background-color: #D3D3D3; color: black; }")
        layout.addWidget(self.composition_table)
        action_bar_layout = QHBoxLayout()
        self.edit_selected_button = QPushButton("Editar Selecionado")
        self.edit_selected_button.clicked.connect(self.load_selected_for_edit)
        self.remove_selected_button = QPushButton("Remover Selecionado")
        self.remove_selected_button.clicked.connect(self.remove_selected_composition_item)
        action_bar_layout.addStretch()
        action_bar_layout.addWidget(self.edit_selected_button)
        action_bar_layout.addWidget(self.remove_selected_button)
        layout.addLayout(action_bar_layout)
        self.total_cost_label = QLabel("Custo Total da Composição: R$ 0.00")
        layout.addWidget(self.total_cost_label, 0, Qt.AlignRight)
        self.tab_widget.addTab(self.composition_widget, "Composição")

    def populate_units_combobox(self):
        response = self.item_service.list_units()
        if not response["success"]:
            print(f"UI Error: {response['message']}")

        for unit in response["data"]:
            self.unit_combo.addItem(f"{unit['NOME']} ({unit['SIGLA']})", userData=unit['ID'])

    def load_item_data(self):
        if self.current_item_id:
            response = self.item_service.get_item_by_id(self.current_item_id)
            if response["success"]:
                item = response["data"]
                self.description_input.setText(item['DESCRICAO'])
                self.type_combo.setCurrentText(item['TIPO_ITEM'])
                unit_index = self.unit_combo.findData(item['ID_UNIDADE'])
                if unit_index != -1:
                    self.unit_combo.setCurrentIndex(unit_index)
                self.load_composition_data()
        self.toggle_composition_tab()

    def load_composition_data(self):
        self.composition_table.setRowCount(0)
        if self.current_item_id:
            response = self.item_service.get_composition(self.current_item_id)
            if response["success"]:
                for comp_item in response["data"]:
                    self.add_row_to_composition_grid(
                        comp_item['ID_INSUMO'],
                        comp_item['DESCRICAO'],
                        comp_item['QUANTIDADE'],
                        comp_item['CUSTO_MEDIO'],
                        comp_item['SIGLA']
                    )
            else:
                print(f"UI Error: {response['message']}")
            self.update_total_cost()

    def toggle_composition_tab(self):
        item_type = self.type_combo.currentText()
        is_visible = item_type in ("Produto", "Ambos")
        self.tab_widget.setTabVisible(self.tab_widget.indexOf(self.composition_widget), is_visible)

    def open_material_search(self):
        from app.item.ui_search_window import SearchWindow
        if self.search_window is None:
            self.search_window = SearchWindow(selection_mode=True, item_type_filter=['Insumo', 'Ambos'], parent=self)
            self.search_window.item_selected.connect(self.set_selected_material)
            self.search_window.destroyed.connect(lambda: setattr(self, 'search_window', None))
            self.search_window.show()
        else:
            self.search_window.activateWindow()
            self.search_window.raise_()

    def set_selected_material(self, item_data):
        self.selected_material = item_data
        self.material_display.setText(item_data['DESCRICAO'])
        self.unit_label.setText(item_data['SIGLA'].upper())
        self.quantity_spinbox.setFocus()

    def add_update_composition_item(self):
        if not self.selected_material:
            print("UI Warning: Nenhum insumo selecionado.")
            return

        quantity = self.quantity_spinbox.value()
        if quantity <= 0:
            print("UI Warning: A quantidade deve ser maior que zero.")
            return

        material_id = self.selected_material['ID']
        response = self.item_service.validate_bom_item(self.current_item_id, material_id)
        if not response["success"]:
            print(f"UI Validation Error: {response['message']}")
            return

        for row in range(self.composition_table.rowCount()):
            if int(self.composition_table.item(row, 0).text()) == material_id:
                self.composition_table.item(row, 2).setText(str(quantity))
                unit_cost = float(self.composition_table.item(row, 4).text())
                total_cost = quantity * unit_cost
                self.composition_table.item(row, 5).setText(f"{total_cost:.4f}")
                self.update_total_cost()
                self._clear_material_form()
                return

        response = self.item_service.get_item_by_id(material_id)
        unit_cost = response["data"]['CUSTO_MEDIO'] if response["success"] else 0

        self.add_row_to_composition_grid(
            material_id, self.selected_material['DESCRICAO'], quantity,
            unit_cost, self.selected_material['SIGLA']
        )
        self.update_total_cost()
        self._clear_material_form()
        self._set_unsaved_changes()

    def load_selected_for_edit(self):
        selected_rows = self.composition_table.selectionModel().selectedRows()
        if not selected_rows:
            print("UI Warning: Selecione um item para editar.")
            return

        selected_row = selected_rows[0].row()
        self.selected_material = {
            'ID': int(self.composition_table.item(selected_row, 0).text()),
            'DESCRICAO': self.composition_table.item(selected_row, 1).text(),
            'SIGLA': self.composition_table.item(selected_row, 3).text()
        }
        self.material_display.setText(self.selected_material['DESCRICAO'])
        self.unit_label.setText(self.selected_material['SIGLA'].upper())
        self.quantity_spinbox.setValue(float(self.composition_table.item(selected_row, 2).text()))
        self.add_update_button.setText("Atualizar Insumo")

    def remove_selected_composition_item(self):
        selected_rows = self.composition_table.selectionModel().selectedRows()
        if not selected_rows:
            print("UI Warning: Selecione um item para remover.")
            return
        for index in sorted([idx.row() for idx in selected_rows], reverse=True):
            self.composition_table.removeRow(index)
        self.update_total_cost()
        self._set_unsaved_changes()

    def _clear_material_form(self):
        self.selected_material = None
        self.material_display.clear()
        self.quantity_spinbox.setValue(0.0)
        self.unit_label.clear()
        self.add_update_button.setText("Adicionar")
        self.composition_table.clearSelection()

    def add_row_to_composition_grid(self, material_id, desc, qty, cost, unit):
        row = self.composition_table.rowCount()
        self.composition_table.insertRow(row)
        total_cost = qty * cost
        self.composition_table.setItem(row, 0, NumericTableWidgetItem(str(material_id)))
        self.composition_table.setItem(row, 1, QTableWidgetItem(desc))
        self.composition_table.setItem(row, 2, NumericTableWidgetItem(str(qty)))
        self.composition_table.setItem(row, 3, QTableWidgetItem(unit.upper()))
        self.composition_table.setItem(row, 4, NumericTableWidgetItem(f"{cost:.4f}"))
        self.composition_table.setItem(row, 5, NumericTableWidgetItem(f"{total_cost:.4f}"))

    def update_total_cost(self):
        total = sum(float(self.composition_table.item(r, 5).text()) for r in range(self.composition_table.rowCount()))
        self.total_cost_label.setText(f"Custo Total da Composição: R$ {total:.4f}")

    def new_item(self):
        self.current_item_id = None
        self.setWindowTitle("Novo Item")
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.unit_combo.setCurrentIndex(0)
        self.composition_table.setRowCount(0)
        self.update_total_cost()
        self.toggle_composition_tab()
        self.description_input.setFocus()
        self._clear_material_form()
        self.has_unsaved_changes = False
        self.setWindowTitle("Novo Item")

    def save_item(self):
        desc = self.description_input.text()
        item_type = self.type_combo.currentText()
        unit_id = self.unit_combo.currentData()

        if self.current_item_id is None:
            response = self.item_service.add_item(desc, item_type, unit_id)
            if response["success"]:
                self.current_item_id = response["data"]
                print(f"Info: Item #{self.current_item_id} criado com sucesso.")
            else:
                print(f"UI Error: {response['message']}")
                return
        else:
            response = self.item_service.update_item(self.current_item_id, desc, item_type, unit_id)
            if not response["success"]:
                print(f"UI Error: {response['message']}")
                return

        if self.tab_widget.isTabVisible(self.tab_widget.indexOf(self.composition_widget)):
            composition = [{'id_insumo': int(self.composition_table.item(r, 0).text()),
                            'quantidade': float(self.composition_table.item(r, 2).text())}
                           for r in range(self.composition_table.rowCount())]
            response = self.item_service.update_composition(self.current_item_id, composition)
            if not response["success"]:
                print(f"UI Error: {response['message']}")
                return

        print(f"Info: Item #{self.current_item_id} salvo com sucesso!")
        self.setWindowTitle(f"Editando Item #{self.current_item_id}")
        self.has_unsaved_changes = False

    def delete_item(self):
        if self.current_item_id is None:
            print("UI Error: Nenhum item carregado para excluir.")
            return

        # Bypassing user confirmation as requested
        print(f"Aviso: Excluindo item #{self.current_item_id} sem confirmação.")
        response = self.item_service.delete_item(self.current_item_id)
        if response["success"]:
            print(f"Info: {response['message']}")
            self.has_unsaved_changes = False
            self.close()
        else:
            print(f"UI Error: {response['message']}")
