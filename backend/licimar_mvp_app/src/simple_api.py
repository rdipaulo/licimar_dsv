from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os
import traceback

app = Flask(__name__)
# Configuração CORS mais explícita para garantir acesso de qualquer origem
CORS(app, origins=["*"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Caminho para o arquivo de banco de dados
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'licimar_db.json')

# Dados iniciais
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

# Função para verificar se um produto é gelo seco
def is_gelo_seco(produto_id):
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if produto:
        return "gelo" in produto['nome'].lower()
    return False

# Função para carregar dados do arquivo
def carregar_dados():
    global vendedores, produtos, pedidos, ultimo_id_pedido
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                vendedores = data.get('vendedores', vendedores)
                produtos = data.get('produtos', produtos)
                pedidos = data.get('pedidos', pedidos)
                ultimo_id_pedido = data.get('ultimo_id_pedido', ultimo_id_pedido)
            print(f"Dados carregados com sucesso de {DB_FILE}")
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            # Não interrompe a execução, continua com os dados padrão

# Função para salvar dados no arquivo
def salvar_dados():
    try:
        with open(DB_FILE, 'w') as f:
            json.dump({
                'vendedores': vendedores,
                'produtos': produtos,
                'pedidos': pedidos,
                'ultimo_id_pedido': ultimo_id_pedido
            }, f, indent=2)
        print(f"Dados salvos com sucesso em {DB_FILE}")
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

# Adicionar cabeçalhos CORS a todas as respostas
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Carregar dados ao iniciar o aplicativo
try:
    carregar_dados()
except Exception as e:
    print(f"Erro ao inicializar dados: {e}")
    # Continua com os dados padrão

@app.route('/api/vendedores', methods=['GET'])
def get_vendedores():
    try:
        return jsonify(vendedores)
    except Exception as e:
        print(f"Erro ao buscar vendedores: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    try:
        return jsonify(produtos)
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
            
            # Converter para float para garantir precisão decimal, especialmente para gelo seco
            if is_gelo_seco(produto_id):
                try:
                    quantidade_saida = float(quantidade_saida)
                except (ValueError, TypeError):
                    quantidade_saida = 0.0
            else:
                try:
                    quantidade_saida = int(float(quantidade_saida))
                except (ValueError, TypeError):
                    quantidade_saida = 0
            
            if produto_id and quantidade_saida > 0:
                novo_pedido["itens"].append({
                    "produto_id": produto_id,
                    "quantidade_saida": quantidade_saida,
                    "quantidade_retorno": 0
                })
        
        # Adicionar pedido à lista
        pedidos.append(novo_pedido)
        
        # Salvar dados no arquivo
        salvar_dados()
        
        print("Pedido criado com sucesso:", novo_pedido)
        
        return jsonify({
            "message": "Pedido de saída registrado com sucesso",
            "pedido_id": novo_pedido["id"]
        }), 201
    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        traceback.print_exc()
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
        
        # Atualizar quantidades de retorno
        for item_retorno in dados_retorno.get('itens', []):
            produto_id = item_retorno.get('produto_id')
            quantidade_retorno = item_retorno.get('quantidade_retorno', 0)
            
            # Converter para float para garantir precisão decimal, especialmente para gelo seco
            if is_gelo_seco(produto_id):
                try:
                    quantidade_retorno = float(quantidade_retorno)
                except (ValueError, TypeError):
                    quantidade_retorno = 0.0
            else:
                try:
                    quantidade_retorno = int(float(quantidade_retorno))
                except (ValueError, TypeError):
                    quantidade_retorno = 0
            
            for item_pedido in pedido['itens']:
                if item_pedido['produto_id'] == produto_id:
                    item_pedido['quantidade_retorno'] = quantidade_retorno
        
        # Calcular valor total
        valor_total = 0
        for item in pedido['itens']:
            produto = next((p for p in produtos if p['id'] == item['produto_id']), None)
            if produto:
                quantidade_vendida = float(item['quantidade_saida']) - float(item['quantidade_retorno'])
                valor_total += quantidade_vendida * float(produto['preco_venda'])
        
        # Salvar dados no arquivo
        salvar_dados()
        
        return jsonify({
            "message": "Retorno registrado com sucesso",
            "pedido_id": pedido_id,
            "valor_total": valor_total
        }), 200
    except Exception as e:
        print(f"Erro ao processar retorno: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro ao processar retorno: {str(e)}"}), 500

@app.route('/api/pedidos/<int:pedido_id>/itens', methods=['GET'])
def get_pedido_itens(pedido_id):
    try:
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
                # Calcular quantidade vendida
                quantidade_saida = float(item.get('quantidade_saida', 0))
                quantidade_retorno = float(item.get('quantidade_retorno', 0))
                quantidade_venda = quantidade_saida - quantidade_retorno
                
                # Calcular valor total do item
                preco_venda = float(produto.get('preco_venda', 0.0))
                valor_total_item = quantidade_venda * preco_venda
                
                # Formatar valores para exibição
                if is_gelo_seco(produto_id):
                    # Manter valores decimais para gelo seco
                    quantidade_saida_formatada = quantidade_saida
                    quantidade_retorno_formatada = quantidade_retorno
                    quantidade_venda_formatada = quantidade_venda
                else:
                    # Converter para inteiros para outros produtos
                    quantidade_saida_formatada = int(quantidade_saida)
                    quantidade_retorno_formatada = int(quantidade_retorno)
                    quantidade_venda_formatada = int(quantidade_venda)
                
                itens_completos.append({
                    "id": produto_id,
                    "nome": produto.get('nome', ''),
                    "preco_venda": preco_venda,
                    "quantidade_saida": quantidade_saida_formatada,
                    "quantidade_retorno": quantidade_retorno_formatada,
                    "quantidade_venda": quantidade_venda_formatada,
                    "valor_total_item": valor_total_item
                })
        
        return jsonify(itens_completos)
    except Exception as e:
        print(f"Erro ao buscar itens do pedido: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro ao buscar itens do pedido: {str(e)}"}), 500

@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    try:
        # Filtrar por status se fornecido
        status = request.args.get('status')
        if status:
            if status == 'EM_ABERTO':
                # Considerar pedidos com status 'saida' como em aberto
                filtered_pedidos = [p for p in pedidos if p.get('status') == 'saida']
            else:
                filtered_pedidos = [p for p in pedidos if p.get('status') == status]
            return jsonify(filtered_pedidos)
        return jsonify(pedidos)
    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        traceback.print_exc()
        return jsonify({"message": f"Erro ao buscar pedidos: {str(e)}"}), 500

# Rota de teste para verificar se o servidor está funcionando
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "message": "API Licimar funcionando corretamente"})

if __name__ == '__main__':
    # Permitir acesso de qualquer origem (0.0.0.0) e usar porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
