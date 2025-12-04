-- =====================================================================
-- LICIMAR MVP - SQL Queries para Limpeza de Histórico de Testes
-- =====================================================================
-- Arquivo: sql_cleanup_queries.sql
-- Descrição: Queries SQL puras para remover dados de teste
-- Banco: SQLite
-- =====================================================================

-- =====================================================================
-- 1. VISUALIZAR DADOS ANTES DE DELETAR
-- =====================================================================

-- Contar pedidos
SELECT COUNT(*) AS total_pedidos FROM pedido;

-- Listar todos os pedidos
SELECT 
    p.id,
    p.ambulante_id,
    a.nome as ambulante_nome,
    p.data,
    p.status,
    p.total,
    p.created_at
FROM pedido p
LEFT JOIN ambulante a ON p.ambulante_id = a.id
ORDER BY p.created_at DESC;

-- Listar dívidas
SELECT 
    id,
    nome,
    divida_acumulada,
    email,
    status
FROM ambulante
WHERE divida_acumulada > 0
ORDER BY divida_acumulada DESC;

-- Total de dívida acumulada
SELECT COALESCE(SUM(divida_acumulada), 0) AS total_divida FROM ambulante;

-- =====================================================================
-- 2. DELETAR HISTÓRICO DE PEDIDOS
-- =====================================================================

-- Opção A: Deletar TODOS os pedidos
DELETE FROM pedido;

-- Opção B: Deletar pedidos por data (últimas 24 horas)
DELETE FROM pedido 
WHERE datetime(created_at) > datetime('now', '-1 day');

-- Opção C: Deletar pedidos de um ambulante específico
DELETE FROM pedido 
WHERE ambulante_id = 1;  -- Substitua 1 pelo ID do ambulante

-- Opção D: Deletar pedidos com status específico
DELETE FROM pedido 
WHERE status = 'pendente';  -- ou 'saida', 'retorno'

-- =====================================================================
-- 3. RESETAR DÍVIDAS
-- =====================================================================

-- Opção A: Resetar TODAS as dívidas para 0
UPDATE ambulante 
SET divida_acumulada = 0;

-- Opção B: Resetar dívida de um ambulante específico
UPDATE ambulante 
SET divida_acumulada = 0 
WHERE id = 1;  -- Substitua 1 pelo ID

-- Opção C: Resetar dívida de um ambulante pelo nome
UPDATE ambulante 
SET divida_acumulada = 0 
WHERE nome = 'Ivan Magé';  -- Substitua pelo nome

-- =====================================================================
-- 4. OPERAÇÕES COMBINADAS
-- =====================================================================

-- Deletar TUDO (pedidos + resetar dívidas) em uma transação
BEGIN;
    DELETE FROM pedido;
    UPDATE ambulante SET divida_acumulada = 0;
COMMIT;

-- =====================================================================
-- 5. RESETAR SEQUÊNCIAS (SQLite)
-- =====================================================================

-- Resetar ID do próximo pedido
DELETE FROM sqlite_sequence WHERE name='pedido';

-- Resetar todos os IDs
DELETE FROM sqlite_sequence;

-- =====================================================================
-- 6. VERIFICAR INTEGRIDADE APÓS LIMPEZA
-- =====================================================================

-- Verificar se pedidos foram deletados
SELECT COUNT(*) as pedidos_restantes FROM pedido;

-- Verificar se todas as dívidas foram zeradas
SELECT COUNT(*) as ambulantes_com_divida 
FROM ambulante 
WHERE divida_acumulada > 0;

-- Resumo completo do banco de dados
SELECT 
    (SELECT COUNT(*) FROM pedido) as total_pedidos,
    (SELECT COUNT(*) FROM ambulante WHERE divida_acumulada > 0) as ambulantes_com_divida,
    COALESCE((SELECT SUM(divida_acumulada) FROM ambulante), 0) as total_divida_acumulada,
    (SELECT COUNT(*) FROM usuario) as total_usuarios,
    (SELECT COUNT(*) FROM categoria) as total_categorias,
    (SELECT COUNT(*) FROM produto) as total_produtos,
    (SELECT COUNT(*) FROM ambulante) as total_ambulantes;

-- =====================================================================
-- 7. BACKUP ANTES DE DELETAR
-- =====================================================================

-- Criar cópia da tabela pedido antes de deletar
CREATE TABLE pedido_backup AS SELECT * FROM pedido;

-- Criar cópia da tabela ambulante antes de resetar
CREATE TABLE ambulante_backup AS SELECT * FROM ambulante;

-- Restaurar de backup se necessário
-- DELETE FROM pedido;
-- INSERT INTO pedido SELECT * FROM pedido_backup;

-- Deletar backups depois de confirmação
-- DROP TABLE IF EXISTS pedido_backup;
-- DROP TABLE IF EXISTS ambulante_backup;

-- =====================================================================
-- COMO USAR ESTE ARQUIVO:
-- =====================================================================
--
-- 1. Via SQLite CLI:
--    sqlite3 instance/licimar_dev.db < sql_cleanup_queries.sql
--
-- 2. Via Python com o script clean_history.py (RECOMENDADO):
--    python clean_history.py limpar-pedidos
--    python clean_history.py limpar-dividas
--    python clean_history.py limpar-tudo
--
-- 3. Via DB Browser for SQLite (GUI):
--    - Abra o arquivo instance/licimar_dev.db
--    - Vá em "Execute SQL"
--    - Cole a query desejada
--    - Clique "Execute SQL"
--
-- =====================================================================
-- NOTAS IMPORTANTES:
-- =====================================================================
--
-- ⚠ CUIDADO: Estas operações são irreversíveis!
--   Faça BACKUP antes de executar qualquer DELETE ou UPDATE
--
-- ✓ Sempre execute: SELECT * FROM pedido; ANTES de deletar
--
-- ✓ Use TRANSAÇÕES para operações múltiplas:
--   BEGIN TRANSACTION;
--   ... sua operação ...
--   ROLLBACK; (se quiser desfazer)
--   ou
--   COMMIT; (para confirmar)
--
-- ✓ Para ambiente de produção:
--   - Use backups regulares
--   - Implemente soft-delete (coluna is_deleted)
--   - Use audit logs para rastrear exclusões
--
-- =====================================================================
