#!/bin/bash

# Script de testes da API Licimar MVP
# Testa todos os endpoints principais

BASE_URL="http://localhost:5000"
TOKEN=""

echo "=========================================="
echo "TESTE DA API LICIMAR MVP"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testando:${NC} $description"
    echo "  Endpoint: $method $endpoint"
    
    if [ -z "$data" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -X $method "$BASE_URL$endpoint")
        else
            response=$(curl -s -X $method "$BASE_URL$endpoint" -H "Authorization: Bearer $TOKEN")
        fi
    else
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $TOKEN" \
                -d "$data")
        fi
    fi
    
    echo "  Resposta: $response"
    echo ""
    
    # Retornar a resposta para uso posterior
    echo "$response"
}

# 1. Teste de Status
echo "=========================================="
echo "1. TESTES DE STATUS"
echo "=========================================="
test_endpoint "GET" "/" "" "Status da API"
test_endpoint "GET" "/api/status" "" "Status detalhado"
echo ""

# 2. Teste de Autenticação
echo "=========================================="
echo "2. TESTES DE AUTENTICAÇÃO"
echo "=========================================="

# Login com usuário admin
echo -e "${YELLOW}Fazendo login como admin...${NC}"
login_response=$(test_endpoint "POST" "/api/auth/login" \
    '{"username":"admin","password":"admin123"}' \
    "Login de administrador")

# Extrair token
TOKEN=$(echo $login_response | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}ERRO: Não foi possível obter o token de autenticação${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Token obtido com sucesso${NC}"
    echo "  Token: ${TOKEN:0:50}..."
fi
echo ""

# 3. Teste de Usuários
echo "=========================================="
echo "3. TESTES DE USUÁRIOS"
echo "=========================================="
test_endpoint "GET" "/api/usuarios" "" "Listar todos os usuários"
test_endpoint "GET" "/api/usuarios/1" "" "Buscar usuário por ID"
echo ""

# 4. Teste de Categorias
echo "=========================================="
echo "4. TESTES DE CATEGORIAS"
echo "=========================================="
test_endpoint "GET" "/api/categorias" "" "Listar todas as categorias"
test_endpoint "GET" "/api/categorias/1" "" "Buscar categoria por ID"

# Criar nova categoria
test_endpoint "POST" "/api/categorias" \
    '{"nome":"Categoria Teste","descricao":"Descrição da categoria teste"}' \
    "Criar nova categoria"
echo ""

# 5. Teste de Produtos
echo "=========================================="
echo "5. TESTES DE PRODUTOS"
echo "=========================================="
test_endpoint "GET" "/api/produtos" "" "Listar todos os produtos"
test_endpoint "GET" "/api/produtos/1" "" "Buscar produto por ID"

# Criar novo produto
test_endpoint "POST" "/api/produtos" \
    '{"nome":"Produto Teste","preco":10.50,"estoque":50,"categoria_id":1,"descricao":"Produto de teste"}' \
    "Criar novo produto"

# Atualizar produto
test_endpoint "PUT" "/api/produtos/1" \
    '{"preco":12.00}' \
    "Atualizar preço do produto"
echo ""

# 6. Teste de Ambulantes
echo "=========================================="
echo "6. TESTES DE AMBULANTES"
echo "=========================================="
test_endpoint "GET" "/api/ambulantes" "" "Listar todos os ambulantes"
test_endpoint "GET" "/api/ambulantes/1" "" "Buscar ambulante por ID"

# Criar novo ambulante
test_endpoint "POST" "/api/ambulantes" \
    '{"nome":"Ambulante Teste","email":"teste@email.com","telefone":"(11) 99999-9999","cpf":"999.999.999-99","endereco":"Rua Teste, 999","status":"ativo"}' \
    "Criar novo ambulante"
echo ""

# 7. Teste de Regras de Cobrança
echo "=========================================="
echo "7. TESTES DE REGRAS DE COBRANÇA"
echo "=========================================="
test_endpoint "GET" "/api/regras-cobranca" "" "Listar todas as regras de cobrança"
test_endpoint "GET" "/api/regras-cobranca/1" "" "Buscar regra por ID"
echo ""

# 8. Teste de Pedidos
echo "=========================================="
echo "8. TESTES DE PEDIDOS"
echo "=========================================="
test_endpoint "GET" "/api/pedidos" "" "Listar todos os pedidos"

# Criar novo pedido
test_endpoint "POST" "/api/pedidos" \
    '{"ambulante_id":1,"status":"saida","observacoes":"Pedido de teste","itens":[{"produto_id":1,"quantidade_saida":10,"preco_unitario":2.50}]}' \
    "Criar novo pedido"

# Listar pedidos novamente
test_endpoint "GET" "/api/pedidos" "" "Listar pedidos após criação"
echo ""

# 9. Teste de Relatórios
echo "=========================================="
echo "9. TESTES DE RELATÓRIOS"
echo "=========================================="
test_endpoint "GET" "/api/relatorios/vendas" "" "Relatório de vendas"
test_endpoint "GET" "/api/relatorios/estoque-baixo" "" "Relatório de estoque baixo"
echo ""

# 10. Teste de Logs
echo "=========================================="
echo "10. TESTES DE LOGS"
echo "=========================================="
test_endpoint "GET" "/api/logs" "" "Listar logs do sistema"
echo ""

echo "=========================================="
echo "TESTES CONCLUÍDOS"
echo "=========================================="
echo -e "${GREEN}✓ Todos os testes foram executados${NC}"
echo ""
