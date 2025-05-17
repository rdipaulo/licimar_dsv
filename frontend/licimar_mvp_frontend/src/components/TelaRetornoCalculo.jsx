import React, { useState, useEffect } from 'react';

// Componente da Tela de Retorno e Cálculo de Pagamento
function TelaRetornoCalculo() {
    const [pedidosEmAberto, setPedidosEmAberto] = useState([]);
    const [pedidoSelecionadoId, setPedidoSelecionadoId] = useState('');
    const [itensDoPedido, setItensDoPedido] = useState([]); // Itens do pedido selecionado
    const [itensRetornoPerda, setItensRetornoPerda] = useState({}); // { itemPedidoId: { retorno: X, perda: Y } }
    const [loadingPedidos, setLoadingPedidos] = useState(true);
    const [loadingItens, setLoadingItens] = useState(false);
    const [valorAPagar, setValorAPagar] = useState(null);
    const [erroApi, setErroApi] = useState(null);

    const API_BASE_URL = 'http://localhost:5000'; // URL do backend Flask

    // Função para buscar pedidos em aberto
    const fetchPedidosEmAberto = () => {
        setLoadingPedidos(true);
        setErroApi(null);
        fetch(`${API_BASE_URL}/api/pedidos?status=EM_ABERTO`)
            .then(res => {
                if (!res.ok) throw new Error(`Erro ao buscar pedidos: ${res.statusText}`);
                return res.json();
            })
            .then(data => {
                setPedidosEmAberto(data);
                setLoadingPedidos(false);
            })
            .catch(error => {
                console.error("Erro ao buscar pedidos em aberto:", error);
                setErroApi("Não foi possível carregar os pedidos em aberto.");
                setPedidosEmAberto([]); // Limpa em caso de erro
                setLoadingPedidos(false);
            });
    };

    // Efeito para buscar pedidos em aberto ao carregar
    useEffect(() => {
        fetchPedidosEmAberto();
    }, []);

    // Efeito para buscar itens de um pedido selecionado
    useEffect(() => {
        if (pedidoSelecionadoId) {
            setLoadingItens(true);
            setValorAPagar(null); // Limpa valor a pagar anterior
            setErroApi(null);
            fetch(`${API_BASE_URL}/api/pedidos/${pedidoSelecionadoId}/itens`)
                .then(res => {
                    if (!res.ok) throw new Error(`Erro ao buscar itens do pedido: ${res.statusText}`);
                    return res.json();
                })
                .then(data => {
                    setItensDoPedido(data);
                    // Inicializa o estado de retorno/perda para os itens carregados
                    const initialRetornoPerda = {};
                    data.forEach(item => {
                        initialRetornoPerda[item.id] = { retorno: 0, perda: 0 };
                    });
                    setItensRetornoPerda(initialRetornoPerda);
                    setLoadingItens(false);
                })
                .catch(error => {
                    console.error(`Erro ao buscar itens para o pedido ID: ${pedidoSelecionadoId}`, error);
                    setErroApi("Não foi possível carregar os itens do pedido selecionado.");
                    setItensDoPedido([]);
                    setLoadingItens(false);
                });
        } else {
            setItensDoPedido([]); // Limpa itens se nenhum pedido estiver selecionado
            setItensRetornoPerda({});
        }
    }, [pedidoSelecionadoId]);

    const handleItemRetornoPerdaChange = (itemPedidoId, tipo, quantidade) => {
        const itemOriginal = itensDoPedido.find(item => item.id === itemPedidoId);
        if (!itemOriginal) return;

        let qtdNum = parseInt(quantidade, 10) || 0;
        if (qtdNum < 0) qtdNum = 0;

        setItensRetornoPerda(prev => {
            const currentItemState = prev[itemPedidoId] || { retorno: 0, perda: 0 };
            const newState = { ...currentItemState, [tipo]: qtdNum };

            if ((newState.retorno + newState.perda) > itemOriginal.quantidade_saida) {
                alert(`Soma de retorno (${newState.retorno}) e perda (${newState.perda}) para ${itemOriginal.produto_nome} excede a quantidade de saída (${itemOriginal.quantidade_saida}). Ajustando para o máximo possível.`);
                // Ajusta para não exceder, priorizando o campo que está sendo alterado
                if (tipo === 'retorno') {
                    newState.retorno = itemOriginal.quantidade_saida - newState.perda;
                    if (newState.retorno < 0) newState.retorno = 0; 
                } else { // tipo === 'perda'
                    newState.perda = itemOriginal.quantidade_saida - newState.retorno;
                    if (newState.perda < 0) newState.perda = 0;
                }
            }
            return { ...prev, [itemPedidoId]: newState };
        });
    };

    const handleSubmitFechamento = async (event) => {
        event.preventDefault();
        setErroApi(null);
        if (!pedidoSelecionadoId) {
            alert("Por favor, selecione um pedido.");
            return;
        }

        const itensParaEnviar = Object.entries(itensRetornoPerda)
            .map(([itemPedidoId, { retorno, perda }]) => ({
                item_pedido_id: parseInt(itemPedidoId, 10),
                quantidade_retorno: retorno,
                quantidade_perda: perda
            }));
        
        const payload = {
            itens_retorno_perda: itensParaEnviar
        };

        console.log(`Enviando dados de fechamento para pedido ID ${pedidoSelecionadoId}:`, payload);

        try {
            const response = await fetch(`${API_BASE_URL}/api/pedidos/${pedidoSelecionadoId}/fechamento`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (response.ok) {
                alert(`Pedido ${pedidoSelecionadoId} fechado com sucesso! Valor a pagar: R$ ${parseFloat(result.valor_total_a_pagar).toFixed(2)}`);
                setValorAPagar(parseFloat(result.valor_total_a_pagar).toFixed(2));
                setPedidoSelecionadoId('');
                setItensDoPedido([]);
                setItensRetornoPerda({});
                fetchPedidosEmAberto(); // Recarrega a lista de pedidos em aberto
            } else {
                alert(`Erro ao fechar pedido: ${result.erro}`);
                setErroApi(result.erro || "Erro desconhecido ao fechar pedido.");
            }
        } catch (error) {
            console.error("Erro ao conectar com a API:", error);
            alert("Erro de conexão ao fechar pedido.");
            setErroApi("Erro de conexão. Verifique se o backend está rodando.");
        }
    };

    const cardStyle = { 
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '15px',
        margin: '10px 0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    };
    const inputStyle = { padding: '8px', margin: '5px 0', width: 'calc(50% - 10px)', boxSizing: 'border-box' };
    const buttonStyle = { 
        backgroundColor: '#FFC72C',
        color: '#27251F',
        border: 'none',
        padding: '12px 25px',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '16px',
        fontWeight: 'bold',
        marginTop: '20px'
    };

    return (
        <div style={{ padding: '20px', maxWidth: '700px', margin: 'auto', fontFamily: 'Arial, sans-serif' }}>
            <h1>Registro de Retorno e Cálculo</h1>
            {erroApi && <p style={{ color: 'red', fontWeight: 'bold' }}>Erro: {erroApi}</p>}
            
            <div style={cardStyle}>
                <label htmlFor="pedido" style={{ display: 'block', marginBottom: '8px', fontSize: '18px' }}>Selecione o Pedido em Aberto:</label>
                <select 
                    id="pedido" 
                    value={pedidoSelecionadoId} 
                    onChange={(e) => setPedidoSelecionadoId(e.target.value)}
                    required
                    style={{ width: '100%', padding: '10px', fontSize: '16px', marginBottom: '15px' }}
                >
                    <option value="">-- Selecione um Pedido --</option>
                    {loadingPedidos ? <option disabled>Carregando pedidos...</option> : 
                        (pedidosEmAberto.length > 0 ? 
                            pedidosEmAberto.map(p => (
                                <option key={p.id} value={p.id}>
                                    Pedido #{p.id} - {p.vendedor_nome} ({new Date(p.data_operacao).toLocaleDateString()})
                                </option>
                            ))
                            : <option disabled>Nenhum pedido em aberto encontrado.</option>)}
                </select>
            </div>

            {pedidoSelecionadoId && (
                <form onSubmit={handleSubmitFechamento}>
                    <h2>Itens do Pedido #{pedidoSelecionadoId}</h2>
                    {loadingItens && <p>Carregando itens do pedido...</p>}
                    {!loadingItens && itensDoPedido.length === 0 && <p>Nenhum item encontrado para este pedido.</p>}
                    
                    {itensDoPedido.map(item => (
                        <div key={item.id} style={cardStyle}>
                            <h3 style={{ marginTop: 0 }}>{item.produto_nome}</h3>
                            <p>Quantidade Saída: {item.quantidade_saida}</p>
                            <p>Preço Unitário Registrado: R$ {parseFloat(item.preco_venda_unitario_registrado).toFixed(2)}</p>
                            <div>
                                <label htmlFor={`item_${item.id}_retorno`} style={{ marginRight: '10px' }}>Qtd. Retorno (Bom Estado):</label>
                                <input 
                                    type="number" 
                                    id={`item_${item.id}_retorno`} 
                                    min="0"
                                    max={item.quantidade_saida - (itensRetornoPerda[item.id]?.perda || 0)}
                                    value={itensRetornoPerda[item.id]?.retorno || ''} 
                                    onChange={(e) => handleItemRetornoPerdaChange(item.id, 'retorno', e.target.value)} 
                                    style={inputStyle}
                                />
                            </div>
                            <div>
                                <label htmlFor={`item_${item.id}_perda`} style={{ marginRight: '10px' }}>Qtd. Perda (Estragado):</label>
                                <input 
                                    type="number" 
                                    id={`item_${item.id}_perda`} 
                                    min="0"
                                    max={item.quantidade_saida - (itensRetornoPerda[item.id]?.retorno || 0)}
                                    value={itensRetornoPerda[item.id]?.perda || ''} 
                                    onChange={(e) => handleItemRetornoPerdaChange(item.id, 'perda', e.target.value)} 
                                    style={inputStyle}
                                />
                            </div>
                        </div>
                    ))}
                    
                    {itensDoPedido.length > 0 && <button type="submit" style={buttonStyle}>Finalizar Retorno e Calcular</button>}
                </form>
            )}

            {valorAPagar !== null && (
                <div style={{ ...cardStyle, marginTop: '30px', backgroundColor: '#E8E8E8' }}>
                    <h2 style={{ color: '#D83A30' }}>Valor Total a Pagar: R$ {valorAPagar}</h2>
                </div>
            )}
        </div>
    );
}

export default TelaRetornoCalculo;

