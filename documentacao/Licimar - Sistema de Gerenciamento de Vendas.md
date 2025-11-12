# Licimar - Sistema de Gerenciamento de Vendas

![Licimar Logo](https://private-us-east-1.manuscdn.com/sessionFile/MqWJHYemMOKLxpiwVoF3so/sandbox/YGbEeUe1wA1Ga7ji9ir3NG-images_1748035463803_na1fn_L2hvbWUvdWJ1bnR1L2xpY2ltYXJfZHN2L2Zyb250ZW5kL2xpY2ltYXJfbXZwX2Zyb250ZW5kL3NyYy9hc3NldHMvcmVhY3Q.svg?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTXFXSkhZZW1NT0tMeHBpd1ZvRjNzby9zYW5kYm94L1lHYkVlVWUxd0ExR2E3amk5aXIzTkctaW1hZ2VzXzE3NDgwMzU0NjM4MDNfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyeHBZMmx0WVhKZlpITjJMMlp5YjI1MFpXNWtMMnhwWTJsdFlYSmZiWFp3WDJaeWIyNTBaVzVrTDNOeVl5OWhjM05sZEhNdmNtVmhZM1Euc3ZnIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzY3MjI1NjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=gRyzSo0lL-KwRTlMlTjxoBrX0d~ct15p3qEEYFPXHZ6-l502XO6nBzqvE1l3OLOpNUz0N2d8z-5mUg95Dh6YN4-rgXM6dVFSW~p~TDS~QGfCzAxAG5nhBApwCxJo94B4J1x5Piub6Dg4a7bRQ-LgfkHEMnGPWrJ2quo4LihO6nE~32v27ZGKeJ3CR4wD9asZyJgD0vnpPzPOCf0-~gCixG1omarnVkswZHwVPsqm3GL5wPZWOZQimoGJ~885353DDLDQkqzpz3~Zctx7kUs~vmfpVMeWe6A77Et-jQlj8jB-mhzAS-pwT4Kv3bSZvsWb4MTDRjE2VIXOXeTE~lePuw__) <!-- Substituir pelo logo real se houver -->

Sistema web para gerenciamento de vendas de produtos, focado em controle de estoque, pedidos e vendedores, com interface moderna inspirada em totens de autoatendimento.

## Visão Geral

O Licimar é uma aplicação full-stack desenvolvida para facilitar o controle de operações de venda, especialmente para vendedores externos. Ele permite:

- Gerenciar produtos (cadastro, estoque, preço)
- Gerenciar vendedores
- Registrar pedidos de saída e retorno de produtos
- Calcular valores a pagar pelos vendedores
- Autenticar usuários com diferentes níveis de acesso
- Auditar operações através de logs detalhados
- Visualizar produtos em uma interface amigável com tema claro/escuro

## Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Shadcn/ui
- **Autenticação**: JWT (JSON Web Tokens)
- **Banco de Dados**: SQLite (pode ser facilmente adaptado para MySQL ou PostgreSQL)
- **Testes**: Pytest (backend), Jest e React Testing Library (frontend)

## Estrutura do Projeto

```
licimar_dsv/
├── backend/
│   └── licimar_mvp_app/
│       ├── src/
│       │   ├── models/       # Modelos SQLAlchemy
│       │   ├── routes/       # Blueprints Flask (API endpoints)
│       │   ├── database.py   # Configuração do DB e migração
│       │   ├── main.py       # Ponto de entrada da aplicação Flask
│       │   └── ...
│       ├── tests/            # Testes automatizados do backend
│       │   ├── conftest.py   # Configuração e fixtures para testes
│       │   ├── test_auth.py  # Testes de autenticação
│       │   └── ...
│       ├── requirements.txt  # Dependências Python
│       └── wsgi.py           # Arquivo WSGI para Gunicorn
├── frontend/
│   └── licimar_mvp_frontend/
│       ├── public/           # Arquivos estáticos públicos
│       ├── src/
│       │   ├── assets/       # Imagens e outros assets
│       │   ├── components/   # Componentes React (UI e reutilizáveis)
│       │   ├── __tests__/    # Testes automatizados do frontend
│       │   ├── __mocks__/    # Mocks para testes
│       │   ├── lib/          # Utilitários
│       │   ├── App.jsx       # Componente principal da aplicação
│       │   └── main.tsx      # Ponto de entrada da aplicação React
│       ├── package.json      # Dependências e scripts Node.js
│       ├── jest.config.js    # Configuração do Jest para testes
│       ├── vite.config.ts    # Configuração do Vite
│       └── tailwind.config.js # Configuração do Tailwind CSS
├── run_backend_tests.py      # Script para executar testes do backend
├── .gitignore
├── README.md                 # Este arquivo
├── modelo_relacional.md      # Documentação do modelo de dados
├── tutorial_licimar.md       # Tutorial de migração e uso
└── guia_hospedagem.md        # Guia de hospedagem
```

## Funcionalidades Principais

- **Dashboard de Produtos**: Visualização de produtos com imagens, preços e descrições.
- **Carrinho de Compras**: Interface estilo totem para adicionar produtos ao carrinho.
- **Gerenciamento (Backend)**:
    - CRUD completo para Usuários, Vendedores, Produtos e Pedidos.
    - Controle de estoque automático.
    - Cálculo de valor a pagar por pedido.
    - Sistema de autenticação seguro.
    - Logs de auditoria detalhados.
- **Temas**: Suporte a tema claro e escuro.
- **Responsividade**: Interface adaptada para diferentes tamanhos de tela.

## Instalação e Configuração

### Pré-requisitos

- Python 3.9+
- Node.js 18+
- npm ou pnpm

### Backend

1.  Navegue até a pasta do backend:
    ```bash
    cd backend/licimar_mvp_app
    ```
2.  Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Execute a aplicação Flask:
    ```bash
    python src/main.py
    ```
    O backend estará rodando em `http://localhost:5000`.
    A primeira execução criará o banco de dados `licimar.db` e migrará os dados do `licimar_db.json` (se encontrado).

### Frontend

1.  Navegue até a pasta do frontend:
    ```bash
    cd frontend/licimar_mvp_frontend
    ```
2.  Instale as dependências:
    ```bash
    npm install
    # ou
    # pnpm install
    ```
3.  Execute a aplicação React em modo de desenvolvimento:
    ```bash
    npm run dev
    # ou
    # pnpm dev
    ```
    O frontend estará acessível em `http://localhost:5173` (ou outra porta indicada pelo Vite).

## Uso

- Acesse a interface do frontend no seu navegador.
- Utilize a interface estilo totem para simular a seleção de produtos.
- Para acessar as funcionalidades de gerenciamento (requer autenticação), utilize uma ferramenta como Postman ou Insomnia para interagir com a API do backend (`http://localhost:5000/api/...`).
- Credenciais de admin padrão: `admin` / `admin123`.

## Testes

### Testes do Backend

O backend utiliza Pytest para testes automatizados, com fixtures configuradas para criar um ambiente de teste isolado usando SQLite em memória. Os testes cobrem autenticação, operações CRUD para todas as entidades e validação de regras de negócio.

Para executar os testes do backend, você pode usar o script auxiliar `run_backend_tests.py` que configura o ambiente corretamente:

```bash
# A partir da raiz do projeto (licimar_dsv/)
python run_backend_tests.py
```

Alternativamente, você pode executar os testes diretamente com o Pytest:

```bash
# Certifique-se de que o ambiente virtual do backend está ativado
# (se você criou um em backend/licimar_mvp_app/venv)
# source backend/licimar_mvp_app/venv/bin/activate

PYTHONPATH=backend/licimar_mvp_app pytest backend/licimar_mvp_app/tests -v
```

O ambiente de testes do backend utiliza:
- SQLite em memória para testes isolados e rápidos
- Fixtures para criar usuários de teste, produtos e outros dados necessários
- Mocks para serviços externos quando necessário
- Asserções para validar respostas da API e estado do banco de dados

### Testes do Frontend

O frontend utiliza Jest e React Testing Library para testes de componentes e integração. Os testes verificam a renderização correta dos componentes, interações do usuário e comportamento da interface.

Para executar os testes do frontend:

```bash
# Navegue até a pasta do frontend
cd frontend/licimar_mvp_frontend

# Execute os testes
npm test

# Para executar em modo de observação (útil durante o desenvolvimento)
npm run test:watch
```

O ambiente de testes do frontend inclui:
- Jest como executor de testes
- React Testing Library para renderizar e interagir com componentes
- Mocks para serviços externos e APIs
- Configuração para lidar com CSS, imagens e outros recursos estáticos
- Cobertura de código para monitorar a qualidade dos testes

Os testes do frontend estão organizados na pasta `src/__tests__` e seguem a convenção de nomenclatura `*.test.jsx` ou `*.test.tsx`. Cada componente importante deve ter seu próprio arquivo de teste correspondente.

Exemplo de teste de componente (Button.test.jsx):
```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Button } from '../components/ui/button';

test('renders button component', () => {
  render(<Button>Click Me</Button>);
  const buttonElement = screen.getByText(/click me/i);
  expect(buttonElement).toBeInTheDocument();
});

test('calls onClick handler when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Click Me</Button>);
  
  const buttonElement = screen.getByText(/click me/i);
  fireEvent.click(buttonElement);
  
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

## Integração Contínua

O projeto está preparado para integração contínua, permitindo que você configure pipelines de CI/CD em plataformas como GitHub Actions, GitLab CI ou Jenkins. Os testes automatizados do backend e frontend podem ser executados como parte do processo de CI para garantir que novas alterações não quebrem a funcionalidade existente.

Exemplo de configuração para GitHub Actions (arquivo `.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        cd backend/licimar_mvp_app
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python run_backend_tests.py

  test-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install dependencies
      run: |
        cd frontend/licimar_mvp_frontend
        npm install
    - name: Run tests
      run: |
        cd frontend/licimar_mvp_frontend
        npm test
```

## Hospedagem

Consulte o arquivo `guia_hospedagem.md` para instruções detalhadas sobre como hospedar a aplicação em plataformas gratuitas como Render. O guia inclui passos específicos para configurar tanto o backend Flask quanto o frontend React, garantindo que a aplicação funcione corretamente em ambiente de produção.

O processo de hospedagem envolve:
1. Preparação dos arquivos para produção
2. Configuração de variáveis de ambiente
3. Implantação do backend e frontend
4. Configuração de CORS para comunicação entre serviços
5. Monitoramento e manutenção

## Documentação Adicional

Para informações mais detalhadas sobre aspectos específicos do projeto, consulte os seguintes documentos:

- **modelo_relacional.md**: Documentação completa do modelo de dados, incluindo tabelas, relacionamentos, índices e considerações de migração.
- **tutorial_licimar.md**: Tutorial passo a passo sobre a migração do JSON para o banco de dados relacional e implementação das melhorias de segurança e interface.
- **guia_hospedagem.md**: Guia detalhado para hospedar a aplicação em serviços gratuitos, com instruções específicas para diferentes plataformas.

## Contribuição

Contribuições são bem-vindas! Se você deseja contribuir para o projeto, siga estas etapas:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Implemente suas alterações
4. Execute os testes para garantir que tudo está funcionando
5. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
6. Envie para o branch (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

Certifique-se de que seus testes passam e que sua implementação segue os padrões do projeto.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes (se aplicável).
