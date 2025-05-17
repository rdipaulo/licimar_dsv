from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Configuração CORS mais permissiva

# Dados dos vendedores
vendedores = [
    {"id": 1, "nome": "Ivan Magé"},
    {"id": 2, "nome": "Roberto Peixoto"},
    {"id": 3, "nome": "Sabino"}
]

# Dados dos produtos
produtos = [
    {"id": 1, "nome": "Picolé Chicabon", "preco_venda": 8.0, "estoque": 100},
    {"id": 2, "nome": "Picolé Tablito", "preco_venda": 10.0, "estoque": 80},
    {"id": 3, "nome": "Sorvete Magnun - classico", "preco_venda": 17.0, "estoque": 50},
    {"id": 4, "nome": "Gelo Seco (kg)", "preco_venda": 28.0, "estoque": 200}
]

# Armazenar pedidos em memória
pedidos = []
ultimo_id_pedido = 0

@app.route('/api/vendedores', methods=['GET'])
def get_vendedores():
    return jsonify(vendedores)

@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    return jsonify(produtos)

@app.route('/api/pedidos/saida', methods=['POST'])
def criar_pedido_saida():
    global ultimo_id_pedido
    
    try:
        # Imprimir os dados recebidos para debug
        print("Dados recebidos:", request.data)
        
        # Obter dados do pedido do corpo da requisição
        dados_pedido = request.json
        print("Dados do pedido:", dados_pedido)
        
        # Verificações mais flexíveis
        if not dados_pedido:
            return jsonify({"message": "Dados do pedido não fornecidos"}), 400
            
        # Extrair vendedor_nome e itens_saida com verificações de segurança
        vendedor_nome = dados_pedido.get('vendedor_nome')
        itens_saida = dados_pedido.get('itens_saida', [])
        
        if not vendedor_nome:
            return jsonify({"message": "Vendedor não selecionado"}), 400
            
        if not itens_saida:
            return jsonify({"message": "Nenhum item adicionado ao pedido"}), 400
        
        # Encontrar o ID do vendedor pelo nome
        vendedor = next((v for v in vendedores if v['nome'] == vendedor_nome), None)
        if not vendedor:
            return jsonify({"message": f"Vendedor '{vendedor_nome}' não encontrado"}), 400
            
        vendedor_id = vendedor['id']
        
        # Incrementar o ID do pedido
        ultimo_id_pedido += 1
        
        # Criar novo pedido
        novo_pedido = {
            "id": ultimo_id_pedido,
            "vendedor_id": vendedor_id,
            "vendedor_nome": vendedor_nome,
            "data_operacao": datetime.now().isoformat(),
            "status": "saida",
            "itens": []
        }
        
        # Adicionar itens ao pedido
        for item in itens_saida:
            produto_id = item.get('produto_id')
            quantidade_saida = item.get('quantidade_saida', 0)
            
            if produto_id and quantidade_saida > 0:
                novo_pedido["itens"].append({
                    "produto_id": produto_id,
                    "quantidade_saida": quantidade_saida,
                    "quantidade_retorno": 0
                })
        
        # Adicionar pedido à lista
        pedidos.append(novo_pedido)
        
        print("Pedido criado com sucesso:", novo_pedido)
        
        return jsonify({
            "message": "Pedido de saída registrado com sucesso",
            "pedido_id": novo_pedido["id"]
        }), 201
    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        # Retornar uma mensagem de erro mais descritiva
        return jsonify({"message": f"Erro ao processar pedido: {str(e)}"}), 500

@app.route('/api/pedidos/retorno', methods=['POST'])
def registrar_retorno():
    try:
        # Obter dados do retorno
        dados_retorno = request.json
        
        # Verificar se há um pedido_id
        if not dados_retorno or 'pedido_id' not in dados_retorno:
            return jsonify({"message": "ID do pedido não fornecido"}), 400
        
        # Encontrar o pedido correspondente
        pedido_id = dados_retorno['pedido_id']
        pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
        
        if not pedido:
            return jsonify({"message": f"Pedido com ID {pedido_id} não encontrado"}), 404
        
        # Atualizar status do pedido
        pedido['status'] = 'retorno'
        
        # Atualizar quantidades de retorno (sem perda)
        for item_retorno in dados_retorno.get('itens', []):
            for item_pedido in pedido['itens']:
                if item_pedido['produto_id'] == item_retorno.get('produto_id'):
                    item_pedido['quantidade_retorno'] = item_retorno.get('quantidade_retorno', 0)
        
        # Calcular valor total
        valor_total = 0
        for item in pedido['itens']:
            produto = next((p for p in produtos if p['id'] == item['produto_id']), None)
            if produto:
                quantidade_vendida = item['quantidade_saida'] - item['quantidade_retorno']
                valor_total += quantidade_vendida * float(produto['preco_venda'])
        
        return jsonify({
            "message": "Retorno registrado com sucesso",
            "pedido_id": pedido_id,
            "valor_total": valor_total
        }), 200
    except Exception as e:
        print(f"Erro ao processar retorno: {e}")
        return jsonify({"message": f"Erro ao processar retorno: {str(e)}"}), 500

@app.route('/api/pedidos/<int:pedido_id>/itens', methods=['GET'])
def get_pedido_itens(pedido_id):
    # Encontrar o pedido pelo ID
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    
    if not pedido:
        # Se não encontrar o pedido, retornar erro 404
        return jsonify({"message": "Pedido não encontrado"}), 404
    
    # Preparar a lista de itens com informações completas
    itens_completos = []
    for item in pedido.get('itens', []):
        produto_id = item.get('produto_id')
        produto = next((p for p in produtos if p['id'] == produto_id), None)
        
        if produto:
            itens_completos.append({
                "id": produto_id,
                "nome": produto.get('nome', ''),
                "preco_venda": float(produto.get('preco_venda', 0.0)),  # Garantir que é um número
                "quantidade_saida": item.get('quantidade_saida', 0),
                "quantidade_retorno": item.get('quantidade_retorno', 0)
            })
    
    return jsonify(itens_completos)

@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    return jsonify(pedidos)

if __name__ == '__main__':
    app.run(debug=True)
