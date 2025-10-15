# Logs de Auditoria

Guia completo para visualizar e interpretar logs de auditoria do Sistema Pint of Science Brasil.

## 🎯 O que são Logs de Auditoria?

Os logs de auditoria registram **todas as ações administrativas** realizadas no sistema, incluindo:

- 👤 Criação, edição e deleção de coordenadores
- 📅 Modificações em eventos
- 🏙️ Cadastro de cidades
- 🎭 Criação de funções
- ✅ Validações de participantes
- 📧 Envios de e-mails
- ⚙️ Alterações em configurações

!!! info "Importância"

    Os logs são fundamentais para:
    - Rastrear quem fez o quê e quando
    - Identificar problemas e inconsistências
    - Auditoria de segurança
    - Conformidade com LGPD
    - Debugging de problemas

## 🚀 Acessando os Logs

### Opção 1: Via Painel Admin istração (futuro)

!!! warning "Em Desenvolvimento"

    A visualização de logs na interface web está planejada para próxima versão do sistema.

### Opção 2: Via Banco de Dados

Logs estão armazenados na tabela `auditoria` do banco de dados SQLite.

#### Estrutura da Tabela

| Coluna            | Tipo     | Descrição                                   |
| ----------------- | -------- | ------------------------------------------- |
| **id**            | Integer  | ID único do log                             |
| **timestamp**     | DateTime | Data e hora da ação                         |
| **usuario_id**    | Integer  | ID do usuário que executou                  |
| **usuario_email** | String   | E-mail do usuário                           |
| **acao**          | String   | Tipo de ação (CREATE, UPDATE, DELETE)       |
| **entidade**      | String   | Entidade afetada (Coordenador, Evento, etc) |
| **entidade_id**   | Integer  | ID do registro afetado                      |
| **detalhes**      | String   | Detalhes adicionais da ação                 |

## 📊 Tipos de Ações Registradas

### Ações em Coordenadores

```
CREATE: Coordenador criado
UPDATE: Dados do coordenador alterados
DELETE: Coordenador removido
ASSOCIATE: Cidades associadas ao coordenador
DISSOCIATE: Associação removida
```

### Ações em Participantes

```
VALIDATE: Participação validada por coordenador
UPDATE: Dados do participante editados
EMAIL_SENT: Certificado enviado por e-mail
```

### Ações em Eventos, Cidades e Funções

```
CREATE: Novo registro criado
UPDATE: Registro editado
DELETE: Registro removido
```

### Ações de Configuração

```
CONFIG_UPDATE: Configuração de certificado alterada
IMAGE_UPLOAD: Imagem enviada
COLOR_UPDATE: Cores do certificado atualizadas
```

## 🔍 Consultando Logs

### Via Linha de Comando (sqlite3)

```bash
# Acessar banco de dados
cd data
sqlite3 pint_of_science.db

# Ver últimos 20 logs
SELECT * FROM auditoria ORDER BY timestamp DESC LIMIT 20;

# Ver logs de um usuário específico
SELECT * FROM auditoria
WHERE usuario_email = 'admin@exemplo.com'
ORDER BY timestamp DESC;

# Ver logs de uma ação específica
SELECT * FROM auditoria
WHERE acao = 'VALIDATE'
ORDER BY timestamp DESC
LIMIT 50;

# Ver logs de um dia específico
SELECT * FROM auditoria
WHERE DATE(timestamp) = '2025-01-15'
ORDER BY timestamp DESC;
```

### Via Python

```python
from app.db import db_manager
from app.models import Auditoria

with db_manager.get_db_session() as session:
    # Últimos 50 logs
    logs = session.query(Auditoria)\
                  .order_by(Auditoria.timestamp.desc())\
                  .limit(50)\
                  .all()

    for log in logs:
        print(f"{log.timestamp} - {log.usuario_email} - "
              f"{log.acao} - {log.entidade} #{log.entidade_id}")
```

## 📋 Exemplos de Logs

### Criação de Coordenador

```
timestamp: 2025-01-15 10:30:00
usuario_id: 1
usuario_email: admin@pintofscience.com.br
acao: CREATE
entidade: Coordenador
entidade_id: 5
detalhes: Criado coordenador: Maria Silva (maria@exemplo.com)
```

### Validação de Participante

```
timestamp: 2025-05-20 15:45:30
usuario_id: 3
usuario_email: coordenador@cidade.com
acao: VALIDATE
entidade: Participante
entidade_id: 123
detalhes: Participante validado: João Santos (joao@email.com) - Brasília-DF
```

### Alteração de Evento

```
timestamp: 2025-01-10 09:00:00
usuario_id: 1
usuario_email: admin@pintofscience.com.br
acao: UPDATE
entidade: Evento
entidade_id: 3
detalhes: Datas atualizadas: 2025 -> ['20/05/2025', '21/05/2025', '22/05/2025']
```

### Upload de Imagem

```
timestamp: 2025-01-12 14:20:00
usuario_id: 1
usuario_email: admin@pintofscience.com.br
acao: CONFIG_UPDATE
entidade: CertificadoConfig
entidade_id: 2025
detalhes: Logo atualizado para ano 2025: 2025/pint_logo.png
```

## 🎯 Casos de Uso Comuns

### Caso 1: Investigar Validação Suspeita

```sql
-- Buscar todas as validações de um coordenador
SELECT * FROM auditoria
WHERE usuario_id = 5
  AND acao = 'VALIDATE'
  AND DATE(timestamp) = '2025-05-20'
ORDER BY timestamp;
```

Resultado: Lista todas validações feitas por esse coordenador no dia.

### Caso 2: Rastrear Quem Alterou um Registro

```sql
-- Ver histórico de alterações em um participante
SELECT * FROM auditoria
WHERE entidade = 'Participante'
  AND entidade_id = 123
ORDER BY timestamp DESC;
```

Resultado: Mostra quem e quando alterou aquele participante.

### Caso 3: Auditar Ações de um Dia

```sql
-- Todas as ações de um dia específico
SELECT timestamp, usuario_email, acao, entidade, detalhes
FROM auditoria
WHERE DATE(timestamp) = '2025-05-20'
ORDER BY timestamp;
```

Resultado: Timeline completo das ações do dia.

### Caso 4: Identificar Coordenador Mais Ativo

```sql
-- Contar validações por coordenador
SELECT usuario_email, COUNT(*) as total_validacoes
FROM auditoria
WHERE acao = 'VALIDATE'
GROUP BY usuario_email
ORDER BY total_validacoes DESC;
```

Resultado: Ranking de coordenadores por número de validações.

## 📊 Análises Úteis

### Total de Ações por Tipo

```sql
SELECT acao, COUNT(*) as total
FROM auditoria
GROUP BY acao
ORDER BY total DESC;
```

### Atividade por Usuário

```sql
SELECT usuario_email, COUNT(*) as total_acoes
FROM auditoria
GROUP BY usuario_email
ORDER BY total_acoes DESC;
```

### Ações por Entidade

```sql
SELECT entidade, COUNT(*) as total
FROM auditoria
GROUP BY entidade
ORDER BY total DESC;
```

### Timeline de Atividades

```sql
SELECT DATE(timestamp) as dia, COUNT(*) as total_acoes
FROM auditoria
GROUP BY DATE(timestamp)
ORDER BY dia DESC
LIMIT 30;
```

## 🔒 Segurança e Privacidade

### Dados Sensíveis

Os logs **NÃO armazenam**:

- ❌ Senhas (nem hash)
- ❌ Dados pessoais descriptografados completos
- ❌ Tokens de sessão
- ❌ Informações bancárias

Os logs **ARMAZENAM**:

- ✅ E-mail do usuário que executou ação
- ✅ Tipo de ação realizada
- ✅ ID dos registros afetados
- ✅ Timestamp preciso
- ✅ Detalhes textuais da ação

### Retenção de Logs

!!! info "Política de Retenção"

    Por padrão, logs são mantidos **indefinidamente** para auditoria. Considere implementar política de limpeza após período (ex: 2 anos).

### Acesso aos Logs

Apenas **superadmins** têm acesso completo aos logs:

- ✅ Visualização irrestrita
- ✅ Export de relatórios
- ✅ Análise forense

Coordenadores comuns **não** veem logs de auditoria.

## 💡 Boas Práticas

### Para Monitoramento

1. **Revise logs regularmente** - Pelo menos mensalmente
2. **Identifique padrões suspeitos** - Validações em massa, alterações noturnas
3. **Verifique integridade** - Certifique-se de que logs estão sendo gerados
4. **Exporte periodicamente** - Mantenha backups dos logs

### Para Investigação

1. **Comece pelo timestamp** - Identifique quando problema ocorreu
2. **Busque por usuário** - Quem estava ativo no momento
3. **Filtre por entidade** - Foque no tipo de registro afetado
4. **Correlacione eventos** - Uma ação pode ter causado outras

### Para Conformidade

1. **Documente acessos** - Mantenha registro de quem consultou logs
2. **Proteja dados** - Logs contêm informações sensíveis
3. **Implemente alertas** - Notificações para ações críticas
4. **Audite regularmente** - Revisão trimestral de atividades

## 🛠️ Ferramentas Auxiliares

### Script de Consulta Rápida

```python
# arquivo: utils/consultar_logs.py
from app.db import db_manager
from app.models import Auditoria
from datetime import datetime, timedelta

def logs_ultimas_24h():
    """Mostra logs das últimas 24 horas"""
    ontem = datetime.now() - timedelta(days=1)

    with db_manager.get_db_session() as session:
        logs = session.query(Auditoria)\
                      .filter(Auditoria.timestamp >= ontem)\
                      .order_by(Auditoria.timestamp.desc())\
                      .all()

        print(f"Total de ações (24h): {len(logs)}\n")

        for log in logs:
            print(f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"{log.usuario_email} - {log.acao} - "
                  f"{log.entidade} - {log.detalhes}")

if __name__ == "__main__":
    logs_ultimas_24h()
```

Uso:

```bash
python utils/consultar_logs.py
```

### Export para CSV

```python
# arquivo: utils/export_logs.py
import csv
from app.db import db_manager
from app.models import Auditoria

def exportar_logs_csv(arquivo_saida="logs_export.csv"):
    """Exporta todos os logs para CSV"""
    with db_manager.get_db_session() as session:
        logs = session.query(Auditoria)\
                      .order_by(Auditoria.timestamp.desc())\
                      .all()

        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Timestamp', 'Usuario Email', 'Acao',
                           'Entidade', 'Entidade ID', 'Detalhes'])

            for log in logs:
                writer.writerow([
                    log.id,
                    log.timestamp.isoformat(),
                    log.usuario_email,
                    log.acao,
                    log.entidade,
                    log.entidade_id,
                    log.detalhes
                ])

        print(f"✅ {len(logs)} logs exportados para {arquivo_saida}")

if __name__ == "__main__":
    exportar_logs_csv()
```

Uso:

```bash
python utils/export_logs.py
```

## 🆘 Problemas Comuns

### Problema: Logs Não Estão Sendo Gerados

**Causas possíveis**:

- Sistema está usando configuração errada
- Tabela auditoria não existe no banco

**Solução**:

```bash
# Verificar estrutura do banco
sqlite3 data/pint_of_science.db
.schema auditoria
```

---

### Problema: Muitos Logs, Performance Lenta

**Causa**: Tabela muito grande (milhares de registros)

**Solução**:

1. Implementar índices:

```sql
CREATE INDEX idx_auditoria_timestamp ON auditoria(timestamp);
CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id);
```

2. Arquivar logs antigos periodicamente

---

### Problema: Como Deletar Logs Antigos?

**Solução** (cuidado!):

```sql
-- Deletar logs com mais de 2 anos
DELETE FROM auditoria
WHERE timestamp < DATE('now', '-2 years');
```

!!! danger "Atenção"

    Deletar logs pode violar políticas de auditoria. Documente e justifique antes de executar.

---

!!! success "Pronto!"

    Agora você sabe como acessar e interpretar os logs de auditoria do sistema!
