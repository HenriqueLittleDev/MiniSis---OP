# app/item/unit_service.py
from app.item.unit_repository import UnitRepository

class UnitService:
    def __init__(self):
        self.unit_repository = UnitRepository()

    def add_unit(self, name, abbreviation):
        if not name or not abbreviation:
            return {"success": False, "message": "Nome e Sigla são obrigatórios."}

        try:
            new_id = self.unit_repository.add(name, abbreviation)
            if new_id:
                return {"success": True, "data": new_id, "message": "Unidade adicionada com sucesso."}
            else:
                return {"success": False, "message": "Unidade com este nome ou sigla já existe."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao adicionar unidade: {e}"}

    def get_all_units(self):
        try:
            units = self.unit_repository.get_all()
            return {"success": True, "data": units}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar unidades: {e}"}

    def update_unit(self, unit_id, name, abbreviation):
        if not all([unit_id, name, abbreviation]):
            return {"success": False, "message": "ID, Nome e Sigla são obrigatórios."}

        try:
            if self.unit_repository.update(unit_id, name, abbreviation):
                return {"success": True, "message": "Unidade atualizada com sucesso."}
            else:
                return {"success": False, "message": "Unidade com este nome ou sigla já existe."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar unidade: {e}"}

    def delete_unit(self, unit_id):
        try:
            if self.unit_repository.is_unit_in_use(unit_id):
                return {"success": False, "message": "Não é possível excluir: A unidade está sendo usada por um ou mais itens."}

            if self.unit_repository.delete(unit_id):
                return {"success": True, "message": "Unidade excluída com sucesso."}
            else:
                return {"success": False, "message": "Erro: Unidade não encontrada para exclusão."}
        except Exception as e:
            return {"success": False, "message": f"Erro no banco de dados ao tentar excluir a unidade: {e}"}
