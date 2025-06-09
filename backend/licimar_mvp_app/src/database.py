import os
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, inspect
from werkzeug.security import generate_password_hash

# Classe base para nossos modelos (tabelas)
class Base(DeclarativeBase):
    pass

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Função para configurar e inicializar o banco de dados com o app Flask
def init_db(app):
    # Define o caminho para o arquivo do banco de dados SQLite
    # Ele será criado dentro da pasta 'src'
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'licimar.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desativa rastreamento desnecessário
    
    # Associa a instância do db com o app Flask
    db.init_app(app)
    
    # Cria as tabelas no banco de dados (se não existirem)
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        print("Tabelas criadas (ou já existentes).")
        # Tenta migrar os dados do JSON na primeira vez
        migrate_json_to_db(app)

# Função para migrar dados do JSON para o SQLite (executa apenas se o DB estiver vazio)
def migrate_json_to_db(app):
    # Importa os modelos aqui para evitar dependência circular
    from src.models.user import User
    from src.models.vendedor import Vendedor
    from src.models.produto import Produto
    from src.models.pedido import Pedido
    from src.models.item_pedido import ItemPedido

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'licimar_db.json')
    
    if not os.path.exists(json_path):
        print(f"Arquivo JSON 'licimar_db.json' não encontrado em {os.path.dirname(json_path)}. Nenhuma migração de dados será feita.")
        # Cria usuário admin padrão se não houver JSON e nenhum usuário existir
        with app.app_context():  # Certifique-se de que isso está aqui
            try:
                if User.query.count() == 0:
                    print("Criando usuário admin padrão...")
                    admin = User(
                        username="admin",
                        email="admin@licimar.com",
                        password_hash=generate_password_hash("admin123"),
                        role="admin",
                        active=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("Usuário admin padrão criado.")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao criar usuário admin: {e}")
        return


    with app.app_context():
        # Verifica se o banco já tem dados (ex: na tabela vendedores)
        if Vendedor.query.count() > 0:
            print("Banco de dados já populado. Migração do JSON ignorada.")
            return
        
        print(f"Iniciando migração do arquivo: {json_path}")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erro ao ler o arquivo JSON: {e}")
            return

        # Migrar Vendedores
        print("Migrando vendedores...")
        vendedores_map = {} # Para mapear ID antigo para novo ID (se necessário)
        for v_data in data.get('vendedores', []):
            vendedor = Vendedor(
                # id=v_data['id'], # Deixe o DB gerar o ID
                nome=v_data['nome'],
                active=True # Assume que todos estão ativos inicialmente
            )
            db.session.add(vendedor)
        db.session.flush() # Garante que os IDs sejam gerados antes de usá-los
        for v_obj in Vendedor.query.all():
             # Aqui você poderia mapear IDs antigos se precisasse, mas para este caso não é crucial
             pass 
        print(f"{Vendedor.query.count()} vendedores migrados.")

        # Migrar Produtos
        print("Migrando produtos...")
        produtos_map = {} # Mapear ID antigo para novo objeto Produto
        for p_data in data.get('produtos', []):
            produto = Produto(
                # id=p_data['id'],
                nome=p_data['nome'],
                preco_venda=p_data['preco_venda'],
                estoque=p_data['estoque'],
                # imagem_url, descricao, categoria podem ser adicionados se existirem no JSON
                active=True
            )
            db.session.add(produto)
        db.session.flush()
        for p_obj in Produto.query.all():
            # Encontra o produto correspondente no JSON pelo nome (ou outro campo único)
            p_data_original = next((p for p in data.get('produtos', []) if p['nome'] == p_obj.nome), None)
            if p_data_original:
                produtos_map[p_data_original['id']] = p_obj # Mapeia ID antigo para objeto novo
        print(f"{Produto.query.count()} produtos migrados.")

        # Criar usuário admin padrão ANTES de migrar pedidos (se não existir)
        if User.query.count() == 0:
            print("Criando usuário admin padrão...")
            admin = User(
                username="admin",
                email="admin@licimar.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                active=True
            )
            db.session.add(admin)
            db.session.flush() # Garante que o admin tenha um ID
            admin_user_id = admin.id
            print("Usuário admin padrão criado.")
        else:
            admin_user_id = User.query.filter_by(role='admin').first().id

        # Migrar Pedidos e Itens de Pedido
        print("Migrando pedidos e itens...")
        for pedido_data in data.get('pedidos', []):
            # Encontra o vendedor correspondente pelo nome (ou mapeamento de ID se feito)
            vendedor_obj = Vendedor.query.filter_by(nome=next((v['nome'] for v in data.get('vendedores', []) if v['id'] == pedido_data['vendedor_id']), None)).first()
            if not vendedor_obj:
                print(f"AVISO: Vendedor com ID {pedido_data['vendedor_id']} não encontrado para o pedido {pedido_data['id']}. Pedido ignorado.")
                continue
            
            try:
                data_op = datetime.fromisoformat(pedido_data['data_operacao'])
            except ValueError:
                print(f"AVISO: Formato de data inválido para pedido {pedido_data['id']}: {pedido_data['data_operacao']}. Usando data atual.")
                data_op = datetime.utcnow()

            pedido = Pedido(
                # id=pedido_data['id'],
                vendedor_id=vendedor_obj.id, # Usa o ID do objeto Vendedor encontrado
                data_operacao=data_op,
                status=pedido_data['status'],
                created_by=admin_user_id # Associa ao admin padrão
                # valor_total_a_pagar será calculado depois ou deixado nulo
            )
            db.session.add(pedido)
            db.session.flush() # Garante que o pedido tenha um ID

            # Migrar Itens do Pedido
            for item_data in pedido_data.get('itens', []):
                produto_obj = produtos_map.get(item_data['produto_id']) # Usa o mapeamento de ID antigo para objeto novo
                if not produto_obj:
                    print(f"AVISO: Produto com ID {item_data['produto_id']} não encontrado para item do pedido {pedido_data['id']}. Item ignorado.")
                    continue

                item_pedido = ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=produto_obj.id,
                    quantidade_saida=item_data['quantidade_saida'],
                    quantidade_retorno=item_data.get('quantidade_retorno', 0),
                    quantidade_perda=0, # Assumindo 0 inicialmente
                    preco_venda_unitario_registrado=produto_obj.preco_venda # Pega o preço atual do produto
                )
                db.session.add(item_pedido)
        
        # Commit final
        try:
            db.session.commit()
            print("Migração do JSON concluída com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro durante o commit da migração: {e}")

# Listener para atualizar 'updated_at' automaticamente
@event.listens_for(db.session, 'before_flush')
def before_flush(session, flush_context, instances):
    for instance in session.dirty:
        if not hasattr(instance, 'updated_at'): continue
        # Verifica se o objeto tem um estado persistido (já existe no DB)
        if not inspect(instance).persistent: continue 
        instance.updated_at = datetime.utcnow()
    for instance in session.deleted:
        # Pode adicionar lógica para lidar com exclusões se necessário
        pass
