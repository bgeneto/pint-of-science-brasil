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
- **Variáveis de Ambiente:** Arquivo `.env`

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
    - O estado de login do usuário **DEVE** ser gerenciado através do `st.session_state`.
    - Ao realizar o login com sucesso, armazene as informações do usuário na sessão. Exemplo:
      ```python
      # Em auth.py, após validar a senha
      st.session_state['logged_in'] = True
      st.session_state['user_id'] = user.id
      st.session_state['user_email'] = user.email
      st.session_state['is_superadmin'] = user.is_superadmin
      ```
    - As páginas restritas (`pages/*.py`) **DEVEM** iniciar com um bloco de verificação:
      ```python
      import streamlit as st

      if 'logged_in' not in st.session_state or not st.session_state.logged_in:
          st.error("⚠️ Você precisa estar logado para acessar esta página.")
          st.stop() # Interrompe a execução do script
      ```

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

## Tooling for shell interactions (install if missing)

- Is it about finding FILES? use `fd`
- Is it about finding TEXT/strings? use `rg`
- Is it about finding CODE STRUCTURE? use `ast-grep`
- Is it about SELECTING from multiple results? pipe to `fzf`
- Is it about interacting with JSON? use `jq`
- Is it about interacting with YAML or XML? use `yq`
