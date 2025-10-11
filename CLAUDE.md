# Project Brief: Pint of Science Certificate System (v2)

## 1. Visão Geral e Objetivos do Projeto

O objetivo é desenvolver um sistema web completo para gerenciar e emitir certificados para os participantes do evento "Pint of Science Brasil". O sistema terá uma área pública para inscrição e download de certificados, e uma área administrativa para coordenadores validarem participações e gerenciarem os dados do evento.

- **Usuários-chave:** Participantes (público), Coordenadores de Cidade (admin restrito), Coordenador Geral (superadmin).
- **Principal Funcionalidade:** Inscrição -> Validação -> Emissão de Certificado em PDF.

## 2. Tecnologias Principais

- **Linguagem:** Python 3.10+
- **Framework Web:** Streamlit
- **Banco de Dados:** SQLite
- **Modelagem de Dados:** Pydantic
- **Criptografia:** Biblioteca `cryptography` (módulo Fernet)
- **Autenticação:** `streamlit-authenticator` (v0.3.3+)
- **Variáveis de Ambiente:** Arquivo `.env`

### 2.1. Authentication System - streamlit-authenticator

**IMPORTANT**: The project uses `streamlit-authenticator` library for robust session management and cookie-based persistent login. This was adopted after manual cookie management with `streamlit-cookies-manager` proved unreliable due to timing issues.

#### Key Implementation Details:

1. **Installation Requirements:**
   ```bash
   pip install streamlit-authenticator>=0.3.3 pyyaml
   # or with uv:
   uv pip install streamlit-authenticator pyyaml
   ```

2. **AuthManager Pattern** (in `app/auth.py`):
   - Uses `streamlit_authenticator.Authenticate` class
   - Loads credentials from database (bcrypt-hashed passwords)
   - Provides simple interface: `auth_manager.show_login_form()`
   - Automatic cookie management (no manual timing logic needed)

3. **Login Flow:**
   ```python
   # In Home.py or any public page:
   name, authentication_status, username = auth_manager.show_login_form()

   if authentication_status is True:
       # Login successful
       auth_manager.handle_login_result(name, authentication_status, username)
   elif authentication_status is False:
       # Login failed (wrong credentials)
       st.error("❌ Credenciais incorretas")
   # authentication_status is None: form not submitted yet
   ```

4. **Protected Pages:**
   ```python
   # At the top of any protected page:
   from app.auth import require_login, require_superadmin

   # For coordinator pages:
   require_login()

   # For superadmin-only pages:
   require_superadmin()
   ```

5. **Session Persistence:**
   - Sessions automatically persist across page refreshes (F5)
   - Cookie expiry: 30 days (configurable in `AuthManager._initialize_authenticator()`)
   - No manual token generation/storage needed
   - No cookie timing checks required

6. **Migration Notes:**
   - Old system used `streamlit-cookies-manager` (removed)
   - Backup of old code: `app/auth_old_backup.py`
   - Code reduction: 699 lines → 375 lines (46% smaller)
   - Database field `session_token` in `coordenadores` table is now unused but harmless
   - bcrypt password hashes remain compatible (no password reset needed)

7. **Troubleshooting:**
   - If login form doesn't appear, check that `streamlit-authenticator` is installed
   - If sessions don't persist, verify `.streamlit/config.toml` exists
   - The library shows warnings about `st.cache` deprecation - these are suppressed in config
   - Login button text is "Login" (English) - this comes from the library

8. **Testing Checklist:**
   - [ ] Login works with existing credentials
   - [ ] Session persists on F5 refresh
   - [ ] Protected pages load without "loading session" messages
   - [ ] Logout clears session properly
   - [ ] Multiple users can login simultaneously (different browsers)

For detailed migration information, see `MIGRATION_TO_STREAMLIT_AUTHENTICATOR.md`.

## 3. Princípios de Arquitetura

O código deve seguir estas boas práticas:

- **Separação de Responsabilidades (SoC):** Encapsular a lógica em classes e módulos distintos (ex: `services`, `models`, `db`, `ui`).
- **Injeção de Dependência (DI):** As dependências (ex: sessão do banco de dados) devem ser passadas para as funções/classes, não instanciadas dentro delas.
- **Configuração Centralizada:** Todas as chaves (Brevo SMTP, chave de criptografia) devem ser carregadas a partir de um arquivo `.env`.

## 4. Estrutura de Arquivos Proposta

```
pint-of-science/
│
├── app/
│   ├── init.py
│   ├── models.py         # Modelos Pydantic e SQLAlchemy
│   ├── services.py       # Lógica de negócio (validar, criptografar, gerar pdf)
│   ├── db.py             # Lógica de conexão e inicialização do DB
│   ├── core.py           # Configurações, carregamento do .env
│   ├── auth.py           # Lógica de autenticação de coordenadores
│   └── utils.py          # Funções utilitárias (ex: email, uuid)
│
├── pages/
│   ├── 1_✅_Validação_de_Participantes.py  # Página para Coordenadores
│   └── 2_⚙️_Administração.py             # Página para Superadmin
│
├── static/
│   └── logo.png
│
├── .env.example          # Exemplo de arquivo de configuração
├── requirements.txt
└── Home.py               # Página principal (inscrição, download e LOGIN)
```

## Development Workflows

### Running the Application

```bash
# Activate environment (using uv recommended)
source .venv/bin/activate  # or `source pint/bin/activate`

# Run Streamlit
streamlit run Home.py

# Access at http://localhost:8501
```

### Database Initialization

Database auto-initializes on first `db_manager` usage. To manually reset:

```bash
rm data/pint_of_science.db
python utils/seed_database.py  # Creates initial data structure
python test_system.py  # Re-creates with test data
```

### Testing

```bash
# Run system validation tests
python test_system.py

# Expected output: Connection tests, encryption tests, database checks

# Run pytest unit/integration tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app
```

## 5. Esquema do Banco de Dados e Modelos de Dados

**Tarefa:** Crie os modelos Pydantic (para validação de dados) e os modelos SQLAlchemy (para o ORM) correspondentes às seguintes tabelas:

### Tabela: `eventos`
- `id`: INTEGER, PRIMARY KEY
- `ano`: INTEGER, NOT NULL, UNIQUE
- `datas_evento`: JSON, NOT NULL (Lista da datas no formato YYYY-MM-DD ISO 8601, ex: ["2025-10-09", "2025-10-10", "2025-10-11"])
- `data_criacao`: TEXT, NOT NULL (data única no formato YYYY-MM-DD ISO 8601)

### Tabela: `cidades`
- `id`: INTEGER, PRIMARY KEY
- `nome`: TEXT, NOT NULL
- `estado`: TEXT, NOT NULL (Sigla com 2 caracteres)

### Tabela: `funcoes`
- `id`: INTEGER, PRIMARY KEY
- `nome_funcao`: TEXT, NOT NULL, UNIQUE

### Tabela: `coordenadores`
- `id`: INTEGER, PRIMARY KEY
- `nome`: TEXT, NOT NULL
- `email`: TEXT, NOT NULL, UNIQUE
- `senha_hash`: TEXT, NOT NULL
- `is_superadmin`: BOOLEAN, NOT NULL, DEFAULT False

### Tabela: `participantes`
- `id`: INTEGER, PRIMARY KEY
- `nome_completo_encrypted`: BLOB, NOT NULL
- `email_encrypted`: BLOB, NOT NULL
- `titulo_apresentacao`: TEXT
- `evento_id`: INTEGER, FOREIGN KEY (`eventos.id`)
- `cidade_id`: INTEGER, FOREIGN KEY (`cidades.id`)
- `funcao_id`: INTEGER, FOREIGN KEY (`funcoes.id`)
- `datas_participacao`: TEXT, NOT NULL
- `carga_horaria_calculada`: INTEGER, NOT NULL
- `validado`: BOOLEAN, NOT NULL, DEFAULT False
- `data_inscricao`: TEXT, NOT NULL (Formato ISO 8601)

### Tabela: `coordenador_cidade_link` (Tabela de Mapeamento N-para-N)
- `coordenador_id`: INTEGER, FOREIGN KEY (`coordenadores.id`)
- `cidade_id`: INTEGER, FOREIGN KEY (`cidades.id`)
- PRIMARY KEY (`coordenador_id`, `cidade_id`)

### Tabela: `auditoria`
- `id`: INTEGER, PRIMARY KEY
- `timestamp`: TEXT, NOT NULL (Formato ISO 8601)
- `coordenador_id`: INTEGER, FOREIGN KEY (`coordenadores.id`)
- `acao`: TEXT, NOT NULL (ex: "VALIDATE_PARTICIPANT", "CREATE_USER")
- `detalhes`: TEXT

## 6. Requisitos Funcionais e Fluxos

### Fluxo 1: Área Pública e Login (Home.py)

1.  **Inscrição de Participante:** (Visível para todos)
    - Formulário com os campos necessários.
    - **Regra:** Um e-mail não pode ser cadastrado duas vezes para o mesmo evento.

2.  **Emissão de Certificado:** (Visível para todos)
    - Campo para inserir o e-mail e obter o PDF.
    - **Regras:** Validar se o e-mail existe e se a participação foi confirmada.

3.  **Login de Coordenadores:** (Visível para todos, geralmente em uma `st.sidebar` ou `st.expander`)
    - Campos: `email` e `senha` (`type='password'`).
    - **Ação:** Após o clique no botão "Entrar", a `auth.py` deve ser chamada para validar as credenciais contra a tabela `coordenadores`. Se for válido, popular o `st.session_state`.

### Fluxo 2: Área do Coordenador (pages/1_✅_Validação_de_Participantes.py)

1.  **Proteção de Acesso:** A primeira linha desta página deve verificar o `st.session_state`. Se o usuário não estiver logado, exiba uma mensagem de erro e pare a execução com `st.stop()`.
2.  **Dashboard de Validação:** A tabela de participantes deve ser renderizada usando `st.data_editor`.
3.  **Ação de Validação:** Um botão "Validar Selecionados" aplicará as mudanças feitas no `st.data_editor` ao banco de dados.

### Fluxo 3: Área do Superadmin (pages/2_⚙️_Administração.py)

1.  **Proteção de Acesso Duplo:** Verificar se o usuário está logado E se `st.session_state.user_is_superadmin == True`.
2.  **Funcionalidades:** CRUDs para Coordenadores, Eventos, Cidades e Funções.

## 7. Detalhes Técnicos de Implementação

- **Criptografia:** Usar `cryptography.Fernet` com a chave no `.env` para os campos `nome_completo` e `email` da tabela `participantes`.
- **Serviço de E-mail:** Usar credenciais do Brevo no `.env`. Os textos dos e-mails devem ser criativos e profissionais.
- **Nome do PDF:** `Certificado-PintOfScience-<ANO>-<UUID_CURTO>.pdf`.

## 8. Padrões de Implementação Específicos do Streamlit

Para garantir uma implementação robusta e idiomática, os seguintes padrões devem ser adotados:

1.  **Gerenciamento de Autenticação e Sessão:**
    - **CURRENT IMPLEMENTATION**: Uses `streamlit-authenticator` library for all authentication
    - The library automatically manages `st.session_state` and cookies
    - Session state is populated by `auth_manager.handle_login_result()`:
      ```python
      # In app/auth.py - handle_login_result() method
      st.session_state[SESSION_KEYS["logged_in"]] = True
      st.session_state[SESSION_KEYS["user_id"]] = coordenador.id
      st.session_state[SESSION_KEYS["user_email"]] = coordenador.email
      st.session_state[SESSION_KEYS["user_name"]] = coordenador.nome
      st.session_state[SESSION_KEYS["is_superadmin"]] = coordenador.is_superadmin
      ```
    - **IMPORTANT**: Always use `SESSION_KEYS` dict from `app/auth.py` when accessing session state
    - Pages are protected using helper functions:
      ```python
      from app.auth import require_login, require_superadmin

      # For coordinator pages:
      require_login()  # Checks auth and calls st.stop() if not logged in

      # For superadmin pages:
      require_superadmin()  # Checks both login and superadmin status
      ```
    - The old manual approach with direct `st.session_state` checks is **DEPRECATED**

2.  **Tabelas de Dados Interativas:**
    - Para a tela de validação de participantes, use o componente `st.data_editor`. Ele permite a edição direta na interface (como marcar checkboxes de validação), além de oferecer ordenação e filtragem nativas, cumprindo o requisito de "DataTable".
    - O resultado do `st.data_editor` pode ser comparado com o estado original para identificar quais linhas foram alteradas pelo coordenador.

3.  **Navegação e Estrutura Multi-Página:**
    - A estrutura de arquivos com `Home.py` e o diretório `pages/` será usada para criar a navegação na barra lateral automaticamente.
    - Um botão de "Logout" deve ser implementado. Sua função será limpar o `st.session_state` (usando `st.session_state.clear()`) e recarregar a página.

## 9. Sugestão de Prompts Iniciais para o Gemini CLI

Os prompts iniciais continuam válidos, e agora a IA terá um contexto muito mais rico para gerar o código de autenticação e das páginas interativas.

1.  **Estrutura e Configuração:**

    ```bash
    gemini -o project_setup.py "Baseado no arquivo GEMINI_BRIEF.md (v2), crie a estrutura de diretórios e arquivos vazios para o projeto Pint of Science..."
    ```
2.  **Modelos de Dados:**

    ```bash
    gemini -o app/models.py "Baseado na seção 5 do GEMINI_BRIEF.md (v2), gere o código Python completo para o arquivo app/models.py..."
    ```
3.  **Lógica de Autenticação:**
    ```bash
    gemini -o app/auth.py "Crie o código para app/auth.py. A função    principal deve receber email e senha, verificar no banco de dados (tabela coordenadores) e usar o padrão de st.session_state descrito na seção 8 do GEMINI_BRIEF.md (v2) para gerenciar a sessão."

    ```

## Tooling for shell interactions

- Is it about finding FILES? use `fd`
- Is it about finding TEXT/strings? use `rg`
- Is it about finding CODE STRUCTURE? use `ast-grep`
- Is it about SELECTING from multiple results? pipe to `fzf`
- Is it about interacting with JSON? use `jq`
- Is it about interacting with YAML or XML? use `yq`

## Avoid creating unnecessary files
- Only create files that are explicitly requested or clearly needed based on the context.
- Do not create placeholder files unless they serve a specific purpose in the project structure.
- Do not create .md files for applied fixes, summaries, or migrations unless explicitly requested.