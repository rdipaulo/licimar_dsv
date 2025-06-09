# Script Simples para Configurar o Banco Licimar - SEM DEPENDÊNCIAS COMPLEXAS
# Este script cria o banco diretamente via SQL para evitar problemas de relacionamento

import sqlite3
import os
from werkzeug.security import generate_password_hash

def main():
    print("=== CONFIGURAÇÃO SIMPLES DO BANCO LICIMAR ===")
    
    # Caminho do banco de dados
    db_path = os.path.join(os.getcwd(), 'src', 'licimar.db')
    print(f"Banco de dados: {db_path}")
    
    # Conecta ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Cria tabela de usuários se não existir
        print("\n1. Configurando tabela de usuários...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifica se admin já existe
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Cria usuário admin
            password_hash = generate_password_hash("admin123")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, active)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@licimar.com', password_hash, 'admin', 1))
            print("✓ Usuário admin criado!")
        else:
            print("✓ Usuário admin já existe!")
        
        # 2. Cria tabela de vendedores
        print("\n2. Configurando tabela de vendedores...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(120),
                telefone VARCHAR(20),
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifica se vendedores já existem
        cursor.execute("SELECT COUNT(*) FROM vendedores")
        if cursor.fetchone()[0] == 0:
            vendedores = [
                ('Ivan Magé', 'ivan@licimar.com', '11987654321'),
                ('Roberto Peixoto', 'roberto@licimar.com', '11912345678'),
                ('Sabino', 'sabino@licimar.com', '11998765432')
            ]
            cursor.executemany('''
                INSERT INTO vendedores (nome, email, telefone)
                VALUES (?, ?, ?)
            ''', vendedores)
            print(f"✓ {len(vendedores)} vendedores adicionados!")
        else:
            print("✓ Vendedores já existem!")
        
        # 3. Cria tabela de produtos
        print("\n3. Configurando tabela de produtos...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                preco_venda DECIMAL(10,2) NOT NULL,
                estoque INTEGER DEFAULT 0,
                categoria VARCHAR(50),
                imagem_url VARCHAR(255),
                descricao TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifica se produtos já existem
        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            produtos = [
                # (nome, preco_venda, estoque, categoria, imagem_url)
                ('Picolé Chicabon', 8.00, 100, 'Picolés', '/assets/images/chicabon.avif'),
                ('Picolé Chicabon Zero', 8.50, 80, 'Picolés', '/assets/images/chicabon_zero.avif'),
                ('Sorvete Magnum Amêndoas', 17.00, 50, 'Sorvetes Premium', '/assets/images/magnum_amendoas.jpeg'),
                ('Picolé Fruttare Morango', 6.50, 120, 'Picolés de Fruta', '/assets/images/fruttare_morango.jpeg'),
                ('Picolé Fruttare Abacaxi', 6.50, 100, 'Picolés de Fruta', '/assets/images/fruttare_abacaxi.jpeg'),
                ('Picolé Fruttare Coco', 6.50, 90, 'Picolés de Fruta', '/assets/images/fruttare_coco.avif'),
                ('Picolé Fruttare Limão', 6.50, 110, 'Picolés de Fruta', '/assets/images/fruttare_limao.avif'),
                ('Picolé Fruttare Uva', 6.50, 95, 'Picolés de Fruta', '/assets/images/fruttare_uva.avif'),
                ('Cone Crocante Nestlé', 12.00, 60, 'Cones', '/assets/images/cone_crocante_nestle.jpeg'),
                ('Cone KitKat', 14.00, 45, 'Cones', '/assets/images/cone_kitkat.jpeg'),
                ('Cornetto Brigadeiro', 13.00, 55, 'Cones', '/assets/images/cornetto_brigadeiro.jpeg'),
                ('Cornetto Crocante', 13.00, 50, 'Cones', '/assets/images/cornetto_crocante.avif'),
                ('Cornetto M&Ms', 15.00, 40, 'Cones', '/assets/images/cornetto_mms.avif'),
                ('Eskibon Clássico', 9.00, 70, 'Picolés Premium', '/assets/images/eskibon_classico.avif'),
                ('Diamante Negro', 11.00, 35, 'Picolés Premium', '/assets/images/diamante_negro.jpeg'),
                ('Brigadeiro', 10.00, 65, 'Picolés Premium', '/assets/images/brigadeiro.avif'),
                ('LaFrutta Coco', 7.50, 85, 'Sorvetes de Leite', '/assets/images/lafrutta_coco.jpeg'),
                ('LaFrutta Manga', 7.50, 80, 'Sorvetes de Leite', '/assets/images/lafrutta_manga.jpeg'),
                ('LaFrutta Maracujá com Leite', 7.50, 75, 'Sorvetes de Leite', '/assets/images/lafrutta_maracuja_leite.jpeg'),
                ('LaFrutta Morango com Leite', 7.50, 90, 'Sorvetes de Leite', '/assets/images/lafrutta_morango_leite.jpeg'),
                ('Baton', 5.50, 150, 'Chocolates', '/assets/images/baton.jpeg'),
                ('Bombom Garoto', 4.50, 200, 'Chocolates', '/assets/images/bombom_garoto.jpeg'),
                ('Laka Oreo', 12.00, 40, 'Chocolates', '/assets/images/laka_oreo.jpeg'),
                ('Leite Moça', 9.50, 60, 'Especiais', '/assets/images/leite_moca.jpeg'),
                ('Gelo Seco (kg)', 28.00, 200, 'Outros', '/assets/images/gelo_seco.jpeg'),
                ('Chambinho', 6.00, 120, 'Picolés', '/assets/images/chambinho.jpeg'),
                ('Caribe', 7.00, 100, 'Picolés', '/assets/images/caribe.jpeg'),
                ('Frutilly', 8.50, 75, 'Picolés de Fruta', '/assets/images/frutilly.avif'),
                ('Fini Dentadura', 3.50, 180, 'Doces', '/assets/images/fini_dentadura.jpeg'),
                ('Fini Tube Morango', 4.00, 160, 'Doces', '/assets/images/fini_tube_morango.jpeg'),
                ('Fini Tube Tutti-Frutti', 4.00, 160, 'Doces', '/assets/images/fini_tube_tuttifruti.jpeg'),
            ]
            
            cursor.executemany('''
                INSERT INTO produtos (nome, preco_venda, estoque, categoria, imagem_url)
                VALUES (?, ?, ?, ?, ?)
            ''', produtos)
            print(f"✓ {len(produtos)} produtos adicionados!")
        else:
            print("✓ Produtos já existem!")
        
        # 4. Cria outras tabelas necessárias
        print("\n4. Criando tabelas auxiliares...")
        
        # Tabela de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendedor_id INTEGER,
                data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pendente',
                total DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendedor_id) REFERENCES vendedores (id)
            )
        ''')
        
        # Tabela de itens do pedido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto_id INTEGER,
                quantidade INTEGER NOT NULL,
                preco_unitario DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        
        # Tabela de logs (opcional, para evitar erros)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Confirma todas as alterações
        conn.commit()
        
        # Verifica os dados criados
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendedores")
        vendedores_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos_count = cursor.fetchone()[0]
        
        print("\n=== CONFIGURAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print(f"\nDados criados:")
        print(f"- {users_count} usuário(s)")
        print(f"- {vendedores_count} vendedor(es)")
        print(f"- {produtos_count} produto(s)")
        
        print(f"\nBanco de dados: {db_path}")
        print("\nPara acessar o sistema:")
        print("1. python src/main.py")
        print("2. Acesse: http://localhost:5173")
        print("3. Login: admin / admin123")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()

