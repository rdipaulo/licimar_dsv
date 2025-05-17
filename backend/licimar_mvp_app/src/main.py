import sys
import os

# Adiciona o diretório pai de 'src' ao sys.path para permitir importações absolutas de 'src'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request # Adicionado jsonify e request
from src.models import db, Vendedor, Produto, Pedido, ItemPedido # Importar todos os modelos e db

app = Flask(__name__)

# Configuração do Banco de Dados (MySQL como no template, ou SQLite para simplicidade no MVP)
# Para MySQL (usando variáveis de ambiente como no template):
#app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'licimar_mvp_db')}"
# Para SQLite (mais simples para iniciar rapidamente, cria um arquivo licimar_mvp.db no diretório do projeto):
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'licimar_mvp.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Inicializa o db com a aplicação Flask

# Comando para criar o banco de dados e as tabelas (executar uma vez)
@app.cli.command("create-db")
def create_db_command():
    """Cria as tabelas do banco de dados."""
    with app.app_context(): # Garante que estamos no contexto da aplicação
        db.create_all()
    print("Banco de dados e tabelas criados!")

# Rota de exemplo para testar
@app.route('/')
def hello():
    return "Bem-vindo ao Backend da Licimar MVP!"

# Aqui começaremos a adicionar as rotas da API para o MVP
# Exemplo: Rota para adicionar um novo vendedor
@app.route('/api/vendedores', methods=['POST'])
def adicionar_vendedor():
    data = request.get_json()
    if not data or not 'nome' in data:
        return jsonify({'erro': 'Nome do vendedor é obrigatório'}), 400
    
    if Vendedor.query.filter_by(nome=data['nome']).first():
        return jsonify({'erro': 'Vendedor com este nome já existe'}), 409

    novo_vendedor = Vendedor(nome=data['nome'])
    db.session.add(novo_vendedor)
    db.session.commit()
    return jsonify({'id': novo_vendedor.id, 'nome': novo_vendedor.nome}), 201

@app.route('/api/vendedores', methods=['GET'])
def listar_vendedores():
    vendedores = Vendedor.query.all()
    return jsonify([{'id': v.id, 'nome': v.nome} for v in vendedores])

if __name__ == '__main__':
    # É importante rodar em 0.0.0.0 para ser acessível na rede local para testes em tablets/celulares
    app.run(host='0.0.0.0', port=5000, debug=True)


# Rotas para Produtos
@app.route("/api/produtos", methods=["POST"])
def adicionar_produto():
    data = request.get_json()
    if not data or not data.get("nome") or not data.get("preco_venda"):
        return jsonify({"erro": "Nome e preco_venda do produto são obrigatórios"}), 400

    # Validação adicional pode ser incluída aqui (ex: se o preço é um número)
    try:
        preco_venda = float(data["preco_venda"])
        estoque = int(data.get("estoque", 0))
    except ValueError:
        return jsonify({"erro": "preco_venda e estoque devem ser números"}), 400

    novo_produto = Produto(
        nome=data["nome"],
        preco_venda=preco_venda,
        estoque=estoque
    )
    db.session.add(novo_produto)
    db.session.commit()
    return jsonify({
        "id": novo_produto.id,
        "nome": novo_produto.nome,
        "preco_venda": float(novo_produto.preco_venda),
        "estoque": novo_produto.estoque
    }), 201

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    produtos = Produto.query.all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "preco_venda": float(p.preco_venda),
        "estoque": p.estoque
    } for p in produtos])



# Rotas para Pedidos e Itens do Pedido
@app.route("/api/pedidos/saida", methods=["POST"])
def registrar_saida_pedido():
    data = request.get_json()
    if not data or not data.get("vendedor_nome") or not data.get("itens_saida"):
        return jsonify({"erro": "Nome do vendedor e itens de saída são obrigatórios"}), 400

    vendedor = Vendedor.query.filter_by(nome=data["vendedor_nome"]).first()
    if not vendedor:
        return jsonify({"erro": f"Vendedor '{data['vendedor_nome']}' não encontrado."}), 404

    novo_pedido = Pedido(vendedor_id=vendedor.id, status="EM_ABERTO")
    db.session.add(novo_pedido)
    # Precisamos fazer um flush para obter o ID do novo_pedido antes de adicionar itens
    db.session.flush()

    itens_processados = []
    for item_data in data["itens_saida"]:
        produto = Produto.query.get(item_data.get("produto_id"))
        if not produto:
            db.session.rollback() # Desfaz o pedido se um produto não for encontrado
            return jsonify({"erro": f"Produto com ID {item_data.get('produto_id')} não encontrado."}), 404
        
        quantidade_saida = item_data.get("quantidade_saida", 0)
        if quantidade_saida <= 0:
            db.session.rollback()
            return jsonify({"erro": f"Quantidade de saída para o produto {produto.nome} deve ser maior que zero."}), 400

        if produto.estoque < quantidade_saida:
            db.session.rollback()
            return jsonify({"erro": f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.estoque}"}), 400

        novo_item_pedido = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade_saida=quantidade_saida,
            preco_venda_unitario_registrado=produto.preco_venda # Registra o preço no momento da saída
        )
        itens_processados.append(novo_item_pedido)
        produto.estoque -= quantidade_saida # Atualiza o estoque
        db.session.add(produto) # Adiciona a atualização do produto à sessão
    
    db.session.add_all(itens_processados)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao salvar o pedido: {str(e)}"}), 500

    return jsonify({
        "mensagem": "Saída de pedido registrada com sucesso!",
        "pedido_id": novo_pedido.id,
        "vendedor_nome": vendedor.nome,
        "status": novo_pedido.status
    }), 201



@app.route("/api/pedidos/<int:pedido_id>/fechamento", methods=["PUT"])
def registrar_fechamento_pedido(pedido_id):
    data = request.get_json()
    if not data or not data.get("itens_retorno_perda"):
        return jsonify({"erro": "Lista de itens de retorno/perda é obrigatória"}), 400

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": f"Pedido com ID {pedido_id} não encontrado."}), 404
    
    if pedido.status == "FECHADO":
        return jsonify({"erro": f"Pedido {pedido_id} já está fechado."}), 400

    valor_total_produtos_vendidos_calculado = 0
    valor_total_perdas_calculado = 0

    for item_data in data["itens_retorno_perda"]:
        item_pedido_id = item_data.get("item_pedido_id")
        if not item_pedido_id:
            return jsonify({"erro": "ID do item_pedido é obrigatório para cada item."}), 400

        item_pedido = ItemPedido.query.filter_by(id=item_pedido_id, pedido_id=pedido.id).first()
        if not item_pedido:
            db.session.rollback()
            return jsonify({"erro": f"Item de pedido com ID {item_pedido_id} não encontrado para o pedido {pedido.id}."}), 404

        quantidade_retorno = item_data.get("quantidade_retorno", 0)
        quantidade_perda = item_data.get("quantidade_perda", 0)

        if quantidade_retorno < 0 or quantidade_perda < 0:
            db.session.rollback()
            return jsonify({"erro": "Quantidades de retorno e perda não podem ser negativas."}), 400

        if (quantidade_retorno + quantidade_perda) > item_pedido.quantidade_saida:
            db.session.rollback()
            return jsonify({
                "erro": f"Soma de retorno ({quantidade_retorno}) e perda ({quantidade_perda}) para o produto {item_pedido.produto.nome} excede a quantidade de saída ({item_pedido.quantidade_saida})."
            }), 400

        item_pedido.quantidade_retorno = quantidade_retorno
        item_pedido.quantidade_perda = quantidade_perda
        
        # Atualiza estoque do produto que retornou em bom estado
        produto = Produto.query.get(item_pedido.produto_id)
        if produto and quantidade_retorno > 0:
            produto.estoque += quantidade_retorno
            db.session.add(produto)

        # Calcula valor vendido e valor de perda para este item
        quantidade_vendida_item = item_pedido.quantidade_saida - item_pedido.quantidade_retorno - item_pedido.quantidade_perda
        if quantidade_vendida_item < 0: # Segurança, não deveria acontecer se a validação acima estiver correta
            quantidade_vendida_item = 0
            
        valor_total_produtos_vendidos_calculado += quantidade_vendida_item * item_pedido.preco_venda_unitario_registrado
        valor_total_perdas_calculado += item_pedido.quantidade_perda * item_pedido.preco_venda_unitario_registrado # Assumindo que a perda é cobrada pelo preço de venda

        db.session.add(item_pedido)

    pedido.valor_total_produtos_vendidos = valor_total_produtos_vendidos_calculado
    pedido.valor_total_perdas = valor_total_perdas_calculado
    # Simplificando: não estamos incluindo gelo seco neste MVP inicial para o cálculo do valor_total_a_pagar
    pedido.valor_total_a_pagar = pedido.valor_total_produtos_vendidos + pedido.valor_total_perdas
    pedido.status = "FECHADO"
    db.session.add(pedido)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao fechar o pedido: {str(e)}"}), 500

    return jsonify({
        "mensagem": f"Pedido {pedido_id} fechado com sucesso!",
        "pedido_id": pedido.id,
        "status": pedido.status,
        "valor_total_a_pagar": float(pedido.valor_total_a_pagar)
    }), 200



# Rota para listar todos os pedidos (ou filtrar por status)
@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    status_filtro = request.args.get("status")
    query = Pedido.query
    if status_filtro:
        query = query.filter(Pedido.status == status_filtro)
    
    pedidos = query.order_by(Pedido.data_operacao.desc()).all()
    
    resultado = []
    for p in pedidos:
        # Para simplificar, vamos buscar o nome do vendedor aqui. Em um sistema maior, poderia ser um join mais otimizado.
        vendedor = Vendedor.query.get(p.vendedor_id)
        resultado.append({
            "id": p.id,
            "vendedor_id": p.vendedor_id,
            "vendedor_nome": vendedor.nome if vendedor else "N/A",
            "data_operacao": p.data_operacao.isoformat(),
            "status": p.status,
            "valor_total_a_pagar": float(p.valor_total_a_pagar) if p.valor_total_a_pagar else None
        })
    return jsonify(resultado)

# Rota para listar os itens de um pedido específico
@app.route("/api/pedidos/<int:pedido_id>/itens", methods=["GET"])
def listar_itens_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"erro": f"Pedido com ID {pedido_id} não encontrado."}), 404

    itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
    resultado = []
    for item in itens:
        produto = Produto.query.get(item.produto_id)
        resultado.append({
            "id": item.id,
            "pedido_id": item.pedido_id,
            "produto_id": item.produto_id,
            "produto_nome": produto.nome if produto else "N/A",
            "quantidade_saida": item.quantidade_saida,
            "quantidade_retorno": item.quantidade_retorno,
            "quantidade_perda": item.quantidade_perda,
            "preco_venda_unitario_registrado": float(item.preco_venda_unitario_registrado)
        })
    return jsonify(resultado)

