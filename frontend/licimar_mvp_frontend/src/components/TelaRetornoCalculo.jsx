import React, { useState, useEffect, useRef } from 'react';
import './TelaRetornoCalculo.css';

// Componente da Tela de Retorno e Cálculo de Pagamento
function TelaRetornoCalculo() {
    const [pedidosEmAberto, setPedidosEmAberto] = useState([]);
    const [pedidoSelecionadoId, setPedidoSelecionadoId] = useState('');
    const [itensDoPedido, setItensDoPedido] = useState([]); // Itens do pedido selecionado
    const [itensRetorno, setItensRetorno] = useState({}); // { itemPedidoId: quantidade_retorno }
    const [loadingPedidos, setLoadingPedidos] = useState(true);
    const [loadingItens, setLoadingItens] = useState(false);
    const [valorAPagar, setValorAPagar] = useState(null);
    const [erroApi, setErroApi] = useState(null);
    const [mostrarResumo, setMostrarResumo] = useState(false);
    const [resumoPedido, setResumoPedido] = useState(null);
    const resumoRef = useRef(null);

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
                    // Inicializa o estado de retorno para os itens carregados
                    const initialRetorno = {};
                    data.forEach(item => {
                        initialRetorno[item.id] = 0;
                    });
                    setItensRetorno(initialRetorno);
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
            setItensRetorno({});
        }
    }, [pedidoSelecionadoId]);

    const handleItemRetornoChange = (itemPedidoId, quantidade) => {
        const itemOriginal = itensDoPedido.find(item => item.id === itemPedidoId);
        if (!itemOriginal) return;

        // Verificar se é o produto "Gelo Seco" para permitir valores decimais
        const isGelo = itemOriginal.nome.toLowerCase().includes("gelo");
        
        let qtdNum;
        if (isGelo) {
            qtdNum = parseFloat(quantidade) || 0;
        } else {
            qtdNum = parseInt(quantidade, 10) || 0;
        }

        if (qtdNum < 0) qtdNum = 0;
        if (qtdNum > itemOriginal.quantidade_saida) qtdNum = itemOriginal.quantidade_saida;

        setItensRetorno(prev => ({
            ...prev,
            [itemPedidoId]: qtdNum
        }));
    };

    const calcularQuantidadeVenda = (item) => {
        const retorno = itensRetorno[item.id] || 0;
        return item.quantidade_saida - retorno;
    };

    const calcularValorTotalItem = (item) => {
        const quantidadeVenda = calcularQuantidadeVenda(item);
        return quantidadeVenda * parseFloat(item.preco_venda);
    };

    const calcularValorTotalNota = () => {
        return itensDoPedido.reduce((total, item) => {
            return total + calcularValorTotalItem(item);
        }, 0);
    };

    const handleSubmitFechamento = async (event) => {
        event.preventDefault();
        setErroApi(null);
        if (!pedidoSelecionadoId) {
            alert("Por favor, selecione um pedido.");
            return;
        }

        const itensParaEnviar = Object.entries(itensRetorno)
            .map(([itemPedidoId, quantidade_retorno]) => ({
                produto_id: parseInt(itemPedidoId, 10),
                quantidade_retorno: quantidade_retorno
            }));
        
        const payload = {
            pedido_id: parseInt(pedidoSelecionadoId, 10),
            itens: itensParaEnviar
        };

        console.log(`Enviando dados de fechamento para pedido ID ${pedidoSelecionadoId}:`, payload);

        try {
            const response = await fetch(`${API_BASE_URL}/api/pedidos/retorno`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (response.ok) {
                // Preparar dados para o resumo
                const pedidoInfo = pedidosEmAberto.find(p => p.id === parseInt(pedidoSelecionadoId));
                const resumo = {
                    pedidoId: pedidoSelecionadoId,
                    vendedor: pedidoInfo ? pedidoInfo.vendedor_nome : 'Vendedor não identificado',
                    data: pedidoInfo ? new Date(pedidoInfo.data_operacao) : new Date(),
                    dataRetorno: new Date(),
                    itens: itensDoPedido.map(item => ({
                        nome: item.nome,
                        quantidade_saida: item.quantidade_saida,
                        quantidade_retorno: itensRetorno[item.id] || 0,
                        quantidade_venda: calcularQuantidadeVenda(item),
                        preco_venda: parseFloat(item.preco_venda),
                        valor_total: calcularValorTotalItem(item)
                    })),
                    valorTotal: parseFloat(result.valor_total)
                };
                
                setResumoPedido(resumo);
                setMostrarResumo(true);
                setValorAPagar(parseFloat(result.valor_total).toFixed(2));
                
                // Não limpar os dados ainda para permitir a visualização do resumo
            } else {
                alert(`Erro ao fechar pedido: ${result.message}`);
                setErroApi(result.message || "Erro desconhecido ao fechar pedido.");
            }
        } catch (error) {
            console.error("Erro ao conectar com a API:", error);
            alert("Erro de conexão ao fechar pedido.");
            setErroApi("Erro de conexão. Verifique se o backend está rodando.");
        }
    };

    const handleImprimirResumo = () => {
        if (resumoRef.current) {
            // Abrir uma nova janela para impressão
            const conteudoImpressao = resumoRef.current.innerHTML;
            const janelaImpressao = window.open('', '_blank', 'height=600,width=800');
            
            janelaImpressao.document.write(`
                <html>
                    <head>
                        <title>Resumo do Pedido #${resumoPedido.pedidoId}</title>
                        <style>
                            body {
                                font-family: 'Courier New', monospace;
                                font-size: 12px;
                                width: 80mm;
                                margin: 0 auto;
                                padding: 5mm;
                            }
                            .cabecalho {
                                text-align: center;
                                margin-bottom: 10px;
                                border-bottom: 1px dashed #000;
                                padding-bottom: 10px;
                            }
                            .titulo {
                                font-size: 14px;
                                font-weight: bold;
                            }
                            .info {
                                margin: 5px 0;
                            }
                            .item {
                                margin: 5px 0;
                            }
                            .item-nome {
                                font-weight: bold;
                            }
                            .valores {
                                display: flex;
                                justify-content: space-between;
                            }
                            .total {
                                margin-top: 10px;
                                border-top: 1px dashed #000;
                                padding-top: 10px;
                                font-weight: bold;
                                text-align: right;
                            }
                            .rodape {
                                margin-top: 20px;
                                text-align: center;
                                border-top: 1px dashed #000;
                                padding-top: 10px;
                            }
                            table {
                                width: 100%;
                                border-collapse: collapse;
                            }
                            th, td {
                                text-align: left;
                                padding: 3px;
                            }
                            th {
                                border-bottom: 1px solid #000;
                            }
                            .valor-direita {
                                text-align: right;
                            }
                            @media print {
                                body {
                                    width: 80mm;
                                }
                            }
                        </style>
                    </head>
                    <body>
                        <div class="cupom-fiscal">
                            <div class="cabecalho">
                                <div class="titulo">LICIMAR - DEPÓSITO DE SORVETES</div>
                                <div class="info">CNPJ: 00.000.000/0000-00</div>
                                <div class="info">Rua Exemplo, 123 - Bairro</div>
                                <div class="info">Cidade - Estado - CEP: 00000-000</div>
                            </div>
                            
                            <div class="info">Pedido: #${resumoPedido.pedidoId}</div>
                            <div class="info">Vendedor: ${resumoPedido.vendedor}</div>
                            <div class="info">Data Saída: ${resumoPedido.data.toLocaleDateString()} ${resumoPedido.data.toLocaleTimeString()}</div>
                            <div class="info">Data Retorno: ${resumoPedido.dataRetorno.toLocaleDateString()} ${resumoPedido.dataRetorno.toLocaleTimeString()}</div>
                            
                            <table>
                                <thead>
                                    <tr>
                                        <th>Produto</th>
                                        <th>Qtd</th>
                                        <th>Preço</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${resumoPedido.itens.map(item => `
                                        <tr>
                                            <td>${item.nome}</td>
                                            <td>${item.quantidade_venda}</td>
                                            <td>R$ ${item.preco_venda.toFixed(2)}</td>
                                            <td class="valor-direita">R$ ${item.valor_total.toFixed(2)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                            
                            <div class="total">
                                <div>TOTAL A PAGAR: R$ ${resumoPedido.valorTotal.toFixed(2)}</div>
                            </div>
                            
                            <div class="rodape">
                                <div>Obrigado pela preferência!</div>
                                <div>Data: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</div>
                            </div>
                        </div>
                    </body>
                </html>
            `);
            
            janelaImpressao.document.close();
            janelaImpressao.focus();
            
            // Imprimir após um pequeno delay para garantir que o conteúdo seja carregado
            setTimeout(() => {
                janelaImpressao.print();
                // Fechar a janela após a impressão (opcional)
                // janelaImpressao.close();
            }, 500);
        }
    };

    const handleFecharResumo = () => {
        setMostrarResumo(false);
        // Limpar os dados após fechar o resumo
        setPedidoSelecionadoId('');
        setItensDoPedido([]);
        setItensRetorno({});
        fetchPedidosEmAberto(); // Recarrega a lista de pedidos em aberto
    };

    return (
        <div className="tela-retorno">
            <h1>Registro de Retorno e Cálculo</h1>
            {erroApi && <p className="erro">Erro: {erroApi}</p>}
            
            {!mostrarResumo ? (
                <>
                    <div className="selecao-pedido">
                        <label htmlFor="pedido">Selecione o Pedido em Aberto:</label>
                        <select 
                            id="pedido" 
                            value={pedidoSelecionadoId} 
                            onChange={(e) => setPedidoSelecionadoId(e.target.value)}
                            required
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
                            
                            {itensDoPedido.length > 0 && (
                                <div className="tabela-container">
                                    <table className="tabela-retorno">
                                        <thead>
                                            <tr>
                                                <th>Produto</th>
                                                <th>Qtd. Saída</th>
                                                <th>Qtd. Retorno</th>
                                                <th>Qtd. Venda</th>
                                                <th>Preço Item</th>
                                                <th>Valor Total Item</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {itensDoPedido.map(item => {
                                                const isGelo = item.nome.toLowerCase().includes("gelo");
                                                const quantidadeVenda = calcularQuantidadeVenda(item);
                                                const valorTotalItem = calcularValorTotalItem(item);
                                                
                                                return (
                                                    <tr key={item.id}>
                                                        <td>{item.nome}</td>
                                                        <td>{item.quantidade_saida}</td>
                                                        <td>
                                                            <input 
                                                                type="number" 
                                                                min="0"
                                                                max={item.quantidade_saida}
                                                                step={isGelo ? "0.001" : "1"}
                                                                value={itensRetorno[item.id] || 0} 
                                                                onChange={(e) => handleItemRetornoChange(item.id, e.target.value)} 
                                                                className="input-quantidade"
                                                            />
                                                        </td>
                                                        <td>{quantidadeVenda}</td>
                                                        <td>R$ {parseFloat(item.preco_venda).toFixed(2)}</td>
                                                        <td>R$ {valorTotalItem.toFixed(2)}</td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                        <tfoot>
                                            <tr>
                                                <td colSpan="5" className="valor-total-label">Valor Total da Nota:</td>
                                                <td className="valor-total-valor">R$ {calcularValorTotalNota().toFixed(2)}</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                    
                                    <button type="submit" className="botao-finalizar">Finalizar Retorno e Calcular</button>
                                </div>
                            )}
                        </form>
                    )}
                </>
            ) : (
                <div className="resumo-pedido" ref={resumoRef}>
                    <div className="resumo-cabecalho">
                        <h2>Resumo do Pedido #{resumoPedido.pedidoId}</h2>
                        <div className="resumo-info">
                            <p><strong>Vendedor:</strong> {resumoPedido.vendedor}</p>
                            <p><strong>Data Saída:</strong> {resumoPedido.data.toLocaleDateString()} {resumoPedido.data.toLocaleTimeString()}</p>
                            <p><strong>Data Retorno:</strong> {resumoPedido.dataRetorno.toLocaleDateString()} {resumoPedido.dataRetorno.toLocaleTimeString()}</p>
                        </div>
                    </div>
                    
                    <table className="tabela-resumo">
                        <thead>
                            <tr>
                                <th>Produto</th>
                                <th>Qtd. Saída</th>
                                <th>Qtd. Retorno</th>
                                <th>Qtd. Venda</th>
                                <th>Preço Item</th>
                                <th>Valor Total Item</th>
                            </tr>
                        </thead>
                        <tbody>
                            {resumoPedido.itens.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.nome}</td>
                                    <td>{item.quantidade_saida}</td>
                                    <td>{item.quantidade_retorno}</td>
                                    <td>{item.quantidade_venda}</td>
                                    <td>R$ {item.preco_venda.toFixed(2)}</td>
                                    <td>R$ {item.valor_total.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colSpan="5" className="valor-total-label">Valor Total a Pagar:</td>
                                <td className="valor-total-valor">R$ {resumoPedido.valorTotal.toFixed(2)}</td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <div className="resumo-acoes">
                        <button onClick={handleImprimirResumo} className="botao-imprimir">Imprimir Resumo</button>
                        <button onClick={handleFecharResumo} className="botao-fechar">Fechar Resumo</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TelaRetornoCalculo;
