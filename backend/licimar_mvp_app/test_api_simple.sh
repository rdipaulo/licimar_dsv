#!/bin/bash

# Script de testes simplificado da API Licimar MVP

BASE_URL="http://localhost:5000"

echo "=========================================="
echo "TESTE DA API LICIMAR MVP"
echo "=========================================="
echo ""

# 1. Teste de Status
echo "1. TESTE DE STATUS"
echo "------------------------------------------"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

# 2. Login
echo "2. TESTE DE LOGIN"
echo "------------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')

echo "$LOGIN_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "ERRO: Não foi possível obter o token"
    exit 1
fi

echo "✓ Token obtido com sucesso"
echo ""

# 3. Listar Usuários
echo "3. LISTAR USUÁRIOS"
echo "------------------------------------------"
curl -s "$BASE_URL/api/usuarios" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 4. Listar Categorias
echo "4. LISTAR CATEGORIAS"
echo "------------------------------------------"
curl -s "$BASE_URL/api/categorias" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 5. Listar Produtos
echo "5. LISTAR PRODUTOS"
echo "------------------------------------------"
curl -s "$BASE_URL/api/produtos" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 6. Listar Ambulantes
echo "6. LISTAR AMBULANTES"
echo "------------------------------------------"
curl -s "$BASE_URL/api/ambulantes" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 7. Listar Pedidos
echo "7. LISTAR PEDIDOS"
echo "------------------------------------------"
curl -s "$BASE_URL/api/pedidos" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# 8. Criar Pedido
echo "8. CRIAR PEDIDO"
echo "------------------------------------------"
curl -s -X POST "$BASE_URL/api/pedidos" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "ambulante_id": 1,
        "status": "saida",
        "observacoes": "Pedido de teste",
        "itens": [
            {
                "produto_id": 1,
                "quantidade_saida": 10,
                "preco_unitario": 2.50
            },
            {
                "produto_id": 2,
                "quantidade_saida": 5,
                "preco_unitario": 4.00
            }
        ]
    }' | python3 -m json.tool
echo ""

# 9. Relatório de Estoque Baixo
echo "9. RELATÓRIO DE ESTOQUE BAIXO"
echo "------------------------------------------"
curl -s "$BASE_URL/api/relatorios/estoque-baixo" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "TESTES CONCLUÍDOS COM SUCESSO"
echo "=========================================="
