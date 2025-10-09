# Sistema de Inscrição e Emissão Certificados Pint of Science Brasil

Um sistema completo para gerenciamento e emissão de certificados para participantes do evento Pint of Science Brasil, desenvolvido com Python, Streamlit e SQLite.

## 📋 Visão Geral

O sistema permite:
- **Inscrição de Participantes**: Registro público de participantes com validação de dados
- **Validação de Participação**: Coordenadores podem validar participações em suas cidades
- **Emissão de Certificados**: Geração automática de PDFs para participantes validados
- **Gestão Administrativa**: Interface completa para administradores gerenciarem o sistema

## 🏗️ Arquitetura

O sistema segue uma arquitetura modular com separação clara de responsabilidades:

```
pint-of-science/
├── app/                    # Módulos principais
│   ├── __init__.py        # Inicialização do pacote
│   ├── core.py            # Configurações e ambiente
│   ├── models.py          # Modelos de dados (SQLAlchemy + Pydantic)
│   ├── db.py              # Gerenciamento do banco de dados
│   ├── auth.py            # Autenticação e sessão
│   ├── services.py        # Lógica de negócio
│   └── utils.py           # Funções utilitárias
├── pages/                 # Páginas restritas
│   ├── 1_✅_Validação_de_Participantes.py  # Área de coordenadores
│   └── 2_⚙️_Administração.py             # Área de superadmin
├── static/                # Arquivos estáticos
│   └── .gitkeep
├── Home.py               # Página principal (pública)
├── requirements.txt      # Dependências Python
├── .env.example         # Exemplo de configuração
└── README.md           # Este arquivo
```

## 🚀 Funcionalidades

### Para Participantes (Público)
- ✅ Formulário de inscrição com validação
- ✅ Download de certificados por e-mail
- ✅ Interface responsiva e intuitiva

### Para Coordenadores (Acesso Restrito)
- ✅ Login seguro com autenticação
- ✅ Dashboard com estatísticas de participantes
- ✅ Validação em lote de participantes
- ✅ Filtros por cidade, função e status
- ✅ Visualização de detalhes dos participantes

### Para Superadmin (Acesso Restrito)
- ✅ Gestão completa de coordenadores
- ✅ CRUD de eventos, cidades e funções
- ✅ Dashboard com métricas do sistema
- ✅ Visualização de logs de auditoria
- ✅ Gerenciamento de usuários

## 📦 Tecnologias Utilizadas

- **Python 3.13+**: Linguagem principal
- **Streamlit**: Framework web
- **SQLite**: Banco de dados
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **Cryptography**: Criptografia de dados sensíveis
- **ReportLab**: Geração de PDFs
- **Brevo**: Serviço de e-mail
- **bcrypt**: Hash de senhas

## 🛠️ Instalação

### Pré-requisitos
- Python 3.13 ou superior
- pip ou uv para gerenciamento de pacotes

### Passo 1: Clonar o Repositório
```bash
git clone <URL-DO-REPOSITORIO>
cd pint-of-science
```

### Passo 2: Criar Ambiente Virtual
```bash
# Usando venv
python -m venv pint
source pint/bin/activate  # Linux/Mac
# ou
pint\Scripts\activate     # Windows

# Ou usando uv (recomendado)
uv venv
source .venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
# Usando pip
pip install -r requirements.txt

# Ou usando uv
uv pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env com suas configurações
nano .env  # ou use seu editor preferido
```

Variáveis necessárias:
```env
# Configurações do Banco de Dados
DATABASE_URL=sqlite:///pint_of_science.db

# Criptografia (gerar com: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode()))
ENCRYPTION_KEY=sua_chave_de_criptografia_aqui

# Configurações do Brevo (opcional, para envio de e-mails)
BREVO_API_KEY=sua_chave_api_brevo
BREVO_SENDER_EMAIL=seu_email@dominio.com
BREVO_SENDER_NAME=Pint of Science Brasil
```

### Passo 5: Inicializar o Banco de Dados

O sistema utiliza SQLite como banco de dados e será criado automaticamente na primeira execução. O processo de inicialização inclui a criação das tabelas e o seed de dados iniciais.

#### 5.1: Executar a Inicialização Automática
```bash
# Executar o sistema pela primeira vez
streamlit run Home.py
```

Na primeira execução, o sistema irá:
- ✅ Criar o arquivo `pint_of_science.db`
- ✅ Criar todas as tabelas necessárias
- ✅ Popular dados iniciais (cidades, funções, eventos)
- ✅ Criar usuário superadmin (se configurado)

#### 5.2: Verificar a Inicialização
Para verificar se o banco foi criado corretamente, execute o script de teste:

```bash
python tests/test_system.py
```

**Saída esperada:**
```
🚀 Iniciando testes do sistema Pint of Science Brasil
✅ Todos os arquivos necessários encontrados!
✅ Conexão com o banco de dados bem-sucedida!
✅ Banco de dados inicializado corretamente!
   - 10 cidades cadastradas
   - 6 funções cadastradas
   - 1 eventos cadastrados
🎉 Todos os testes passaram! O sistema está pronto para uso.
```

#### 5.3: Dados Iniciais Criados

**Cidades (10 cidades):**
- São Paulo (SP), Rio de Janeiro (RJ), Belo Horizonte (MG)
- Porto Alegre (RS), Recife (PE), Salvador (BA)
- Brasília (DF), Campinas (SP), Fortaleza (CE), Curitiba (PR)

**Funções (6 funções):**
- Organizador(a), Voluntário(a), Palestrante
- Moderador(a), Apoio Técnico, Divulgação

**Eventos:**
- Pint of Science 2024 (datas: 13-15 de maio)

**Superadmin (opcional):**
- Criado apenas se as variáveis `INITIAL_SUPERADMIN_*` estiverem configuradas no `.env`

**Coordenadores de Teste:**
- Um coordenador de teste é criado durante os testes: `teste@exemplo.com` / `senha123`
- Um participante de teste é criado: `participante@exemplo.com`

#### 5.4: Solução de Problemas

**Se o banco não for criado:**
```bash
# Forçar recriação do banco
rm pint_of_science.db
python tests/test_system.py
```

**Se houver erro de permissão:**
```bash
# Verificar permissões da pasta
chmod 755 .
ls -la pint_of_science.db
```

**Se os dados iniciais não forem criados:**
- Verifique se o arquivo `.env` existe e está configurado
- Execute `python -c "from app.db import init_database; init_database()"` para debug

#### 5.5: Reset/Recriação do Banco (Desenvolvimento)

Para desenvolvimento ou teste, você pode recriar o banco do zero:

```bash
# 1. Remover banco existente
rm pint_of_science.db

# 2. Executar inicialização
python tests/test_system.py

# 3. Verificar dados
python -c "
from app.db import db_manager
from app.models import Cidade, Funcao, Evento, Coordenador
with db_manager.get_db_session() as session:
    print(f'Cidades: {session.query(Cidade).count()}')
    print(f'Funções: {session.query(Funcao).count()}')
    print(f'Eventos: {session.query(Evento).count()}')
    print(f'Coordenadores: {session.query(Coordenador).count()}')
"
```
### Passo 6: Executar a Aplicação
```bash
streamlit run Home.py
```

A aplicação estará disponível em `http://localhost:8501`

## 👥 Perfis de Usuário

### 1. Participante (Público)
- Acesso livre ao formulário de inscrição
- Download de certificados após validação
- Sem necessidade de login

### 2. Coordenador de Cidade
- Login restrito com e-mail e senha
- Validação de participantes de sua cidade
- Visualização de estatísticas e relatórios

### 3. Superadmin
- Acesso completo ao sistema
- Gestão de usuários e configurações
- Visualização de logs e auditoria

## 🔐 Segurança

O sistema implementa várias camadas de segurança:

- **Criptografia de Dados**: Nomes e e-mails de participantes são criptografados
- **Hash de Senhas**: Senhas armazenadas com bcrypt
- **Sessão Segura**: Timeout de sessão (2 horas)
- **Proteção contra Brute Force**: Limite de tentativas de login
- **Validação de Entrada**: Todos os dados são validados com Pydantic
- **Auditoria**: Todas as ações importantes são registradas

## 📊 Fluxo de Trabalho

1. **Inscrição**: Participantes se registram através do formulário público
2. **Validação**: Coordenadores acessam a área restrita e validam as participações
3. **Emissão**: Sistema gera certificados PDF para participantes validados
4. **Download**: Participantes baixam certificados usando e-mail de cadastro

## 🧪 Testes

### Sistema de Testes Automatizado
O projeto inclui um sistema completo de testes que valida todas as funcionalidades:

```bash
# Executar todos os testes
python tests/test_system.py
```

**Testes Incluídos:**
- ✅ Verificação de estrutura de arquivos
- ✅ Conexão com banco de dados
- ✅ Inicialização do banco de dados
- ✅ Criptografia de dados
- ✅ Criação de coordenadores
- ✅ Registro de participantes
- ✅ Configuração de e-mail

### Teste de Funcionalidade Básica
1. Acesse `http://localhost:8501`
2. Preencha o formulário de inscrição como participante
3. Tente fazer login como coordenador (`teste@exemplo.com` / `senha123`)
4. Valide participantes na área restrita
5. Faça download de certificado

### Teste de E-mail
Configure as credenciais do Brevo no `.env` para testar o envio de e-mails.

## 🚀 Deploy

### Para Produção

1. **Variáveis de Ambiente**: Configure todas as variáveis necessárias no ambiente de produção
2. **Banco de Dados**: Considere usar PostgreSQL ou MySQL para produção
3. **SSL**: Configure HTTPS com certificado SSL
4. **Backup**: Implemente rotina de backup do banco de dados
5. **Monitoramento**: Configure logs e monitoramento

### Exemplo com Docker
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]
```

## 📝 Estrutura do Banco de Dados

### Tabelas Principais
- **eventos**: Informações dos eventos (ano, datas)
- **cidades**: Cidades participantes
- **funcoes**: Funções dos participantes
- **coordenadores**: Usuários do sistema
- **participantes**: Dados dos participantes (com criptografia)
- **auditoria**: Registro de ações do sistema

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Erro de Importação**: Verifique se todas as dependências foram instaladas
2. **Erro de Conexão**: Verifique as variáveis de ambiente no arquivo `.env`
3. **PDF não Gera**: Verifique se a pasta `static/` existe e tem permissões
4. **Login não Funciona**: Verifique as credenciais no banco de dados

### Logs de Erro
O sistema registra erros e pode ser configurado para exibir logs detalhados.

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Crie uma issue no GitHub
- Entre em contato com a equipe do Pint of Science Brasil

## 🎯 Próximos Passos

- [ ] Implementar testes unitários automatizados
- [ ] Adicionar suporte a múltiplos idiomas
- [ ] Dashboard avançado com analytics
- [ ] API REST para integração externa

---

**Desenvolvido com ❤️ para a comunidade Pint of Science Brasil**
