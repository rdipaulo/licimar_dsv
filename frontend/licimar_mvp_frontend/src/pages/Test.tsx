import React from 'react';

export default function TestPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>✅ Sistema Licimar MVP</h1>
      <p>O Frontend está carregando corretamente!</p>
      
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
        <h2>Verificações:</h2>
        <ul>
          <li>✅ React está funcionando</li>
          <li>✅ Router está configurado</li>
          <li>✅ Componentes podem ser carregados</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <h3>Próximos passos:</h3>
        <p>Se você está vendo esta página, tudo está funcionando.</p>
        <p>Verifique o console do navegador (F12) para erros mais específicos.</p>
      </div>
    </div>
  );
}
