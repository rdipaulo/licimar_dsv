# 📋 Limpeza de Dados de Teste - Licimar MVP

Instruções para remover o histórico de pedidos e dívidas de testes.

## 🚀 Forma Mais Fácil (Script Python)

### 1. Listar Pedidos
```bash
python clean_history.py listar-pedidos
```
Mostra todos os pedidos registrados no banco.

### 2. Limpar Pedidos
```bash
python clean_history.py limpar-pedidos
```
Deleta **TODOS** os pedidos. Pedirá confirmação.

### 3. Limpar Dívidas
```bash
python clean_history.py limpar-dividas
```
Reseta `divida_acumulada` de todos os ambulantes para **0.00**.

### 4. Limpar TUDO
```bash
python clean_history.py limpar-tudo
```
Deleta pedidos **E** reseta dívidas em uma operação.

### 5. Resetar Banco Inteiro
```bash
python clean_history.py resetar-db
```
⚠️ **CUIDADO**: Deleta TUDO e recria com dados de teste (admin/admin123).

---

## 🔍 Forma Manual (SQL)

Se preferir usar SQL direto, consulte `sql_cleanup_queries.sql`:

### Deletar todos os pedidos
```sql
DELETE FROM pedidos;
```

### Resetar todas as dívidas
```sql
UPDATE ambulante SET divida_acumulada = 0;
```

### Ambos
```sql
BEGIN TRANSACTION;
    DELETE FROM pedidos;
    UPDATE ambulante SET divida_acumulada = 0;
COMMIT;
```

### Executar arquivo SQL completo
```bash
sqlite3 backend/licimar_mvp_app/instance/licimar_dev.db < sql_cleanup_queries.sql
```

---

## 📊 Verificar Dados

```bash
# Ver resumo de dados de teste
cd backend/licimar_mvp_app
python check_test_data.py
```

Output esperado:
```
============================================================
VERIFICAÇÃO DE DADOS DE TESTE
============================================================

Total de pedidos: 0
Ambuantes com dívida: 0

============================================================
```

---

## ⚠️ Advertências Importantes

1. **Backups**: Sempre faça backup antes de deletar dados
   ```bash
   cp backend/licimar_mvp_app/instance/licimar_dev.db backup_licimar_dev.db
   ```

2. **Confirmação Necessária**: Todos os comandos pedem confirmação (`s/n`)

3. **Irreversível**: Uma vez deletado, não pode ser recuperado (sem backup)

4. **Produção**: NUNCA execute `resetar-db` em produção sem backup!

---

## 📁 Arquivos Fornecidos

| Arquivo | Descrição |
|---------|-----------|
| `clean_history.py` | Script Python para limpeza (RECOMENDADO) |
| `sql_cleanup_queries.sql` | Queries SQL puras com documentação |
| `check_test_data.py` | Script para verificar dados de teste |

---

## 🎯 Casos de Uso

### ✅ Depois de testar tudo
```bash
python clean_history.py limpar-tudo
```

### ✅ Antes de demonstração
```bash
python clean_history.py listar-pedidos  # Verificar o que vai deletar
python clean_history.py limpar-tudo     # Limpar
python init_database.py                 # Recriar dados de teste
```

### ✅ Resetar tudo para começar do zero
```bash
python clean_history.py resetar-db
```

### ✅ Backup antes de deletar
```bash
cd backend/licimar_mvp_app
cp instance/licimar_dev.db instance/licimar_dev.db.bak
cd ../..
python clean_history.py limpar-tudo
```

---

## 🔧 Troubleshooting

### Script retorna "Nenhum pedido para deletar"
✓ Isso é normal se já foram deletados anteriormente.

### Erro de permissão
```
PermissionError: database is locked
```
- Certifique-se que nenhum servidor está rodando
- Ou espere alguns segundos e tente novamente

### Erro de conexão ao banco
```
sqlite3.OperationalError: unable to open database file
```
- Verifique se `backend/licimar_mvp_app/instance/licimar_dev.db` existe
- Se não existir, execute: `cd backend/licimar_mvp_app && python init_database.py`

---

## 📝 Logs

Os scripts registram todas as ações em console. Exemplos:

```
✓ Deletados 3 pedido(s)
✓ Dívidas resetadas para 2 ambulante(s)
[OK] Operação concluída com sucesso
```

---

## 🔐 Backup e Recuperação

### Fazer backup
```bash
cp backend/licimar_mvp_app/instance/licimar_dev.db backup_$(date +%Y%m%d_%H%M%S).db
```

### Restaurar backup
```bash
cp backup_licimar_dev.db backend/licimar_mvp_app/instance/licimar_dev.db
```

### Listar backups
```bash
ls -la backup_*.db
```

---

## ❓ Dúvidas

**P: Posso deletar apenas um pedido específico?**
R: Sim, edite a query em `sql_cleanup_queries.sql`:
```sql
DELETE FROM pedidos WHERE id = 1;  -- Deleta apenas pedido ID 1
```

**P: Posso resetar dívida de um ambulante específico?**
R: Sim:
```sql
UPDATE ambulante SET divida_acumulada = 0 WHERE nome = 'Ivan Magé';
```

**P: Quantos dados posso deletar por vez?**
R: Ilimitado! O script suporta qualquer quantidade.

**P: Preciso de senha para executar?**
R: Não, mas o script pedirá confirmação (`s/n`).

---

**Última atualização**: 28/11/2025
**Versão**: 2.0.0
