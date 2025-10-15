# Configurações Avançadas

Guia completo para configurações técnicas e integrações externas do Sistema Pint of Science Brasil.

## 🎯 O que são Configurações Avançadas?

Parâmetros técnicos que controlam:

- 🔒 Criptografia de dados
- 📧 Envio de e-mails (integração Brevo)
- 💾 Conexão com banco de dados
- 🔐 Sessões e autenticação
- ⚙️ Comportamento do sistema

!!! warning "Usuários Avançados"

    Estas configurações requerem conhecimento técnico. Alterações incorretas podem quebrar o sistema.

## 📁 Arquivo de Configuração

### .env

Arquivo de ambiente na raiz do projeto:

```
pint-of-science-brasil/
├── .env                    # ← Arquivo de configuração
├── 🏠_Home.py
├── requirements.txt
├── app/
├── data/
└── static/
```

### Estrutura do .env

```bash
# Banco de Dados
DATABASE_URL=sqlite:///data/pint_of_science.db

# Criptografia
ENCRYPTION_KEY=sua_chave_fernet_base64_aqui

# E-mail (Brevo)
BREVO_API_KEY=sua_chave_api_brevo
BREVO_SENDER_EMAIL=contato@pintofscience.com.br

# Autenticação (opcional)
SESSION_EXPIRY_DAYS=30
```

## 🔒 Configuração de Criptografia

### ENCRYPTION_KEY

**O que é**: Chave Fernet para criptografar dados pessoais (nome e e-mail) no banco de dados.

**Formato**: String Base64 de 44 caracteres

**Como gerar**:

```bash
# Via Python
python utils/generate_certificate_key.py
```

Ou manualmente:

```python
from cryptography.fernet import Fernet

# Gerar nova chave
key = Fernet.generate_key()
print(key.decode())
```

Saída (exemplo):

```
vQv8hJ3KN8Y_7rZ2mL5pX9nT4wB6sU1cD0eF2gH3iJ4=
```

**Configuração no .env**:

```bash
ENCRYPTION_KEY=vQv8hJ3KN8Y_7rZ2mL5pX9nT4wB6sU1cD0eF2gH3iJ4=
```

!!! danger "CRÍTICO"

    - **NUNCA comite** `.env` no Git (já está no `.gitignore`)
    - **Faça backup** da chave em local seguro
    - **Se perder a chave**, dados criptografados serão irrecuperáveis
    - **Não altere** após criptografar dados (não será possível descriptografar)

## 📧 Configuração de E-mail

### Serviço Brevo (SendinBlue)

O sistema usa **Brevo** para envio de e-mails transacionais.

### Obter Credenciais Brevo

1. Crie conta em: https://www.brevo.com/
2. Plano gratuito: 300 e-mails/dia
3. Acesse: **Settings** → **SMTP & API** → **API Keys**
4. Crie nova API Key
5. Copie a chave (exemplo: `xkeysib-abc123...`)

### Configurar no .env

```bash
# API Key do Brevo
BREVO_API_KEY=xkeysib-abc123def456ghi789jkl012mno345pqr678stu901

# E-mail remetente (deve ser verificado no Brevo)
BREVO_SENDER_EMAIL=contato@pintofscience.com.br
```

### Verificar E-mail Remetente

No painel Brevo:

1. **Senders** → **Add a Sender**
2. Digite e-mail que será usado
3. Confirme verificação por e-mail
4. Use esse e-mail em `BREVO_SENDER_EMAIL`

### Desativar Envio de E-mail

Se não quiser usar e-mail:

```bash
# Deixe vazio ou comente
# BREVO_API_KEY=
# BREVO_SENDER_EMAIL=
```

Sistema detecta automaticamente e desativa recursos de e-mail.

## 💾 Configuração de Banco de Dados

### DATABASE_URL

**O que é**: String de conexão com banco de dados.

**Padrão (SQLite)**:

```bash
DATABASE_URL=sqlite:///data/pint_of_science.db
```

Cria arquivo em: `pint-of-science-brasil/data/pint_of_science.db`

### Usar Caminho Absoluto

```bash
DATABASE_URL=sqlite:////home/usuario/dados/pint.db
```

Observe: 4 barras (`////`) para caminho absoluto.

### Outros Bancos (PostgreSQL, MySQL)

O sistema suporta via SQLAlchemy:

**PostgreSQL**:

```bash
DATABASE_URL=postgresql://usuario:senha@localhost:5432/pint_db
```

**MySQL**:

```bash
DATABASE_URL=mysql://usuario:senha@localhost:3306/pint_db
```

!!! warning "Requer Dependências"

    Instale drivers adicionais:
    ```bash
    pip install psycopg2-binary  # PostgreSQL
    pip install pymysql          # MySQL
    ```

## 🔐 Configuração de Sessões

### SESSION_EXPIRY_DAYS

**O que é**: Tempo em dias que sessão de login permanece ativa.

**Padrão**: 30 dias

**Configuração**:

```bash
SESSION_EXPIRY_DAYS=30
```

**Valores comuns**:

- `1` - Sessão expira em 1 dia (mais seguro)
- `7` - Sessão expira em 1 semana
- `30` - Sessão expira em 1 mês (padrão)
- `90` - Sessão expira em 3 meses

## ⚙️ Outras Configurações

### APP_NAME

Nome da aplicação (usado em títulos):

```bash
APP_NAME="Pint of Science Brasil"
```

### DEBUG_MODE

Ativar modo debug (apenas desenvolvimento):

```bash
DEBUG_MODE=true
```

!!! danger "Produção"

    NUNCA ative debug em produção. Expõe informações sensíveis.

## 🚀 Aplicando Configurações

### Após Editar .env

1. **Salve o arquivo** `.env`
2. **Reinicie a aplicação**:

   ```bash
   # Parar aplicação atual (Ctrl+C)
   # Iniciar novamente
   streamlit run 🏠_Home.py
   ```

3. **Verificar carregamento**:
   - Sistema lê `.env` na inicialização
   - Configurações são carregadas em `app/core.py`
   - Use `settings` para acessar valores

## 🧪 Testando Configurações

### Teste de E-mail

```python
# arquivo: utils/testar_email.py
from app.core import settings

print(f"E-mail configurado: {settings.is_email_configured}")
print(f"Remetente: {settings.brevo_sender_email}")
```

### Teste de Criptografia

```python
# arquivo: utils/testar_criptografia.py
from app.services import servico_criptografia

# Tentar criptografar
texto = "teste@email.com"
encrypted = servico_criptografia.criptografar_email(texto)
decrypted = servico_criptografia.descriptografar(encrypted)

print(f"Original: {texto}")
print(f"Criptografado: {encrypted}")
print(f"Descriptografado: {decrypted}")
print(f"✅ Criptografia OK: {texto == decrypted}")
```

### Teste de Banco

```python
# arquivo: utils/testar_banco.py
from app.db import db_manager

try:
    with db_manager.get_db_session() as session:
        result = session.execute("SELECT 1").scalar()
        print(f"✅ Conexão com banco OK: {result == 1}")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
```

## 🔧 Troubleshooting

### Problema: "ENCRYPTION_KEY not found"

**Causa**: `.env` não existe ou chave não definida

**Solução**:

1. Crie arquivo `.env` na raiz
2. Gere chave: `python utils/generate_certificate_key.py`
3. Adicione em `.env`: `ENCRYPTION_KEY=sua_chave`

---

### Problema: E-mails Não são Enviados

**Causa**: Credenciais Brevo inválidas ou não configuradas

**Solução**:

1. Verifique `BREVO_API_KEY` em `.env`
2. Teste API key no painel Brevo
3. Confirme e-mail remetente verificado
4. Verifique logs de erro do sistema

---

### Problema: Erro ao Conectar Banco

**Causa**: `DATABASE_URL` incorreto ou permissões

**Solução**:

1. Verifique sintaxe de `DATABASE_URL`
2. Confirme que pasta `data/` existe e tem permissões de escrita
3. Para caminho absoluto, use 4 barras: `sqlite:////caminho/completo`

---

### Problema: Sessão Expira Muito Rápido

**Causa**: `SESSION_EXPIRY_DAYS` muito baixo

**Solução**:

1. Edite `.env`: `SESSION_EXPIRY_DAYS=30`
2. Reinicie aplicação
3. Usuários precisam fazer login novamente

---

## 🔒 Segurança

### Boas Práticas

1. **Nunca comite .env**

   ```bash
   # Verificar se está no .gitignore
   grep ".env" .gitignore
   ```

2. **Use senhas fortes**

   - API keys com 32+ caracteres
   - Senhas de banco com 16+ caracteres
   - Não use palavras de dicionário

3. **Rotação de chaves**

   - Troque API keys periodicamente (trimestral)
   - Documente mudanças

4. **Backup seguro**

   - Mantenha cópia de `.env` em local seguro (não na nuvem pública)
   - Use gerenciador de senhas (1Password, Bitwarden)
   - Criptografe backups

5. **Princípio do menor privilégio**
   - Chaves de API com mínimas permissões necessárias
   - Usuários de banco com apenas acessos necessários

### Checklist de Segurança

- [ ] `.env` está no `.gitignore`
- [ ] `ENCRYPTION_KEY` tem backup seguro
- [ ] API keys não estão em código fonte
- [ ] Senhas são fortes (16+ caracteres)
- [ ] `DEBUG_MODE=false` em produção
- [ ] Logs não expõem dados sensíveis

## 📚 Referências

- **Cryptography (Fernet)**: https://cryptography.io/
- **Brevo API Docs**: https://developers.brevo.com/
- **SQLAlchemy URLs**: https://docs.sqlalchemy.org/en/14/core/engines.html
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management

---

!!! success "Configurações Avançadas Completas!"

    Com todas as configurações ajustadas, seu sistema está otimizado e seguro!
