# Conversão de Datas - Formato Brasileiro

## Visão Geral

O sistema foi refatorado para aceitar e exibir datas no formato brasileiro **DD/MM/YYYY** na interface do usuário, enquanto mantém o armazenamento interno no formato ISO **YYYY-MM-DD** no banco de dados.

Esta conversão se aplica a:
1. **Datas de Evento** (`eventos.datas_evento`) - Administração
2. **Datas de Participação** (`participantes.datas_participacao`) - Participantes

## Motivação

- **Usabilidade**: Usuários brasileiros estão acostumados com o formato DD/MM/YYYY
- **Consistência**: Mantém o padrão brasileiro em toda a interface
- **Armazenamento**: Formato ISO no banco de dados permite ordenação e comparação eficiente

## Implementação

### Métodos Auxiliares nos Modelos (app/models.py)

Foram adicionados métodos de classe aos modelos `Evento` e `Participante`:

#### Evento - Datas do Evento

**1. `Evento.parse_datas_br_to_iso(datas_str: str) -> List[str]`**

Converte string de datas no formato brasileiro para lista de datas ISO.

**Entrada**: `"19/05/2025, 20/05/2025, 21/05/2025"`
**Saída**: `["2025-05-19", "2025-05-20", "2025-05-21"]`

**Validações**:
- Formato DD/MM/YYYY obrigatório
- Levanta `ValueError` se formato inválido
- Remove espaços extras automaticamente
- Valida se as datas são válidas (dia, mês, ano existem)

**Exemplo de uso**:
```python
from app.models import Evento

# No formulário, receber entrada do usuário
datas_usuario = "19/05/2025, 20/05/2025"

# Converter para ISO antes de salvar no banco
try:
    datas_iso = Evento.parse_datas_br_to_iso(datas_usuario)
    # datas_iso = ["2025-05-19", "2025-05-20"]
    # Salvar no banco...
except ValueError as e:
    print(f"Erro: {e}")
```

**2. `Evento.format_datas_iso_to_br(datas_list: List[str]) -> str`**

Converte lista de datas ISO para formato brasileiro.

**Entrada**: `["2025-05-19", "2025-05-20", "2025-05-21"]`
**Saída**: `"19/05/2025, 20/05/2025, 21/05/2025"`

**Exemplo de uso**:
```python
from app.models import Evento

# Buscar evento do banco
evento = evento_repo.get_by_id(1)
# evento.datas_evento = ["2025-05-19", "2025-05-20"]

# Converter para exibição
datas_br = Evento.format_datas_iso_to_br(evento.datas_evento)
# datas_br = "19/05/2025, 20/05/2025"
print(f"Datas do evento: {datas_br}")
```

#### Participante - Datas de Participação

**1. `Participante.parse_datas_participacao_br_to_iso(datas_str: str) -> str`**

Converte string de datas de participação no formato brasileiro para ISO.

**Entrada**: `"19/05/2025, 20/05/2025"`
**Saída**: `"2025-05-19, 2025-05-20"` (retorna string, não lista)

**Exemplo de uso**:
```python
from app.models import Participante

# No data editor, ao salvar edição
datas_usuario = "19/05/2025, 20/05/2025"

# Converter para ISO antes de salvar no banco
try:
    datas_iso = Participante.parse_datas_participacao_br_to_iso(datas_usuario)
    # datas_iso = "2025-05-19, 2025-05-20"
    participante.datas_participacao = datas_iso
except ValueError as e:
    print(f"Data inválida: {e}")
```

**2. `Participante.format_datas_participacao_iso_to_br(datas_str: str) -> str`**

Converte string de datas ISO para formato brasileiro.

**Entrada**: `"2025-05-19, 2025-05-20"`
**Saída**: `"19/05/2025, 20/05/2025"`

**Exemplo de uso**:
```python
from app.models import Participante

# Buscar participante do banco
# participante.datas_participacao = "2025-05-19, 2025-05-20"

# Converter para exibição
datas_br = Participante.format_datas_participacao_iso_to_br(participante.datas_participacao)
# datas_br = "19/05/2025, 20/05/2025"
print(f"Datas de participação: {datas_br}")
```

### Alterações na Interface de Administração

#### Formulário de Criação de Eventos

**Antes**:
```python
datas_evento = st.text_input(
    "Datas do Evento (YYYY-MM-DD) *",
    placeholder="Ex: 2025-05-19, 2025-05-20, 2025-05-21",
    help="Datas no formato YYYY-MM-DD (ISO), separadas por vírgula",
)
```

**Depois**:
```python
datas_evento = st.text_input(
    "Datas do Evento (DD/MM/YYYY) *",
    placeholder="Ex: 19/05/2025, 20/05/2025, 21/05/2025",
    help="Datas no formato brasileiro DD/MM/YYYY, separadas por vírgula",
)

# Parse usando o método auxiliar
datas_list = Evento.parse_datas_br_to_iso(datas_evento)
```

#### Listagem de Eventos (Data Editor)

**Antes**:
```python
# Exibir datas no formato ISO
datas_str = ", ".join(evento.datas_evento)
```

**Depois**:
```python
# Exibir datas no formato brasileiro
datas_str = Evento.format_datas_iso_to_br(evento.datas_evento)
```

#### Edição de Eventos

**Antes**:
```python
# Parse direto do ISO
for d in datas_str.split(","):
    datetime.fromisoformat(d)
    datas_list.append(d)
```

**Depois**:
```python
# Parse usando o método auxiliar
datas_list = Evento.parse_datas_br_to_iso(datas_str)
```

### Alterações na Interface de Participantes

#### Exibição de Datas de Participação

**Antes**:
```python
linha = {
    # ...
    "Datas Participação": participante["datas_participacao"],
    # ...
}
```

**Depois**:
```python
linha = {
    # ...
    "Datas Participação": Participante.format_datas_participacao_iso_to_br(
        participante["datas_participacao"]
    ),
    # ...
}
```

#### Configuração do Data Editor

**Antes**:
```python
"Datas Participação": st.column_config.TextColumn(
    "Datas Participação",
    help="Editar datas (coordenadores e superadmin)"
),
```

**Depois**:
```python
"Datas Participação": st.column_config.TextColumn(
    "Datas Participação",
    help="Editar datas no formato DD/MM/YYYY, separadas por vírgula"
),
```

#### Salvamento de Edições

**Antes**:
```python
elif campo == "datas_participacao":
    participante.datas_participacao = valor
```

**Depois**:
```python
elif campo == "datas_participacao":
    try:
        valor_iso = Participante.parse_datas_participacao_br_to_iso(valor)
        participante.datas_participacao = valor_iso
    except ValueError as e:
        logger.error(f"Erro ao converter datas: {e}")
        continue
```

## Testes

### Testes Unitários (`tests/test_evento_datas.py`)

Total: **28 testes** (15 para Evento + 13 para Participante) cobrindo:

**Evento (15 testes):**
1. ✅ Conversão única data BR -> ISO
2. ✅ Conversão múltiplas datas BR -> ISO
3. ✅ Conversão com espaços extras
4. ✅ Rejeição de formato inválido (ISO em vez de BR)
5. ✅ Rejeição de string vazia
6. ✅ Rejeição de apenas vírgulas
7. ✅ Validação de dia inválido (32/05/2025)
8. ✅ Validação de mês inválido (19/13/2025)
9. ✅ Conversão única data ISO -> BR
10. ✅ Conversão múltiplas datas ISO -> BR
11. ✅ Conversão de lista vazia
12. ✅ Graceful handling de data inválida
13. ✅ Roundtrip (BR -> ISO -> BR mantém valores)
14. ✅ Datas com zeros à esquerda (parsing)
15. ✅ Datas com zeros à esquerda (formatação)

**Participante (13 testes):**
1. ✅ Conversão única data BR -> ISO (retorna string)
2. ✅ Conversão múltiplas datas BR -> ISO
3. ✅ Conversão com espaços extras
4. ✅ Rejeição de formato inválido
5. ✅ Rejeição de string vazia
6. ✅ Validação de dia inválido
7. ✅ Conversão única data ISO -> BR
8. ✅ Conversão múltiplas datas ISO -> BR
9. ✅ Conversão de string vazia
10. ✅ Graceful handling de data inválida
11. ✅ Roundtrip (BR -> ISO -> BR)
12. ✅ Datas com zeros à esquerda (parsing)
13. ✅ Datas com zeros à esquerda (formatação)

**Executar testes**:
```bash
pytest tests/test_evento_datas.py -v
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIO                             │
│                                                             │
│  Digita: "19/05/2025, 20/05/2025"                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Evento.parse_datas_br_to_iso()                 │
│                                                             │
│  Converte para: ["2025-05-19", "2025-05-20"]               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BANCO DE DADOS                           │
│                                                             │
│  Armazena como JSON: ["2025-05-19", "2025-05-20"]          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             Evento.format_datas_iso_to_br()                 │
│                                                             │
│  Converte para: "19/05/2025, 20/05/2025"                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIO                             │
│                                                             │
│  Vê: "19/05/2025, 20/05/2025"                              │
└─────────────────────────────────────────────────────────────┘
```

## Vantagens da Abordagem com @classmethod

1. **Centralização**: Toda lógica de conversão em um único lugar
2. **Reutilização**: Pode ser usada em qualquer parte do código
3. **Testabilidade**: Fácil de testar isoladamente
4. **Manutenibilidade**: Mudanças futuras em um único local
5. **Coerência**: Mesmo padrão usado em todo o projeto
6. **Type Safety**: Tipo de entrada/saída explícito

## Mensagens de Erro

O sistema agora fornece mensagens de erro mais claras:

**Antes**:
```
❌ Formato de datas inválido. Use YYYY-MM-DD separado por vírgula. Erro: ...
```

**Depois**:
```
❌ Formato de datas inválido. Data inválida: 2025-05-19. Use o formato DD/MM/YYYY
```

## Compatibilidade

- ✅ **Banco de dados**: Mantém formato ISO (nenhuma migração necessária)
- ✅ **API interna**: Continua usando ISO internamente
- ✅ **Certificados**: Não afetados (usam formatação própria)
- ✅ **Backward compatible**: Dados existentes funcionam normalmente

## Próximos Passos (Opcional)

1. Aplicar mesmo padrão para outras datas do sistema (data_inscricao, etc.)
2. Adicionar date picker UI para melhor UX
3. Considerar internacionalização (i18n) para outros formatos

## Conclusão

A refatoração melhora significativamente a experiência do usuário brasileiro mantendo a integridade dos dados e seguindo as melhores práticas do projeto com uso de métodos de classe centralizados.
