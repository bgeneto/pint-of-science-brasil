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
pint-of-science-brasil/
├── 🏠_Home.py               # Página principal (pública)
├── app/                    # Módulos principais
│   ├── __init__.py        # Inicialização do pacote
│   ├── core.py            # Configurações e ambiente
│   ├── models.py          # Modelos de dados (SQLAlchemy + Pydantic)
│   ├── db.py              # Gerenciamento do banco de dados
│   ├── auth.py            # Autenticação e sessão
│   ├── services.py        # Lógica de negócio
│   └── utils.py           # Funções utilitárias
├── pages/                 # Páginas restritas
│   ├── 1_👨‍👨‍👦‍👦_Participantes.py    # Área de coordenadores (validação)
│   ├── 2_⚙️_Administração.py         # Área de superadmin
│   └── 3_✅_Validar_Certificado.py   # Validação pública de certificados
├── static/                # Arquivos estáticos e configurações
│   ├── certificate_config.json     # Configurações visuais e carga horária
│   └── 2024/, 2025/               # Imagens por ano do evento
├── data/                  # Banco de dados SQLite
├── docs/                  # Documentação técnica
├── tests/                 # Testes automatizados
├── utils/                 # Scripts utilitários e migrações
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de configuração
└── README.md            # Este arquivo
```

## 🚀 Funcionalidades

### Para Participantes (Público)
- ✅ Formulário de inscrição com validação
- ✅ Download de certificados por e-mail
- ✅ **Validação de autenticidade de certificados** - Verifique certificados online via hash HMAC-SHA256
- ✅ Interface responsiva e intuitiva
- ✅ Página pública de validação com link direto do certificado

### Para Coordenadores (Acesso Restrito)
- ✅ Login seguro com autenticação persistente
- ✅ Dashboard com estatísticas de participantes
- ✅ Validação em lote de participantes
- ✅ Filtros por cidade, função e status
- ✅ Visualização de detalhes dos participantes
- ✅ Editor interativo de dados (data_editor)

### Para Superadmin (Acesso Restrito)
- ✅ Gestão completa de coordenadores
- ✅ CRUD de eventos, cidades e funções
- ✅ Dashboard com métricas do sistema
- ✅ Visualização de logs de auditoria
- ✅ Gerenciamento de usuários
- ✅ **Configuração visual de certificados por ano do evento**
  - Upload de imagens (logo, assinatura, patrocinadores) isoladas por ano
  - Personalização de paleta de cores por ano
  - Preview visual das cores em tempo real
  - Gerenciamento através de interface intuitiva
- ✅ **Configuração de carga horária por ano do evento**
  - Definição de horas por dia de participação (1-24h)
  - Definição de carga horária total do evento (1-200h)
  - Seleção de funções que recebem carga horária total (independente dos dias)
  - Cálculo automático baseado em regras configuráveis
  - Exemplo: Coordenadores recebem 40h independente dos dias trabalhados

## 📦 Tecnologias Utilizadas

- **Python 3.11+**: Linguagem principal
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
- Python 3.11 ou superior
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
# Base Application URL
BASE_URL=https://seu-dominio.com  # URL base para links de validação

# Database Configuration
DATABASE_URL=sqlite:///./data/pint_of_science.db

# Encryption Key (gerar com: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode()))
ENCRYPTION_KEY=sua_chave_de_criptografia_aqui

# Certificate Secret Key (gerar com: import secrets; print(secrets.token_hex(32)))
CERTIFICATE_SECRET_KEY=chave_secreta_64_caracteres_hex

# Brevo Email Service Configuration (opcional)
BREVO_API_KEY=sua_chave_api_brevo
BREVO_SENDER_EMAIL=seu_email@dominio.com
BREVO_SENDER_NAME=Pint of Science Brasil

# Initial superadmin (opcional, para primeira configuração)
INITIAL_SUPERADMIN_EMAIL=admin@pintofscience.com
INITIAL_SUPERADMIN_PASSWORD=senha_segura_aqui
INITIAL_SUPERADMIN_NAME=Administrador
```

**Notas sobre configuração:**
- `ENCRYPTION_KEY`: Obrigatória. Usada para criptografar dados PII (nome, email)
- `CERTIFICATE_SECRET_KEY`: Recomendada. Se não configurada, uma chave temporária será gerada (não use em produção!)
- `BASE_URL`: Usado para gerar links de validação nos certificados. Padrão: `http://localhost:8501`
- Variáveis Brevo: Opcionais. Sistema funciona sem email, mas participantes não receberão notificações
- Variáveis `INITIAL_SUPERADMIN_*`: Opcionais. Criam um superadmin na primeira inicialização

### Passo 5: Inicializar o Banco de Dados

O sistema utiliza SQLite como banco de dados. Você pode inicializar o banco de duas formas:

#### 5.1: Inicialização Automática (Recomendado)
```bash
# Usando o script de seeding dedicado
python utils/seed_database.py
```

Este script irá:
- ✅ Criar o arquivo `data/pint_of_science.db`
- ✅ Criar todas as tabelas necessárias
- ✅ Popular dados iniciais (cidades, funções, eventos)
- ✅ Criar usuário superadmin (se configurado no `.env`)

#### 5.2: Inicialização Manual
```bash
# Executar o sistema pela primeira vez
streamlit run 🏠_Home.py
```

Na primeira execução do Streamlit, o sistema irá inicializar o banco automaticamente.

#### 5.3: Verificar Status do Banco
```bash
# Ver apenas o status sem modificar
python utils/seed_database.py --status-only

# Ou executar testes completos
python tests/test_system.py
```

**Saída esperada:**
```
🚀 Iniciando testes do sistema Pint of Science Brasil
✅ Todos os arquivos necessários encontrados!
✅ Conexão com o banco de dados bem-sucedida!
✅ Banco de dados inicializado corretamente!
   - 98 cidades cadastradas
   - 34 funções cadastradas
   - 1 eventos cadastrados
🎉 Todos os testes passaram! O sistema está pronto para uso.
```

#### 5.4: Dados Iniciais Criados

**Cidades (98 cidades):**
- Todas as capitais brasileiras e principais cidades do interior

**Funções (34 funções):**
- Organizador(a), Voluntário(a), Palestrante, Moderador(a)
- Coordenador(a) Local/Regional, Apoio Técnico, Divulgação
- E outras funções específicas do evento

**Eventos:**
- Pint of Science 2025 (datas: 19-21 de maio)

**Coordenadores de Teste:**
- Um coordenador de teste é criado durante os testes: `teste@exemplo.com` / `senha123`
- Um participante de teste é criado: `participante@exemplo.com`

#### 5.5: Solução de Problemas

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

#### 5.6: Reset/Recriação do Banco (Desenvolvimento)

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
streamlit run 🏠_Home.py
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

- **Criptografia de Dados**: Nomes e e-mails de participantes são criptografados (Fernet)
- **Hash de Senhas**: Senhas armazenadas com bcrypt
- **Validação de Certificados**: HMAC-SHA256 para verificar autenticidade **sem armazenar PDFs**
- **Sessão Segura**: Timeout de sessão (2 horas) com persistência via cookie
- **Proteção contra Brute Force**: Limite de tentativas de login
- **Validação de Entrada**: Todos os dados são validados com Pydantic
- **Auditoria**: Todas as ações importantes são registradas
- **Hash de Email**: SHA-256 para lookups sem expor dados criptografados

### 🔒 Sistema de Validação de Certificados

Todos os certificados emitidos incluem:
- **Hash único de validação** (HMAC-SHA256) no rodapé do certificado
- **Link clicável** para verificação online instantânea
- **Impossível falsificar** sem a chave secreta (`CERTIFICATE_SECRET_KEY`)
- **Sem armazenamento de PDFs** - hash é gerado dinamicamente dos dados do participante
- **Verificação criptográfica** usando `hmac.compare_digest()` para prevenir timing attacks

**Como funciona:**
1. Ao gerar o certificado, um hash HMAC é criado com: `id|evento_id|email|nome`
2. Hash é armazenado no banco de dados e impresso no certificado
3. Link no certificado direciona para página pública de validação
4. Sistema verifica hash recalculando com dados do banco
5. Resultado mostra se certificado é autêntico e exibe detalhes

Qualquer pessoa pode validar um certificado acessando a página `/Validar_Certificado` ou clicando no link do próprio certificado.

📚 **Documentação técnica completa**: [`docs/CERTIFICATE_VALIDATION.md`](docs/CERTIFICATE_VALIDATION.md)
- **Proteção contra Brute Force**: Limite de tentativas de login
- **Validação de Entrada**: Todos os dados são validados com Pydantic
- **Auditoria**: Todas as ações importantes são registradas

### Sistema de Validação de Certificados

Todos os certificados emitidos incluem:
- **Hash único de validação** (HMAC-SHA256) no rodapé
- **Link clicável** para verificação online
- **Impossível falsificar** sem a chave secreta

Qualquer pessoa pode validar um certificado em `/Validar_Certificado`.

� **Documentação completa**: [`docs/CERTIFICATE_VALIDATION.md`](docs/CERTIFICATE_VALIDATION.md)

##  Fluxo de Trabalho

1. **Inscrição**: Participantes se registram através do formulário público
2. **Validação**: Coordenadores acessam a área restrita e validam as participações
3. **Emissão**: Sistema gera certificados PDF personalizados com:
   - Hash de validação HMAC-SHA256 único e não-forjável
   - Design visual específico do ano do evento (cores e imagens)
   - **Carga horária calculada baseada em regras configuráveis por ano**
   - Link clicável para verificação online
4. **Download**: Participantes baixam certificados usando e-mail de cadastro
5. **Verificação**: Qualquer pessoa pode validar autenticidade do certificado online através do link ou página pública

## 🎨 Configuração Visual por Ano do Evento

### Sistema de Multi-Year Configuration

O sistema mantém **configurações visuais isoladas por ano do evento**, garantindo que certificados de anos diferentes mantenham sua identidade visual original, mesmo quando gerados posteriormente.

#### Estrutura de Configuração

```
static/
├── 2024/
│   ├── pint_logo.png           # Logo do evento de 2024
│   ├── pint_signature.png      # Assinatura de 2024
│   └── sponsor_logo.png        # Patrocinadores de 2024
├── 2025/
│   ├── pint_logo.png           # Logo do evento de 2025
│   ├── pint_signature.png      # Assinatura de 2025
│   └── sponsor_logo.png        # Patrocinadores de 2025
└── certificate_config.json     # Configurações de cores e caminhos
```

#### Configuração no Admin

Superadmins podem configurar através da aba **"🖼️ Certificado"**:

1. **Upload de Imagens por Ano**:
   - Selecione o ano do evento
   - Faça upload de 3 imagens: Logo Pint, Assinatura, Logo Patrocinador
   - Formatos aceitos: PNG, JPG, WEBP (máx. 2MB)
   - Arquivos salvos automaticamente em `static/{ANO}/`

2. **Personalização de Cores por Ano**:
   - Selecione o ano do evento
   - Configure 4 cores com color pickers:
     - **Cor Primária**: Barra lateral do certificado
     - **Cor Secundária**: Título "CERTIFICADO DE PARTICIPAÇÃO"
     - **Cor do Texto**: Texto principal do certificado
     - **Cor de Destaque**: Nome do participante e cidade
   - Preview visual em tempo real
   - Configuração salva em `certificate_config.json`

#### Exemplo de Configuração JSON

```json
{
  "2024": {
    "cores": {
      "cor_primaria": "#e74c3c",
      "cor_secundaria": "#c0392b",
      "cor_texto": "#2c3e50",
      "cor_destaque": "#f39c12"
    },
    "imagens": {
      "pint_logo": "2024/pint_logo.png",
      "pint_signature": "2024/pint_signature.png",
      "sponsor_logo": "2024/sponsor_logo.png"
    }
  },
  "2025": {
    "cores": {
      "cor_primaria": "#e74c3c",
      "cor_secundaria": "#c0392b",
      "cor_texto": "#2c3e50",
      "cor_destaque": "#f39c12"
    },
    "imagens": {
      "pint_logo": "2025/pint_logo.png",
      "pint_signature": "2025/pint_signature.png",
      "sponsor_logo": "2025/sponsor_logo.png"
    },
    "carga_horaria": {
      "horas_por_dia": 8,
      "horas_por_evento": 40,
      "funcoes_evento_completo": [1, 2, 3, 10, 11]
    }
  },
  "_default": {
    "cores": { "..." },
    "imagens": { "..." }
  }
}
```

#### Benefícios

- **Preservação Histórica**: Certificados de anos anteriores mantêm design original
- **Flexibilidade**: Cada ano pode ter branding diferente
- **Regeneração Segura**: Certificados podem ser regenerados no futuro com visual correto
- **Gestão Simples**: Interface intuitiva sem necessidade de editar arquivos manualmente

## ⏱️ Configuração de Carga Horária por Ano do Evento

### Sistema de Cálculo Flexível de Carga Horária

O sistema permite **configurar regras específicas de cálculo de carga horária** para cada ano do evento, garantindo flexibilidade na emissão de certificados baseada em funções e participação.

**Importante**: A carga horária não é mais armazenada no banco de dados. Ela é **calculada dinamicamente** a partir das regras configuradas no `certificate_config.json`, garantindo que mudanças nas regras afetem imediatamente novos certificados gerados.

#### Funcionalidades da Configuração

Superadmins podem configurar através da aba **"⏱️ Carga Horária"**:

1. **Horas por Dia de Participação**:
   - Define quantas horas equivalem a 1 dia de participação
   - Valor padrão: 4 horas
   - Faixa: 1-24 horas
   - Aplicado a participantes com funções comuns

2. **Horas Totais do Evento**:
   - Define carga horária total para funções especiais
   - Valor padrão: 40 horas
   - Faixa: 1-200 horas
   - Independente da quantidade de dias trabalhados

3. **Funções com Carga Horária Total**:
   - Seleção múltipla de funções que recebem CH total
   - Aplicado independente dos dias de participação
   - Exemplos: Coordenador(a) Local, Regional, Organizador(a)
   - Interface intuitiva com nomes legíveis

#### Lógica de Cálculo

O sistema utiliza lógica condicional inteligente:

```python
def calcular_carga_horaria(funcao_id, dias_participacao, ano_evento):
    config = carregar_configuracao(ano_evento)

    # Verificar se função tem direito a carga horária total
    if funcao_id in config['funcoes_evento_completo']:
        return config['horas_por_evento']  # Ex: 40h sempre

    # Caso contrário, calcular por dias
    return dias_participacao * config['horas_por_dia']  # Ex: 3 dias × 8h = 24h
```

#### Exemplo Prático de Aplicação

**Configuração para Pint of Science 2025**:
```json
{
  "horas_por_dia": 8,
  "horas_por_evento": 40,
  "funcoes_evento_completo": [1, 2, 3, 10, 11]
}
```

**Resultados nos Certificados**:

| Participante | Função | Dias | Carga Horária | Cálculo |
|--------------|--------|------|---------------|---------|
| João Silva | Palestrante | 3 dias | **24h** | 3 × 8h |
| Maria Santos | Coord. Local (ID 1) | 2 dias | **40h** | Total evento |
| Pedro Costa | Organizador (ID 5) | 1 dia | **8h** | 1 × 8h |
| Ana Lima | Coord. Regional (ID 2) | 3 dias | **40h** | Total evento |

#### Estrutura de Configuração

**Arquivo**: `static/certificate_config.json`

```json
{
  "2025": {
    "cores": { ... },
    "imagens": { ... },
    "carga_horaria": {
      "horas_por_dia": 8,
      "horas_por_evento": 40,
      "funcoes_evento_completo": [1, 2, 3, 10, 11]
    }
  }
}
```

#### Benefícios

- **Flexibilidade Total**: Cada ano pode ter regras diferentes
- **Justiça nas Atribuições**: Funções especiais recebem reconhecimento adequado
- **Automação**: Cálculo automático sem intervenção manual
- **Transparência**: Regras claras e documentadas
- **Atualização Imediata**: Mudanças nas regras afetam novos certificados instantaneamente
- **Histórico Preservado**: Certificados regenerados sempre usam regras atuais do ano

#### Interface do Usuário

A configuração oferece:
- ✅ Seletor de ano do evento
- ✅ Inputs numéricos com validação
- ✅ Multiselect de funções com nomes legíveis
- ✅ Preview de métricas em tempo real
- ✅ Exemplos práticos de aplicação
- ✅ Feedback visual de sucesso/erro
- ✅ Validações automáticas

#### Documentação Técnica

- **[CONFIGURACAO_CARGA_HORARIA.md](docs/CONFIGURACAO_CARGA_HORARIA.md)** - Documentação técnica completa
- **[RESUMO_IMPLEMENTACAO_CARGA_HORARIA.md](docs/RESUMO_IMPLEMENTACAO_CARGA_HORARIA.md)** - Resumo da implementação
- **[IMPLEMENTACAO_CONCLUIDA.md](docs/IMPLEMENTACAO_CONCLUIDA.md)** - Guia rápido

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
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "🏠_Home.py", "--server.address=0.0.0.0"]
```

## 📝 Estrutura do Banco de Dados

### Tabelas Principais
- **eventos**: Informações dos eventos (ano, datas em JSON)
- **cidades**: Cidades participantes (nome, estado UF)
- **funcoes**: Funções dos participantes (Organizador, Voluntário, etc.)
- **coordenadores**: Usuários do sistema (com senha hash bcrypt, session_token para persistência)
- **participantes**: Dados dos participantes com:
  - `nome_completo_encrypted` e `email_encrypted` (BLOB, Fernet)
  - `email_hash` (SHA-256 para lookups, STRING 64 chars)
  - `hash_validacao` (HMAC-SHA256 para validação de certificados, STRING 64 chars, UNIQUE)
  - Dados de validação e participação
  - **Carga horária calculada dinamicamente** (não armazenada no banco)
- **coordenador_cidade_link**: Relacionamento N:N entre coordenadores e cidades
- **auditoria**: Registro de ações do sistema (timestamp, coordenador_id, ação, detalhes)

### Migrations Necessárias

Se estiver atualizando de uma versão anterior, execute as migrations em ordem:

```bash
# 1. Adicionar coluna hash_validacao se não existir (para validação de certificados)
python utils/add_hash_validacao_column.py

# 2. Remover coluna carga_horaria_calculada (sistema agora calcula dinamicamente)
python utils/migrate_drop_carga_horaria_column.py
```

Estes scripts verificam e modificam a estrutura do banco de forma segura (idempotente).

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

- [x] ✅ Sistema de validação de certificados com HMAC-SHA256
- [x] ✅ Configuração visual de certificados por ano do evento
- [x] ✅ **Configuração de carga horária flexível por ano do evento (calculada dinamicamente)**
- [x] ✅ Sessão persistente com cookie para coordenadores
- [x] ✅ Sistema de notificações por email para participantes
- [x] ✅ **Refatoração: Remoção da coluna carga_horaria_calculada do banco de dados**
- [ ] Implementar testes unitários automatizados (pytest)
- [ ] Adicionar suporte a múltiplos idiomas (i18n)
- [ ] Dashboard avançado com analytics e gráficos
- [ ] API REST para integração externa
- [ ] Exportação de dados em formatos CSV/Excel


## 📚 Documentação Adicional

- **[CERTIFICATE_VALIDATION.md](docs/CERTIFICATE_VALIDATION.md)** - Documentação técnica completa do sistema de validação
- **[QUICKSTART_VALIDATION.md](docs/QUICKSTART_VALIDATION.md)** - Guia rápido de instalação e configuração
- **[CONFIGURACAO_CARGA_HORARIA.md](docs/CONFIGURACAO_CARGA_HORARIA.md)** - Documentação técnica da configuração de carga horária
- **[RESUMO_IMPLEMENTACAO_CARGA_HORARIA.md](docs/RESUMO_IMPLEMENTACAO_CARGA_HORARIA.md)** - Resumo da implementação da carga horária
- **[IMPLEMENTACAO_CONCLUIDA.md](docs/IMPLEMENTACAO_CONCLUIDA.md)** - Guia rápido da implementação concluída
- **[static/README.md](static/README.md)** - Documentação sobre estrutura de imagens e configurações visuais
- **[CLAUDE.md](CLAUDE.md)** - Brief original do projeto com requisitos completos
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Guia de arquitetura para desenvolvimento com IA

---

**Desenvolvido com ❤️ para a comunidade Pint of Science Brasil**
