# Implementation Plan

## Overview
Implementar um sistema web completo de gerenciamento e emissão de certificados para o evento Pint of Science Brasil, utilizando Python 3.13+ com Streamlit, SQLite3 e criptografia de dados sensíveis.

O sistema atenderá três tipos de usuários: participantes (público), coordenadores de cidade (admin restrito) e coordenador geral (superadmin), com funcionalidades de inscrição, validação de participações e emissão de certificados em PDF.

## Types
Definir modelos de dados Pydantic para validação e modelos SQLAlchemy para ORM, incluindo criptografia para campos sensíveis.

### Modelos de Dados Principais:

**Evento:**
- id: int (PK, autoincrement)
- ano: int (NOT NULL, UNIQUE)
- datas_evento: str (NOT NULL, descrição textual)
- data_criacao: str (NOT NULL, ISO 8601)

**Cidade:**
- id: int (PK, autoincrement)
- nome: str (NOT NULL)
- estado: str (NOT NULL, 2 caracteres)

**Funcao:**
- id: int (PK, autoincrement)
- nome_funcao: str (NOT NULL, UNIQUE)

**Coordenador:**
- id: int (PK, autoincrement)
- nome: str (NOT NULL)
- email: str (NOT NULL, UNIQUE)
- senha_hash: str (NOT NULL)
- is_superadmin: bool (NOT NULL, DEFAULT False)

**Participante:**
- id: int (PK, autoincrement)
- nome_completo_encrypted: bytes (NOT NULL)
- email_encrypted: bytes (NOT NULL)
- titulo_apresentacao: str (Optional)
- evento_id: int (FK eventos.id)
- cidade_id: int (FK cidades.id)
- funcao_id: int (FK funcoes.id)
- datas_participacao: str (NOT NULL)
- carga_horaria_calculada: int (NOT NULL)
- validado: bool (NOT NULL, DEFAULT False)
- data_inscricao: str (NOT NULL, ISO 8601)

**CoordenadorCidadeLink (N:N):**
- coordenador_id: int (FK coordenadores.id)
- cidade_id: int (FK cidades.id)
- PRIMARY KEY (coordenador_id, cidade_id)

**Auditoria:**
- id: int (PK, autoincrement)
- timestamp: str (NOT NULL, ISO 8601)
- coordenador_id: int (FK coordenadores.id)
- acao: str (NOT NULL)
- detalhes: str (Optional)

## Files
Criar estrutura completa de diretórios e arquivos seguindo princípios de separação de responsabilidades e injeção de dependência.

### Novos Arquivos:

**Arquivos Principais:**
- Home.py - Página principal com inscrição, download e login
- requirements.txt - Dependências do projeto
- .env.example - Template de configurações

**Módulo app/:**
- app/__init__.py - Inicialização do pacote
- app/models.py - Modelos Pydantic e SQLAlchemy
- app/services.py - Lógica de negócio
- app/db.py - Conexão e inicialização do DB
- app/core.py - Configurações e carregamento .env
- app/auth.py - Autenticação de coordenadores
- app/utils.py - Funções utilitárias

**Páginas Restritas:**
- pages/1_✅_Validação_de_Participantes.py - Dashboard de coordenadores
- pages/2_⚙️_Administração.py - Área do superadmin

**Recursos Estáticos:**
- static/.gitkeep - Manter diretório

## Functions
Implementar funções de negócio seguindo princípios de injeção de dependência e separação de responsabilidades.

### Novas Funções:

**app/services.py:**
- criptografar_dados_sensiveis(dados: str, chave: bytes) -> bytes
- descriptografar_dados_sensiveis(dados_encrypted: bytes, chave: bytes) -> str
- calcular_carga_horaria(datas_participacao: List[str], evento_datas: List[str]) -> int
- gerar_certificado_pdf(participante: Participante, evento: Evento) -> bytes
- enviar_email_confirmacao(email: str, dados_inscricao: dict) -> bool
- enviar_email_certificado_liberado(email: str, link_download: str) -> bool
- validar_participante(participante_id: int, coordenador_id: int, db_session: Session) -> bool

**app/auth.py:**
- autenticar_coordenador(email: str, senha: str, db_session: Session) -> Optional[Coordenador]
- criar_coordenador(dados: dict, db_session: Session) -> Coordenador
- verificar_permissao_coordenador_cidade(coordenador_id: int, cidade_id: int, db_session: Session) -> bool

**app/utils.py:**
- gerar_uuid_curto() -> str
- formatar_data_iso(data: datetime) -> str
- validar_email(email: str) -> bool
- gerar_senha_hash(senha: str) -> str
- verificar_senha_hash(senha: str, hash_armazenado: str) -> bool

## Classes
Implementar classes de modelos e serviços seguindo princípios de SOLID e boas práticas de programação Python.

### Novas Classes:

**app/models.py (Modelos Pydantic):**
- EventoBase, EventoCreate, EventoRead
- CidadeBase, CidadeCreate, CidadeRead
- FuncaoBase, FuncaoCreate, FuncaoRead
- CoordenadorBase, CoordenadorCreate, CoordenadorRead, CoordenadorLogin
- ParticipanteBase, ParticipanteCreate, ParticipanteRead
- AuditoriaBase, AuditoriaCreate

**app/models.py (Modelos SQLAlchemy):**
- Evento, Cidade, Funcao, Coordenador, Participante, Auditoria
- CoordenadorCidadeLink (tabela associativa)

**app/services.py:**
- GeradorCertificado
- ServicoEmail
- ServicoCriptografia
- ServicoValidacao

**app/db.py:**
- GerenciadorBancoDados
- RepositorioParticipantes
- RepositorioCoordenadores

## Dependencies
Configurar dependências modernas e otimizadas para desenvolvimento Python com Streamlit.

### Dependências Principais:
- streamlit>=1.28.0
- sqlalchemy>=2.0.0
- pydantic>=2.0.0
- cryptography>=41.0.0
- python-dotenv>=1.0.0
- reportlab>=4.0.0
- aiosqlite>=0.19.0
- pillow>=10.0.0
- bcrypt>=4.0.0

### Dependências de Desenvolvimento:
- pytest>=7.0.0
- pytest-asyncio>=0.21.0
- black>=23.0.0
- isort>=5.12.0
- flake8>=6.0.0

## Testing
Implementar testes unitários e de integração para garantir robustez do sistema.

### Estrutura de Testes:
- tests/test_models.py - Testes de modelos Pydantic
- tests/test_services.py - Testes de serviços de negócio
- tests/test_auth.py - Testes de autenticação
- tests/test_db.py - Testes de operações de banco
- tests/test_integration.py - Testes de fluxos completos

### Estratégias de Validação:
- Testes unitários para cada função de negócio
- Testes de criptografia/descriptografia
- Testes de autenticação e autorização
- Testes de geração de certificados PDF
- Testes de envio de e-mails (mock)

## Implementation Order
Executar implementação em ordem lógica para minimizar dependências e facilitar validação incremental.

1. **Estrutura Base e Configuração:** Criar diretórios, arquivos de configuração e setup inicial
2. **Modelos de Dados:** Implementar modelos Pydantic e SQLAlchemy com validação
3. **Banco de Dados:** Criar sistema de inicialização e migração do SQLite
4. **Autenticação:** Implementar sistema de login e gerenciamento de sessão
5. **Lógica de Negócio:** Desenvolver serviços de criptografia, e-mail e validação
6. **Interface Pública:** Criar página Home com inscrição e download
7. **Área Restrita Coordenador:** Implementar dashboard de validação
8. **Área Administrativa:** Desenvolver interface de superadmin
9. **Geração de Certificados:** Implementar PDF generation e download
10. **Testes e Validação:** Criar suíte de testes e validação final
