import React, { useState, useEffect } from 'react';

// Componente da Tela de Saída de Produtos
function TelaSaidaProdutos() {
    // Estados para armazenar dados do formulário e da API
    const [vendedores, setVendedores] = useState([]);
    const [produtos, setProdutos] = useState([]);
    const [vendedorSelecionado, setVendedorSelecionado] = useState('');
    const [itensSaida, setItensSaida] = useState({}); // Objeto para { produtoId: quantidade }
    const [loadingVendedores, setLoadingVendedores] = useState(true);
    const [loadingProdutos, setLoadingProdutos] = useState(true);
    const [erroApi, setErroApi] = useState(null);

    const API_BASE_URL = 'http://localhost:5000'; // URL do backend Flask

    // Efeito para buscar vendedores e produtos da API ao carregar o componente
    useEffect(() => {
        setLoadingVendedores(true);
        fetch(`${API_BASE_URL}/api/vendedores`)
            .then(res => {
                if (!res.ok) throw new Error(`Erro ao buscar vendedores: ${res.statusText}`);
                return res.json();
            })
            .then(data => {
                setVendedores(data);
                setLoadingVendedores(false);
            })
            .catch(error => {
                console.error("Erro ao buscar vendedores:", error);
                setErroApi("Não foi possível carregar os vendedores.");
                setLoadingVendedores(false);
            });

        setLoadingProdutos(true);
        fetch(`${API_BASE_URL}/api/produtos`)
            .then(res => {
                if (!res.ok) throw new Error(`Erro ao buscar produtos: ${res.statusText}`);
                return res.json();
            })
            .then(data => {
                setProdutos(data);
                setLoadingProdutos(false);
            })
            .catch(error => {
                console.error("Erro ao buscar produtos:", error);
                setErroApi("Não foi possível carregar os produtos.");
                setLoadingProdutos(false);
            });
    }, []);

    // Função para lidar com a mudança na quantidade de um produto
    const handleQuantidadeChange = (produtoId, quantidade) => {
        const produto = produtos.find(p => p.id === parseInt(produtoId, 10));
        const estoqueDisponivel = produto ? produto.estoque : 0;
        let qtdNum = parseInt(quantidade, 10) || 0;

        if (qtdNum < 0) qtdNum = 0;
        if (qtdNum > estoqueDisponivel) {
            alert(`Quantidade solicitada (${qtdNum}) para ${produto.nome} excede o estoque disponível (${estoqueDisponivel}).`);
            qtdNum = estoqueDisponivel; // Ajusta para o máximo disponível
        }

        setItensSaida(prevItens => ({
            ...prevItens,
            [produtoId]: qtdNum
        }));
    };

    // Função para lidar com o envio do formulário de saída
    const handleSubmitSaida = async (event) => {
        event.preventDefault();
        setErroApi(null); // Limpa erros anteriores
        if (!vendedorSelecionado) {
            alert("Por favor, selecione um vendedor.");
            return;
        }

        const itensParaEnviar = Object.entries(itensSaida)
            .filter(([_, quantidade]) => quantidade > 0)
            .map(([produtoId, quantidade]) => ({
                produto_id: parseInt(produtoId, 10),
                quantidade_saida: quantidade
            }));

        if (itensParaEnviar.length === 0) {
            alert("Por favor, adicione pelo menos um produto à saída.");
            return;
        }

        const payload = {
            vendedor_nome: vendedorSelecionado,
            itens_saida: itensParaEnviar
        };

        console.log("Enviando dados de saída:", payload);

        try {
            const response = await fetch(`${API_BASE_URL}/api/pedidos/saida`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (response.ok) {
                alert(`Saída registrada com sucesso! Pedido ID: ${result.pedido_id}`);
                // Limpar formulário ou redirecionar
                setVendedorSelecionado('');
                setItensSaida({});
                // Refrescar lista de produtos para atualizar estoque (ou backend poderia retornar produtos atualizados)
                fetch(`${API_BASE_URL}/api/produtos`).then(res => res.json()).then(data => setProdutos(data));
            } else {
                alert(`Erro ao registrar saída: ${result.erro}`);
                setErroApi(result.erro || "Erro desconhecido ao registrar saída.");
            }
        } catch (error) {
            console.error("Erro ao conectar com a API:", error);
            alert("Erro de conexão ao registrar saída.");
            setErroApi("Erro de conexão. Verifique se o backend está rodando.");
        }
    };

    if (loadingVendedores || loadingProdutos) {
        return <p>Carregando dados...</p>;
    }

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: 'auto' }}>
            <h1>Registro de Saída de Produtos</h1>
            {erroApi && <p style={{ color: 'red' }}>Erro: {erroApi}</p>}
            <form onSubmit={handleSubmitSaida}>
                <div style={{ marginBottom: '15px' }}>
                    <label htmlFor="vendedor" style={{ display: 'block', marginBottom: '5px' }}>Selecione o Vendedor:</label>
                    <select 
                        id="vendedor" 
                        value={vendedorSelecionado} 
                        onChange={(e) => setVendedorSelecionado(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px' }}
                    >
                        <option value="">-- Selecione --</option>
                        {vendedores.map(v => <option key={v.id} value={v.nome}>{v.nome}</option>)}
                    </select>
                </div>

                <h2>Produtos Disponíveis</h2>
                {produtos.length === 0 && !loadingProdutos && <p>Nenhum produto encontrado.</p>}
                {produtos.map(produto => (
                    <div key={produto.id} style={{ border: '1px solid #ccc', margin: '10px 0', padding: '10px', borderRadius: '5px' }}>
                        <p><strong>{produto.nome}</strong></p>
                        <p>Preço: R$ {parseFloat(produto.preco_venda).toFixed(2)} - Estoque: {produto.estoque}</p>
                        <label htmlFor={`produto_${produto.id}_qtd`} style={{ marginRight: '10px' }}>Quantidade Saída:</label>
                        <input 
                            type="number" 
                            id={`produto_${produto.id}_qtd`} 
                            min="0" 
                            max={produto.estoque} // Limita pelo estoque atual
                            value={itensSaida[produto.id] || ''} 
                            onChange={(e) => handleQuantidadeChange(produto.id, e.target.value)} 
                            style={{ padding: '5px', width: '80px' }}
                        />
                    </div>
                ))}

                <button type="submit" style={{ padding: '10px 20px', marginTop: '20px', cursor: 'pointer' }}>Registrar Saída</button>
            </form>
        </div>
    );
}

export default TelaSaidaProdutos;

