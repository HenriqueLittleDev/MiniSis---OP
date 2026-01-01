# app/database.py
import sqlite3
import os
import atexit
import platform

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = self._get_db_path()
            self.connection = None
            self.initialize_database()
            atexit.register(self.close_connection)
            self.initialized = True

    def _get_db_path(self):
        if os.environ.get("MINISIS_ENV") == "test":
            return ":memory:"

        # Use a more flexible path that works across different OSes
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "MiniSis", "Gestão de Produção", "Dados", "DADOS.DB")

    def initialize_database(self):
        is_memory_db = self.db_path == ":memory:"
        if not is_memory_db:
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        self.connection = sqlite3.connect(self.db_path, check_same_thread=False if is_memory_db else True)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()
        print(f"Banco de dados inicializado em: {self.db_path}")

    def get_connection(self):
        if self.connection is None:
            raise Exception("A conexão com o banco de dados não foi inicializada.")
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Conexão com o banco de dados fechada.")

    def _create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TUNIDADE (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOME TEXT NOT NULL UNIQUE,
            SIGLA TEXT NOT NULL UNIQUE
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TITEM (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DESCRICAO TEXT NOT NULL UNIQUE,
            TIPO_ITEM TEXT NOT NULL CHECK(TIPO_ITEM IN ('Insumo', 'Produto', 'Ambos')),
            ID_UNIDADE INTEGER NOT NULL,
            SALDO_ESTOQUE REAL NOT NULL DEFAULT 0,
            CUSTO_MEDIO REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (ID_UNIDADE) REFERENCES TUNIDADE (ID)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TFORNECEDOR (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            RAZAO_SOCIAL TEXT NOT NULL UNIQUE,
            NOME_FANTASIA TEXT,
            CNPJ TEXT,
            TELEFONE TEXT,
            EMAIL TEXT,
            LOGRADOURO TEXT,
            NUMERO TEXT,
            COMPLEMENTO TEXT,
            BAIRRO TEXT,
            CIDADE TEXT,
            UF TEXT,
            CEP TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TENTRADANOTA (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_FORNECEDOR INTEGER,
            DATA_ENTRADA TEXT NOT NULL,
            DATA_DIGITACAO TEXT,
            NUMERO_NOTA TEXT,
            VALOR_TOTAL REAL,
            STATUS TEXT NOT NULL CHECK(STATUS IN ('Em Aberto', 'Finalizada')),
            FOREIGN KEY (ID_FORNECEDOR) REFERENCES TFORNECEDOR (ID)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TCOMPOSICAO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_PRODUTO INTEGER NOT NULL,
            ID_INSUMO INTEGER NOT NULL,
            QUANTIDADE REAL NOT NULL,
            FOREIGN KEY (ID_PRODUTO) REFERENCES TITEM (ID),
            FOREIGN KEY (ID_INSUMO) REFERENCES TITEM (ID),
            UNIQUE (ID_PRODUTO, ID_INSUMO)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TORDEMPRODUCAO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DATA_CRIACAO TEXT NOT NULL,
            DATA_PREVISTA TEXT,
            STATUS TEXT NOT NULL CHECK(STATUS IN ('Planejada', 'Em Andamento', 'Concluída', 'Cancelada'))
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TORDEMPRODUCAO_ITENS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_ORDEM_PRODUCAO INTEGER NOT NULL,
            ID_PRODUTO INTEGER NOT NULL,
            QUANTIDADE_PRODUZIR REAL NOT NULL,
            FOREIGN KEY (ID_ORDEM_PRODUCAO) REFERENCES TORDEMPRODUCAO (ID),
            FOREIGN KEY (ID_PRODUTO) REFERENCES TITEM (ID),
            UNIQUE (ID_ORDEM_PRODUCAO, ID_PRODUTO)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TMOVIMENTO (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_ITEM INTEGER NOT NULL,
            TIPO_MOVIMENTO TEXT NOT NULL,
            QUANTIDADE REAL NOT NULL,
            VALOR_UNITARIO REAL,
            ID_ORDEM_PRODUCAO INTEGER,
            DATA_MOVIMENTO TEXT NOT NULL,
            FOREIGN KEY (ID_ITEM) REFERENCES TITEM (ID),
            FOREIGN KEY (ID_ORDEM_PRODUCAO) REFERENCES TORDEMPRODUCAO (ID)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TENTRADANOTA_ITENS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_ENTRADA INTEGER NOT NULL,
            ID_INSUMO INTEGER NOT NULL,
            QUANTIDADE REAL NOT NULL,
            VALOR_UNITARIO REAL NOT NULL,
            FOREIGN KEY (ID_ENTRADA) REFERENCES TENTRADANOTA (ID),
            FOREIGN KEY (ID_INSUMO) REFERENCES TITEM (ID),
            UNIQUE (ID_ENTRADA, ID_INSUMO)
        )
        ''')

        unidades = [('Grama', 'g'), ('Quilograma', 'kg'), ('Mililitro', 'ml'), ('Litro', 'L'), ('Unidade', 'un')]
        for nome, sigla in unidades:
            cursor.execute("SELECT ID FROM TUNIDADE WHERE NOME = ?", (nome,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO TUNIDADE (NOME, SIGLA) VALUES (?, ?)", (nome, sigla))

        self.connection.commit()

def get_db_manager():
    return DatabaseManager()
