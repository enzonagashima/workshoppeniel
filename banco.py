"""
banco.py - Módulo de Banco de Dados (SQLite3)
Projeto: Mesa de Som Virtual (Workshop Didático)

Este arquivo é responsável por:
1. Criar o banco de dados 'mesa.db' e suas tabelas.
2. Inserir os dados iniciais dos instrumentos.
3. Fornecer funções para consultar e atualizar instrumentos, solicitações e volume auxiliar (retorno).
"""

import sqlite3
import os

DB_NAME = "mesa.db"

def conectar():
    """Conecta ao banco de dados SQLite e habilita retorno em dicionário/Row."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    """Cria as tabelas se não existirem e insere os instrumentos iniciais."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabela de Instrumentos (inclui volume_atual e volume_auxiliar)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instrumentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        volume_atual INTEGER NOT NULL DEFAULT 50,
        volume_auxiliar INTEGER NOT NULL DEFAULT 50,
        musico TEXT
    )
    """)

    # Tenta adicionar a coluna volume_auxiliar se a tabela já existia antes
    try:
        cursor.execute("ALTER TABLE instrumentos ADD COLUMN volume_auxiliar INTEGER NOT NULL DEFAULT 50")
    except sqlite3.OperationalError:
        pass

    # 2. Tabela de Solicitações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrumento_id INTEGER NOT NULL,
        volume_atual INTEGER NOT NULL,
        volume_solicitado INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pendente',
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (instrumento_id) REFERENCES instrumentos(id)
    )
    """)

    # Inserir instrumentos padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM instrumentos")
    total = cursor.fetchone()[0]
    if total == 0:
        instrumentos_iniciais = [
            ("Vocal", 60, 50, "João"),
            ("Guitarra", 70, 60, "Pedro"),
            ("Baixo", 65, 55, "Lucas"),
            ("Teclado", 50, 45, "Ana"),
            ("Bateria", 75, 70, "Carlos")
        ]
        cursor.executemany(
            "INSERT INTO instrumentos (nome, volume_atual, volume_auxiliar, musico) VALUES (?, ?, ?, ?)",
            instrumentos_iniciais
        )

    conn.commit()
    conn.close()

def listar_instrumentos():
    """Retorna uma lista com todos os instrumentos."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instrumentos ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def obter_instrumento(instrumento_id):
    """Retorna os dados de um instrumento pelo ID."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instrumentos WHERE id = ?", (instrumento_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def atualizar_volume_auxiliar(instrumento_id, novo_volume_aux):
    """Atualiza diretamente o volume do retorno auxiliar do instrumento."""
    novo_volume_aux = max(0, min(100, int(novo_volume_aux)))
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE instrumentos SET volume_auxiliar = ? WHERE id = ?",
        (novo_volume_aux, instrumento_id)
    )
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": "Volume do retorno auxiliar atualizado"}

def criar_solicitacao(instrumento_id, volume_solicitado):
    """
    Cria uma nova solicitação de alteração de volume para um instrumento.
    Valida limites de volume (0 a 100).
    """
    volume_solicitado = max(0, min(100, int(volume_solicitado)))

    inst = obter_instrumento(instrumento_id)
    if not inst:
        return {"sucesso": False, "mensagem": "Instrumento não encontrado"}

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO solicitacoes (instrumento_id, volume_atual, volume_solicitado, status)
        VALUES (?, ?, ?, 'pendente')
    """, (instrumento_id, inst["volume_atual"], volume_solicitado))
    
    solicitacao_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "sucesso": True,
        "mensagem": "Solicitação criada com sucesso",
        "solicitacao_id": solicitacao_id
    }

def listar_solicitacoes():
    """Retorna todas as solicitações com o nome do instrumento associado."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.instrumento_id, i.nome as instrumento, i.musico,
               s.volume_atual, s.volume_solicitado, s.status, s.data_hora
        FROM solicitacoes s
        JOIN instrumentos i ON s.instrumento_id = i.id
        ORDER BY s.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def aceitar_solicitacao(solicitacao_id):
    """
    Aceita uma solicitação pendente:
    1. Atualiza o volume do instrumento correspondente.
    2. Altera o status da solicitação para 'atendida'.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM solicitacoes WHERE id = ?", (solicitacao_id,))
    sol = cursor.fetchone()
    
    if not sol:
        conn.close()
        return {"sucesso": False, "mensagem": "Solicitação não encontrada"}
    
    if sol["status"] != "pendente":
        conn.close()
        return {"sucesso": False, "mensagem": f"Solicitação já está '{sol['status']}'"}

    cursor.execute(
        "UPDATE instrumentos SET volume_atual = ? WHERE id = ?",
        (sol["volume_solicitado"], sol["instrumento_id"])
    )
    
    cursor.execute(
        "UPDATE solicitacoes SET status = 'atendida' WHERE id = ?",
        (solicitacao_id,)
    )

    conn.commit()
    conn.close()

    return {"sucesso": True, "mensagem": "Solicitação atendida com sucesso"}

def recusar_solicitacao(solicitacao_id):
    """
    Recusa uma solicitação pendente:
    1. Altera o status da solicitação para 'recusada'.
    2. NÃO altera o volume do instrumento.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM solicitacoes WHERE id = ?", (solicitacao_id,))
    sol = cursor.fetchone()

    if not sol:
        conn.close()
        return {"sucesso": False, "mensagem": "Solicitação não encontrada"}

    if sol["status"] != "pendente":
        conn.close()
        return {"sucesso": False, "mensagem": f"Solicitação já está '{sol['status']}'"}

    cursor.execute(
        "UPDATE solicitacoes SET status = 'recusada' WHERE id = ?",
        (solicitacao_id,)
    )

    conn.commit()
    conn.close()

    return {"sucesso": True, "mensagem": "Solicitação recusada"}
