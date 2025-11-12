#!/usr/bin/env python3
"""
Script standalone para criar o banco de dados SQLite e suas tabelas
usando a biblioteca nativa sqlite3, evitando problemas de permissão com SQLAlchemy
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'licimar_dev.db')

def create_database():
    """Cria o banco de dados e todas as tabelas necessárias"""
    
    # Criar diretório instance se não existir
    instance_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"✓ Diretório {instance_dir} criado")
    
    # Remover banco de dados existente se houver
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"✓ Banco de dados existente removido")
    
    # Conectar ao banco de dados (será criado se não existir)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"✓ Banco de dados criado em: {DB_PATH}")
    
    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'operador',
            active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Tabela 'users' criada")
    
    # Criar tabela de ambulantes
    cursor.execute('''
        CREATE TABLE ambulantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE,
            telefone VARCHAR(20),
            cpf VARCHAR(14) UNIQUE,
            endereco TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Tabela 'ambulantes' criada")
    
    # Criar tabela de categorias
    cursor.execute('''
        CREATE TABLE categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) UNIQUE NOT NULL,
            descricao TEXT,
            active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Tabela 'categorias' criada")
    
    # Criar tabela de produtos
    cursor.execute('''
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            preco DECIMAL(10, 2) NOT NULL,
            estoque INTEGER NOT NULL DEFAULT 0,
            categoria_id INTEGER,
            imagem_url VARCHAR(255),
            descricao TEXT,
            active BOOLEAN NOT NULL DEFAULT 1,
            estoque_minimo INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    ''')
    print("✓ Tabela 'produtos' criada")
    
    # Criar tabela de regras de cobrança
    cursor.execute('''
        CREATE TABLE regras_cobranca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faixa_inicial DECIMAL(10, 2) NOT NULL,
            faixa_final DECIMAL(10, 2) NOT NULL,
            percentual DECIMAL(5, 2) NOT NULL,
            descricao VARCHAR(255),
            active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Tabela 'regras_cobranca' criada")
    
    # Criar tabela de pedidos
    cursor.execute('''
        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ambulante_id INTEGER NOT NULL,
            data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL DEFAULT 'saida',
            total DECIMAL(10, 2) DEFAULT 0,
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ambulante_id) REFERENCES ambulantes(id)
        )
    ''')
    print("✓ Tabela 'pedidos' criada")
    
    # Criar tabela de itens de pedido
    cursor.execute('''
        CREATE TABLE itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade_saida DECIMAL(10, 3) NOT NULL DEFAULT 0,
            quantidade_retorno DECIMAL(10, 3) NOT NULL DEFAULT 0,
            preco_unitario DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    print("✓ Tabela 'itens_pedido' criada")
    
    # Criar tabela de logs
    cursor.execute('''
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(100) NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✓ Tabela 'logs' criada")
    
    # Criar índices para melhor performance
    cursor.execute('CREATE INDEX idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX idx_ambulantes_cpf ON ambulantes(cpf)')
    cursor.execute('CREATE INDEX idx_produtos_categoria ON produtos(categoria_id)')
    cursor.execute('CREATE INDEX idx_pedidos_ambulante ON pedidos(ambulante_id)')
    cursor.execute('CREATE INDEX idx_itens_pedido_pedido ON itens_pedido(pedido_id)')
    cursor.execute('CREATE INDEX idx_itens_pedido_produto ON itens_pedido(produto_id)')
    cursor.execute('CREATE INDEX idx_logs_user ON logs(user_id)')
    print("✓ Índices criados")
    
    # Commit e fechar conexão
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados criado com sucesso!")
    return DB_PATH

def populate_initial_data():
    """Popula o banco de dados com dados iniciais"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📝 Populando dados iniciais...")
    
    # Inserir usuário admin
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@licimar.com', admin_password, 'admin', 1))
    print("✓ Usuário admin criado (username: admin, senha: admin123)")
    
    # Inserir usuário operador
    operador_password = generate_password_hash('operador123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('operador', 'operador@licimar.com', operador_password, 'operador', 1))
    print("✓ Usuário operador criado (username: operador, senha: operador123)")
    
    # Inserir categorias
    categorias = [
        ('Bebidas', 'Bebidas geladas e quentes'),
        ('Sorvetes', 'Sorvetes e picolés'),
        ('Gelo', 'Gelo em barra e seco'),
        ('Snacks', 'Salgadinhos e petiscos'),
        ('Doces', 'Balas, chocolates e doces')
    ]
    cursor.executemany('INSERT INTO categorias (nome, descricao) VALUES (?, ?)', categorias)
    print(f"✓ {len(categorias)} categorias criadas")
    
    # Inserir produtos
    produtos = [
        ('Água Mineral 500ml', 2.50, 100, 1, None, 'Água mineral natural', 1, 20),
        ('Refrigerante Lata', 4.00, 80, 1, None, 'Refrigerante em lata 350ml', 1, 15),
        ('Suco Natural', 5.00, 50, 1, None, 'Suco natural de frutas', 1, 10),
        ('Picolé Frutas', 3.00, 120, 2, None, 'Picolé de frutas variadas', 1, 30),
        ('Sorvete Pote', 8.00, 40, 2, None, 'Sorvete em pote 500ml', 1, 10),
        ('Gelo Barra 5kg', 10.00, 60, 3, None, 'Gelo em barra de 5kg', 1, 15),
        ('Gelo Seco 1kg', 15.00, 30, 3, None, 'Gelo seco para conservação', 1, 10),
        ('Salgadinho', 3.50, 90, 4, None, 'Salgadinho pacote 100g', 1, 20),
        ('Amendoim', 4.50, 70, 4, None, 'Amendoim torrado 150g', 1, 15),
        ('Chocolate Barra', 5.50, 60, 5, None, 'Chocolate ao leite 100g', 1, 15)
    ]
    cursor.executemany('''
        INSERT INTO produtos (nome, preco, estoque, categoria_id, imagem_url, descricao, active, estoque_minimo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', produtos)
    print(f"✓ {len(produtos)} produtos criados")
    
    # Inserir ambulantes
    ambulantes = [
        ('João Silva', 'joao.silva@email.com', '(11) 98765-4321', '123.456.789-00', 'Rua A, 123', 'ativo'),
        ('Maria Santos', 'maria.santos@email.com', '(11) 98765-4322', '234.567.890-11', 'Rua B, 456', 'ativo'),
        ('Pedro Oliveira', 'pedro.oliveira@email.com', '(11) 98765-4323', '345.678.901-22', 'Rua C, 789', 'ativo'),
        ('Ana Costa', 'ana.costa@email.com', '(11) 98765-4324', '456.789.012-33', 'Rua D, 321', 'ativo'),
        ('Carlos Souza', 'carlos.souza@email.com', '(11) 98765-4325', '567.890.123-44', 'Rua E, 654', 'inativo')
    ]
    cursor.executemany('''
        INSERT INTO ambulantes (nome, email, telefone, cpf, endereco, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ambulantes)
    print(f"✓ {len(ambulantes)} ambulantes criados")
    
    # Inserir regras de cobrança
    regras = [
        (0, 100, 0, 'Sem desconto para dívidas até R$ 100'),
        (100.01, 500, 5, '5% de desconto para dívidas entre R$ 100 e R$ 500'),
        (500.01, 1000, 10, '10% de desconto para dívidas entre R$ 500 e R$ 1000'),
        (1000.01, 999999, 15, '15% de desconto para dívidas acima de R$ 1000')
    ]
    cursor.executemany('''
        INSERT INTO regras_cobranca (faixa_inicial, faixa_final, percentual, descricao)
        VALUES (?, ?, ?, ?)
    ''', regras)
    print(f"✓ {len(regras)} regras de cobrança criadas")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Dados iniciais populados com sucesso!")

if __name__ == '__main__':
    print("=" * 60)
    print("INICIALIZAÇÃO DO BANCO DE DADOS LICIMAR MVP")
    print("=" * 60)
    
    db_path = create_database()
    populate_initial_data()
    
    print("\n" + "=" * 60)
    print(f"Banco de dados pronto em: {db_path}")
    print("=" * 60)
