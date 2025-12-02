✅ CHECKLIST DE TESTES - Browser Testing

## 📱 COMO TESTAR

1. **Iniciar Backend:**
   ```
   cd backend/licimar_mvp_app
   python app.py
   ```

2. **Abrir Frontend:**
   ```
   cd frontend/licimar_mvp_frontend
   npm run dev
   # ou
   pnpm dev
   ```

3. **Acessar:** http://localhost:3000

---

## ✓ TESTES A FAZER

### ✓ TESTE 1: Atualizar Preço (Sem erro de nome duplicado)
- [ ] Login com admin/admin123
- [ ] Ir para "Produtos"
- [ ] Clicar em um produto
- [ ] Aumentar preço em 1% (ex: 10.00 → 10.10)
- [ ] Manter mesmo nome
- [ ] Clicar "Salvar"
- [ ] ✓ NÃO DEVE dar erro "Produto com esse nome já existe"
- [ ] ✓ DEVE atualizar preço com sucesso

### ✓ TESTE 2: Campo Gelo (Deve aceitar decimais)
- [ ] Ir para "Pedidos" → "Retorno"
- [ ] Selecionar um pedido
- [ ] No campo "Gelo (kg)"
- [ ] Inserir valor: 1.5
- [ ] ✓ DEVE aceitar e exibir claramente
- [ ] Observação: Campo agora é 33% maior (w-16)

### ✓ TESTE 3: Campo Dívida (Deve aceitar decimais)
- [ ] Mesmo pedido de cima
- [ ] No campo "Cobrança de Dívida"
- [ ] Inserir valor: 5.75
- [ ] ✓ DEVE aceitar e exibir claramente
- [ ] Observação: Campo agora é 50% maior (w-48)

### ✓ TESTE 4: Criar Saida (Deve persistir)
- [ ] Ir para "Pedidos" → "Saída"
- [ ] Criar novo pedido com saída
- [ ] ✓ DEVE registrar com sucesso
- [ ] Ir para "Retorno"
- [ ] ✓ DEVE aparecer o pedido na lista

### ✓ TESTE 5: Imprimir Nota Fiscal
- [ ] No pedido de saída criado
- [ ] Clicar "Registrar Saida"
- [ ] ✓ DEVE mostrar notificação "Nota Fiscal gerada"
- [ ] ✓ DEVE iniciar download do PDF
- [ ] ✓ DEVE recarregar página após 1.5 segundos
- [ ] ✓ Tela DEVE estar limpa e pronta para novo pedido

### ✓ TESTE 6: Verificar Histórico
- [ ] Ir para "Pedidos" → "Histórico"
- [ ] ✓ DEVE aparecer o pedido que completou retorno
- [ ] ✓ DEVE mostrar dados completos (cliente, total, data)

---

## 📊 RESULTADO ESPERADO

Se todos os testes ✓, então:
- ✓ Todas 6 correções críticas funcionando
- ✓ Sistema pronto para produção
- ✓ Usuários não mais enfrentarão esses problemas

---

## 🚀 SE TUDO PASSOU

Parabéns! Sistema Licimar MVP está 100% funcional!

Próximos passos:
1. Backup do banco de dados
2. Deploy em produção (usar .env com DATABASE_URL)
3. Monitorar logs por 24 horas

---

## ❌ SE ALGO FALHAR

1. Verifique se backend está rodando (porta 5000)
2. Verifique se frontend está rodando (porta 3000)
3. Abra console do navegador (F12) para ver erros
4. Limpe cache: Ctrl+Shift+Delete
5. Reinicie backend e frontend

---

**Criado:** 01/12/2025
**Versão:** 1.0
**Status:** Pronto para Testes
