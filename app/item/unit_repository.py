# app/item/unit_repository.py
from app.database.db import get_db_manager

class UnitRepository:
    def __init__(self):
        self.db_manager = get_db_manager()
        self.connection = self.db_manager.get_connection()

    def add(self, name, abbreviation):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO UNIDADE (NOME, SIGLA) VALUES (?, ?)",
                (name, abbreviation)
            )
            self.connection.commit()
            return cursor.lastrowid
        except self.connection.IntegrityError:
            self.connection.rollback()
            return None

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT ID, NOME, SIGLA FROM UNIDADE ORDER BY NOME")
        return cursor.fetchall()

    def update(self, unit_id, name, abbreviation):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE UNIDADE SET NOME = ?, SIGLA = ? WHERE ID = ?",
                (name, abbreviation, unit_id)
            )
            self.connection.commit()
            return True
        except self.connection.IntegrityError:
            self.connection.rollback()
            return False

    def delete(self, unit_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM UNIDADE WHERE ID = ?", (unit_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def is_unit_in_use(self, unit_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM ITEM WHERE ID_UNIDADE = ?", (unit_id,))
        return cursor.fetchone() is not None
