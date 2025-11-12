import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TelaSaidaProdutos from './components/TelaSaidaProdutos';
import TelaRetornoCalculo from './components/TelaRetornoCalculo';

function App() {
  // Estilo simples para a navegação
  const navStyle = {
    padding: '10px',
    backgroundColor: '#f0f0f0',
    marginBottom: '20px',
  };
  const linkStyle = {
    margin: '0 10px',
    textDecoration: 'none',
    color: '#333',
    fontWeight: 'bold',
    fontSize: '16px'
  };

  return (
    <Router>
      <div>
        <nav style={navStyle}>
          <Link to="/saida" style={linkStyle}>Registrar Saída</Link>
          <Link to="/retorno" style={linkStyle}>Registrar Retorno/Cálculo</Link>
        </nav>

        <Routes>
          <Route path="/saida" element={<TelaSaidaProdutos />} />
          <Route path="/retorno" element={<TelaRetornoCalculo />} />
          {/* Rota padrão pode ser a de saída ou uma tela inicial, se houver */}
          <Route path="/" element={<TelaSaidaProdutos />} /> 
        </Routes>
      </div>
    </Router>
  );
}

export default App;

