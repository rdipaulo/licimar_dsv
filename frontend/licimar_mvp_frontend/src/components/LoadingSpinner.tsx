import React from 'react';

/**
 * Componente de spinner de carregamento
 * Exibido enquanto a autenticação está sendo verificada
 */
const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <div className="inline-flex items-center justify-center">
          <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
        </div>
        <p className="mt-4 text-lg font-medium text-gray-700">Carregando...</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
