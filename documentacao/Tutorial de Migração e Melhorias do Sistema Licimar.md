# Tutorial de Migração e Melhorias do Sistema Licimar

Este tutorial detalha todas as etapas realizadas para migrar o sistema Licimar de uma persistência baseada em JSON para um banco de dados relacional, além de implementar melhorias de segurança e interface.

## Índice

1. [Visão Geral das Melhorias](#1-visão-geral-das-melhorias)
2. [Migração para Banco de Dados Relacional](#2-migração-para-banco-de-dados-relacional)
3. [Implementação de Segurança](#3-implementação-de-segurança)
4. [Melhorias na Interface](#4-melhorias-na-interface)
5. [Hospedagem da Aplicação](#5-hospedagem-da-aplicação)
6. [Guia de Uso](#6-guia-de-uso)

## 1. Visão Geral das Melhorias

O projeto Licimar foi aprimorado com as seguintes melhorias:

- **Migração para banco de dados relacional**: Substituição da persistência em JSON por SQLite, garantindo maior escalabilidade e integridade dos dados.
- **Melhorias de segurança**: Implementação de autenticação de usuários, controle de acesso baseado em perfis e registro de logs para auditoria.
- **Melhorias na interface**: Implementação de temas claro/escuro, layout inspirado em totens de fast-food e integração de imagens de produtos.

## 2. Migração para Banco de Dados Relacional

### 2.1. Modelagem do Banco de Dados

O primeiro passo foi analisar a estrutura atual dos dados em JSON e definir um modelo relacional adequado. O modelo inclui as seguintes tabelas:

- **users**: Armazena informações de usuários do sistema
- **vendedores**: Armazena informações dos vendedores
- **produtos**: Armazena informações dos produtos disponíveis
- **pedidos**: Armazena informações dos pedidos realizados
- **itens_pedido**: Armazena os itens de cada pedido
- **logs**: Registra todas as operações realizadas no sistema
- **configuracoes**: Armazena configurações globais do sistema

### 2.2. Implementação do Banco de Dados

#### Configuração do SQLite

O arquivo `database.py` centraliza a configuração do banco de dados:

```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from datetime import datetime
import os

# Definição da classe base para os modelos
class Base(DeclarativeBase):
    pass

# Inicialização do SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Função para inicializar o banco de dados
def init_db(app):
    # Configuração do SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'licimar.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialização do SQLAlchemy com o app
    db.init_app(app)
    
    # Criação das tabelas se não existirem
    with app.app_context():
        db.create_all()
```

#### Definição dos Modelos

Os modelos foram definidos na pasta `models`, cada um em seu próprio arquivo:

**User (user.py)**:
```python
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)
```

**Vendedor (vendedor.py)**:
```python
class Vendedor(db.Model):
    __tablename__ = "vendedores"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    telefone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)
```

**Produto (produto.py)**:
```python
class Produto(db.Model):
    __tablename__ = "produtos"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    imagem_url = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)
```

### 2.3. Migração dos Dados

Para migrar os dados do JSON para o banco de dados, foi implementada a função `migrate_json_to_db` no arquivo `database.py`:

```python
def migrate_json_to_db(app):
    import json
    from .models.vendedor import Vendedor
    from .models.produto import Produto
    from .models.pedido import Pedido
    from .models.item_pedido import ItemPedido
    
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'licimar_db.json')
    
    if not os.path.exists(json_path):
        print(f"Arquivo JSON não encontrado: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with app.app_context():
        # Verificar se já existem dados no banco
        if Vendedor.query.count() > 0:
            print("Banco de dados já possui dados. Migração ignorada.")
            return
        
        # Migrar vendedores
        for v in data.get('vendedores', []):
            vendedor = Vendedor(
                id=v['id'],
                nome=v['nome'],
                active=True
            )
            db.session.add(vendedor)
        
        # Migrar produtos
        for p in data.get('produtos', []):
            produto = Produto(
                id=p['id'],
                nome=p['nome'],
                preco_venda=p['preco_venda'],
                estoque=p['estoque'],
                active=True
            )
            db.session.add(produto)
        
        # Migrar pedidos e itens
        for p in data.get('pedidos', []):
            pedido = Pedido(
                id=p['id'],
                vendedor_id=p['vendedor_id'],
                data_operacao=datetime.fromisoformat(p['data_operacao']),
                status=p['status'],
                created_by=1  # Admin como criador padrão
            )
            db.session.add(pedido)
            
            # Migrar itens do pedido
            for item in p.get('itens', []):
                # Buscar preço do produto
                produto = next((prod for prod in data.get('produtos', []) if prod['id'] == item['produto_id']), None)
                preco = produto['preco_venda'] if produto else 0
                
                item_pedido = ItemPedido(
                    pedido_id=p['id'],
                    produto_id=item['produto_id'],
                    quantidade_saida=item['quantidade_saida'],
                    quantidade_retorno=item.get('quantidade_retorno', 0),
                    quantidade_perda=0,  # Valor padrão
                    preco_venda_unitario_registrado=preco
                )
                db.session.add(item_pedido)
        
        # Commit das alterações
        try:
            db.session.commit()
            print("Migração concluída com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro na migração: {str(e)}")
```

## 3. Implementação de Segurança

### 3.1. Autenticação de Usuários

A autenticação foi implementada utilizando JWT (JSON Web Tokens) para garantir segurança nas requisições:

```python
# Função para gerar token JWT
def generate_token(user_id, role):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id,
        'role': role
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY', 'dev_key'),
        algorithm='HS256'
    )

# Decorator para verificar token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token não fornecido!'}), 401
        
        try:
            # Decodificar o token
            data = jwt.decode(
                token, 
                current_app.config.get('SECRET_KEY', 'dev_key'),
                algorithms=['HS256']
            )
            
            # Buscar o usuário no banco
            current_user = User.query.filter_by(id=data['sub']).first()
            
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado!'}), 401
                
            if not current_user.active:
                return jsonify({'message': 'Usuário inativo!'}), 401
            
            # Armazenar o usuário e papel no contexto da requisição
            g.user = current_user
            g.role = data['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
            
        return f(*args, **kwargs)
    
    return decorated
```

### 3.2. Controle de Acesso Baseado em Perfis

O controle de acesso foi implementado utilizando um decorator que verifica o papel do usuário:

```python
# Decorator para verificar papel do usuário
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user:
                return jsonify({'message': 'Não autenticado!'}), 401
                
            if g.role not in roles:
                return jsonify({'message': 'Permissão negada!'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 3.3. Registro de Logs para Auditoria

Foi implementado um sistema de logs para registrar todas as operações realizadas no sistema:

```python
# Função auxiliar para registrar logs
def register_log(action, entity_type, entity_id, details=None):
    """
    Registra uma operação no log de auditoria
    
    Args:
        action (str): Tipo de ação (CREATE, UPDATE, DELETE, etc)
        entity_type (str): Tipo de entidade afetada
        entity_id (int): ID da entidade afetada
        details (str, optional): Detalhes adicionais da operação
    """
    if not hasattr(g, 'user') or not g.user:
        # Se não houver usuário autenticado, não registra log
        return
    
    log = Log(
        user_id=g.user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
```

## 4. Melhorias na Interface

### 4.1. Implementação de Temas (Claro/Escuro)

Foi implementado um sistema de temas que permite alternar entre modo claro e escuro:

```jsx
// ThemeProvider.jsx
export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "vite-ui-theme",
  ...props
}) {
  const [theme, setTheme] = useState(
    () => localStorage.getItem(storageKey) || defaultTheme
  )

  useEffect(() => {
    const root = window.document.documentElement

    root.classList.remove("light", "dark")

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light"

      root.classList.add(systemTheme)
      return
    }

    root.classList.add(theme)
  }, [theme])

  const value = {
    theme,
    setTheme: (theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}
```

### 4.2. Layout no Estilo de Totens de Fast-Food

O layout foi redesenhado para se assemelhar aos totens de autoatendimento de fast-food:

```jsx
function App() {
  const [carrinho, setCarrinho] = useState([]);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState('todos');
  const [produtosFiltrados, setProdutosFiltrados] = useState(produtos);
  const [totalCarrinho, setTotalCarrinho] = useState(0);

  // Filtrar produtos por categoria
  useEffect(() => {
    if (categoriaSelecionada === 'todos') {
      setProdutosFiltrados(produtos);
    } else {
      setProdutosFiltrados(produtos.filter(produto => produto.categoria === categoriaSelecionada));
    }
  }, [categoriaSelecionada]);

  // Calcular total do carrinho
  useEffect(() => {
    const total = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
    setTotalCarrinho(total);
  }, [carrinho]);

  // Adicionar produto ao carrinho
  const adicionarAoCarrinho = (produto) => {
    const itemExistente = carrinho.find(item => item.id === produto.id);
    
    if (itemExistente) {
      setCarrinho(carrinho.map(item => 
        item.id === produto.id 
          ? { ...item, quantidade: item.quantidade + 1 } 
          : item
      ));
    } else {
      setCarrinho([...carrinho, { ...produto, quantidade: 1 }]);
    }
  };

  return (
    <ThemeProvider defaultTheme="light">
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-16 items-center justify-between">
            <h1 className="text-2xl font-bold">Licimar Sorvetes</h1>
            <div className="flex items-center gap-4">
              <ModeToggle />
              <div className="relative">
                <Button variant="outline" size="icon">
                  <ShoppingCart className="h-5 w-5" />
                  {carrinho.length > 0 && (
                    <Badge className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0">
                      {carrinho.reduce((acc, item) => acc + item.quantidade, 0)}
                    </Badge>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container py-6">
          <Tabs defaultValue="produtos" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="produtos">Produtos</TabsTrigger>
              <TabsTrigger value="carrinho">Carrinho</TabsTrigger>
            </TabsList>
            
            {/* Produtos Tab */}
            <TabsContent value="produtos" className="space-y-4">
              {/* Categorias */}
              <div className="flex overflow-x-auto pb-2 gap-2">
                {categorias.map(categoria => (
                  <Button
                    key={categoria.id}
                    variant={categoriaSelecionada === categoria.id ? "default" : "outline"}
                    onClick={() => setCategoriaSelecionada(categoria.id)}
                    className="whitespace-nowrap"
                  >
                    {categoria.nome}
                  </Button>
                ))}
              </div>
              
              {/* Lista de Produtos */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {produtosFiltrados.map(produto => (
                  <Card key={produto.id} className="overflow-hidden">
                    <CardHeader className="p-0">
                      <div className="h-48 overflow-hidden">
                        <img 
                          src={produto.imagem} 
                          alt={produto.nome} 
                          className="w-full h-full object-cover transition-transform hover:scale-105"
                        />
                      </div>
                    </CardHeader>
                    <CardContent className="p-4">
                      <CardTitle className="text-lg">{produto.nome}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">{produto.descricao}</p>
                      <p className="font-bold text-lg mt-2">R$ {produto.preco.toFixed(2)}</p>
                    </CardContent>
                    <CardFooter className="p-4 pt-0">
                      <Button 
                        className="w-full" 
                        onClick={() => adicionarAoCarrinho(produto)}
                      >
                        Adicionar ao Carrinho
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </ThemeProvider>
  );
}
```

### 4.3. Integração das Imagens de Produtos

As imagens dos produtos foram integradas ao frontend:

```jsx
// Importar imagens dos produtos
import chicabon from './assets/images/chicabon.avif';
import chicabonZero from './assets/images/chicabon_zero.avif';
import tablito from './assets/images/tablito.avif';
import magnumClassico from './assets/images/magnum_classico.avif';
import magnumBranco from './assets/images/magnum_branco.avif';
import magnumCookiesCream from './assets/images/magnum_cookies_cream.avif';
import cornettoMms from './assets/images/cornetto_mms.avif';
import cornettoCrocante from './assets/images/cornetto_crocante.avif';
import unicornetto from './assets/images/unicornetto.avif';
import fruttareLimao from './assets/images/fruttare_limao.avif';
import fruttareCoco from './assets/images/fruttare_coco.avif';
import fruttareUva from './assets/images/fruttare_uva.avif';
import frutilly from './assets/images/frutilly.avif';
import eskibonClassico from './assets/images/eskibon_classico.avif';
import miniEskibon from './assets/images/mini_eskibon.avif';
import nutablito from './assets/images/nutablito.avif';
import brigadeiro from './assets/images/brigadeiro.avif';

// Dados dos produtos
const produtos = [
  {
    id: 1,
    nome: 'Picolé Chicabon',
    preco: 8.0,
    imagem: chicabon,
    categoria: 'picole',
    descricao: 'O clássico picolé de baunilha com cobertura de chocolate'
  },
  // ... outros produtos
];
```

## 5. Hospedagem da Aplicação

### 5.1. Opções de Hospedagem Gratuita

Para hospedar a aplicação gratuitamente, recomendamos as seguintes opções:

1. **Render**: Oferece hospedagem gratuita para aplicações web com banco de dados SQLite.
   - Site: https://render.com
   - Vantagens: Fácil configuração, suporte a Python e Node.js
   - Limitações: Aplicações gratuitas hibernam após 15 minutos de inatividade

2. **Railway**: Plataforma para implantar aplicações com banco de dados.
   - Site: https://railway.app
   - Vantagens: Fácil integração com GitHub, suporte a vários bancos de dados
   - Limitações: Créditos limitados na versão gratuita

3. **Vercel**: Ideal para hospedar o frontend React.
   - Site: https://vercel.com
   - Vantagens: Otimizado para aplicações frontend, integração com GitHub
   - Limitações: Melhor para frontend, backend com algumas restrições

### 5.2. Configuração para Hospedagem

#### Backend (Flask)

1. Crie um arquivo `Procfile` na raiz do projeto backend:
   ```
   web: gunicorn src.main:app
   ```

2. Crie um arquivo `requirements.txt` com todas as dependências:
   ```
   Flask==3.1.0
   Flask-SQLAlchemy==3.1.1
   PyJWT==2.10.1
   gunicorn==21.2.0
   ```

3. Configure variáveis de ambiente para produção:
   ```python
   # No arquivo main.py
   import os
   
   # Configuração do Secret Key
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
   ```

#### Frontend (React)

1. Crie um arquivo `.env.production` na raiz do projeto frontend:
   ```
   VITE_API_URL=https://sua-api-backend.com
   ```

2. Construa a versão de produção:
   ```bash
   cd frontend/licimar_mvp_frontend
   npm run build
   ```

3. O diretório `dist` gerado pode ser hospedado em qualquer serviço de hospedagem estática.

## 6. Guia de Uso

### 6.1. Inicialização do Sistema

Para iniciar o sistema localmente:

1. **Backend**:
   ```bash
   cd backend/licimar_mvp_app
   pip install -r requirements.txt
   python src/main.py
   ```

2. **Frontend**:
   ```bash
   cd frontend/licimar_mvp_frontend
   npm install
   npm run dev
   ```

### 6.2. Autenticação e Acesso

O sistema possui três níveis de acesso:

1. **Admin**: Acesso total ao sistema, incluindo gerenciamento de usuários
2. **Manager**: Pode gerenciar produtos, vendedores e pedidos
3. **User**: Acesso básico para operações do dia a dia

Para acessar o sistema, use as credenciais padrão:
- Username: admin
- Senha: admin123

### 6.3. Operações Principais

#### Gerenciamento de Produtos

- **Listar produtos**: GET /api/produtos
- **Adicionar produto**: POST /api/produtos
- **Atualizar produto**: PUT /api/produtos/{id}
- **Excluir produto**: DELETE /api/produtos/{id}

#### Gerenciamento de Vendedores

- **Listar vendedores**: GET /api/vendedores
- **Adicionar vendedor**: POST /api/vendedores
- **Atualizar vendedor**: PUT /api/vendedores/{id}
- **Excluir vendedor**: DELETE /api/vendedores/{id}

#### Gerenciamento de Pedidos

- **Listar pedidos**: GET /api/pedidos
- **Criar pedido**: POST /api/pedidos
- **Registrar retorno**: POST /api/pedidos/{id}/retorno
- **Fechar pedido**: POST /api/pedidos/{id}/fechar

### 6.4. Personalização

#### Alteração de Tema

O sistema permite alternar entre tema claro e escuro através do botão no canto superior direito da interface.

#### Adição de Novos Produtos

Para adicionar novos produtos com imagens:

1. Adicione a imagem do produto na pasta `frontend/licimar_mvp_frontend/src/assets/images`
2. Importe a imagem no arquivo `App.jsx`
3. Adicione o produto ao array `produtos` com todas as informações necessárias

---

Este tutorial abrange todas as melhorias implementadas no sistema Licimar. Para qualquer dúvida ou suporte adicional, entre em contato com a equipe de desenvolvimento.
