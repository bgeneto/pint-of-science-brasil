# Resumo da Implementação - Configuração de Carga Horária

## 🎯 Objetivo

Adicionar funcionalidade para configurar de forma flexível como a carga horária é calculada e exibida nos certificados, permitindo:
- Definir horas por dia de participação
- Definir carga horária total do evento
- Selecionar funções que recebem carga horária total (independente de dias)

## ✅ Alterações Realizadas

### 1. Backend - `app/services.py`

#### Classe `ServicoCalculoCargaHoraria`

**Antes**:
```python
def calcular_carga_horaria(self, datas_participacao: str, evento_datas) -> Tuple[int, str]:
    # Calculava sempre 4h por dia (hardcoded)
    carga_horaria = len(dias_unicos) * self._duracao_padrao_evento
```

**Depois**:
```python
def calcular_carga_horaria(
    self,
    datas_participacao: str,
    evento_datas,
    evento_ano: int = None,      # ← NOVO
    funcao_id: int = None         # ← NOVO
) -> Tuple[int, str]:
    # Carrega configuração do ano
    config = self._carregar_configuracao_carga_horaria(evento_ano)

    # Verifica se função tem direito a CH total
    if funcao_id in config['funcoes_evento_completo']:
        return config['horas_por_evento'], detalhes

    # Senão, calcula por dias com valor configurado
    carga_horaria = len(dias_unicos) * config['horas_por_dia']
```

**Método novo adicionado**:
- `_carregar_configuracao_carga_horaria(evento_ano)`: Carrega config do JSON

**Atualizações em chamadas**:
- `validar_inscricao()`: Agora passa `evento.ano` e `dados.funcao_id`
- `inscrever_participante()`: Agora passa `evento.ano` e `dados_inscricao.funcao_id`

### 2. Frontend - `pages/2_⚙️_Administração.py`

#### Nova Tab Adicionada

```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Coordenadores",
    "📅 Eventos",
    "🏙️ Cidades",
    "🎭 Funções",
    "🖼️ Certificado",
    "⏱️ Carga Horária"  # ← NOVA TAB
])
```

#### Funções Novas Criadas

1. **`carregar_configuracao_carga_horaria(ano)`**
   - Carrega config do JSON para um ano específico
   - Retorna defaults se não existir

2. **`salvar_configuracao_carga_horaria(ano, horas_por_dia, horas_por_evento, funcoes_ids)`**
   - Salva config no JSON
   - Cria estrutura se necessário
   - Retorna True/False

3. **`configurar_carga_horaria()`**
   - Interface completa da tab
   - Inputs para todos os parâmetros
   - Preview de configuração
   - Exemplos práticos

#### Interface Implementada

- ✅ Seletor de ano (dropdown)
- ✅ Input de horas por dia (number_input, 1-24)
- ✅ Input de horas por evento (number_input, 1-200)
- ✅ Multiselect de funções (com nomes legíveis)
- ✅ Métricas de preview (3 cards)
- ✅ Expandable com exemplos práticos
- ✅ Botão de salvar com feedback
- ✅ Mensagens de sucesso/erro

### 3. Configuração - `static/certificate_config.json`

**Estrutura adicionada**:
```json
{
  "2025": {
    "cores": { ... },
    "imagens": { ... },
    "carga_horaria": {           // ← NOVA SEÇÃO
      "horas_por_dia": 4,
      "horas_por_evento": 40,
      "funcoes_evento_completo": [1, 2, 3]
    }
  }
}
```

### 4. Testes - `test_carga_horaria.py`

Script de teste criado com 4 cenários:
1. ✅ Salvar configuração
2. ✅ Calcular por dias (função comum)
3. ✅ Calcular evento completo (função especial)
4. ✅ Calcular sem config (fallback)

### 5. Documentação - `docs/CONFIGURACAO_CARGA_HORARIA.md`

Documentação completa criada incluindo:
- Visão geral
- Parâmetros configuráveis
- Lógica de cálculo
- Estrutura de dados
- Interface do usuário
- Exemplos de uso
- Integração com código
- Troubleshooting
- Roadmap

## 🔄 Fluxo de Funcionamento

### Inscrição de Participante

```
1. Usuário preenche formulário de inscrição
   ↓
2. Sistema valida dados
   ↓
3. Sistema calcula carga horária:
   - Busca config do ano do evento
   - Verifica se função_id está na lista de "funcoes_evento_completo"
   - Se SIM: retorna horas_por_evento (ex: 40h)
   - Se NÃO: calcula dias × horas_por_dia (ex: 3 × 4 = 12h)
   ↓
4. Armazena valor em participantes.carga_horaria_calculada
   ↓
5. Gera certificado usando esse valor
```

### Configuração pelo Admin

```
1. Admin acessa tab "⏱️ Carga Horária"
   ↓
2. Seleciona ano do evento
   ↓
3. Sistema carrega config existente (ou defaults)
   ↓
4. Admin ajusta:
   - Horas por dia
   - Horas por evento
   - Funções especiais
   ↓
5. Admin clica "Salvar"
   ↓
6. Sistema persiste em certificate_config.json
   ↓
7. Novas inscrições usam nova config
```

## 📊 Métricas de Implementação

- **Arquivos modificados**: 2
  - `app/services.py`
  - `pages/2_⚙️_Administração.py`

- **Arquivos criados**: 3
  - `test_carga_horaria.py`
  - `docs/CONFIGURACAO_CARGA_HORARIA.md`
  - Este resumo

- **Linhas adicionadas**: ~450
  - Services: ~60 linhas
  - Admin: ~250 linhas
  - Testes: ~90 linhas
  - Docs: ~350 linhas

- **Funções novas**: 4
  - `_carregar_configuracao_carga_horaria()` (services)
  - `carregar_configuracao_carga_horaria()` (admin)
  - `salvar_configuracao_carga_horaria()` (admin)
  - `configurar_carga_horaria()` (admin)

- **Parâmetros novos**: 2
  - `evento_ano` em `calcular_carga_horaria()`
  - `funcao_id` em `calcular_carga_horaria()`

## ✨ Destaques da Implementação

### 1. Separação por Ano
Cada evento mantém sua própria configuração, permitindo:
- Histórico preservado
- Flexibilidade entre edições
- Certificados retroativos consistentes

### 2. Backward Compatibility
Sistema totalmente retrocompatível:
- Parâmetros opcionais com defaults
- Fallback para valores hardcoded
- Dados existentes não afetados

### 3. Flexibilidade
Admins podem:
- Ajustar valores livremente
- Selecionar múltiplas funções
- Ver preview antes de salvar
- Entender impacto com exemplos

### 4. Performance
- Cálculo feito uma vez (na inscrição)
- Valor armazenado no banco
- Sem recálculo a cada certificado

### 5. UX
Interface intuitiva com:
- Labels descritivos
- Tooltips explicativos
- Exemplos práticos
- Feedback visual
- Validações inline

## 🧪 Testes Realizados

```bash
$ python test_carga_horaria.py

✅ Teste 1: Configuração salva com sucesso
✅ Teste 2: Cálculo por dias: 12h (3 dias × 4h)
✅ Teste 3: Cálculo evento completo: 40h (função especial)
✅ Teste 4: Cálculo padrão: 12h (sem config)

🎉 Todos os testes concluídos!
```

## 📝 Exemplo de Uso Real

### Configuração
```json
{
  "horas_por_dia": 4,
  "horas_por_evento": 40,
  "funcoes_evento_completo": [1, 2, 3]
}
```

### Resultados nos Certificados

| Participante | Função | Dias | Carga Horária |
|--------------|--------|------|---------------|
| João Silva | Palestrante (ID 10) | 3 dias | **12h** (3×4) |
| Maria Santos | Coordenadora Local (ID 1) | 2 dias | **40h** (total) |
| Pedro Costa | Organizador (ID 5) | 1 dia | **4h** (1×4) |
| Ana Lima | Coord. Regional (ID 2) | 3 dias | **40h** (total) |

## 🚀 Como Usar

### Para Admins

1. Acesse página de **Administração**
2. Clique na tab **⏱️ Carga Horária**
3. Selecione o ano do evento
4. Configure os valores desejados
5. Selecione as funções especiais
6. Clique em **Salvar**

### Para Desenvolvedores

```python
from app.services import servico_calculo_carga_horaria

# Calcular carga horária com configuração
horas, detalhes = servico_calculo_carga_horaria.calcular_carga_horaria(
    datas_participacao="2025-05-20,2025-05-21",
    evento_datas=["2025-05-20", "2025-05-21", "2025-05-22"],
    evento_ano=2025,
    funcao_id=1
)

print(f"Carga horária: {horas}h")
print(detalhes)
```

## 📚 Recursos Adicionais

- **Documentação completa**: `docs/CONFIGURACAO_CARGA_HORARIA.md`
- **Script de teste**: `test_carga_horaria.py`
- **Código fonte**:
  - Backend: `app/services.py` (linha 178)
  - Frontend: `pages/2_⚙️_Administração.py` (função `configurar_carga_horaria`)

## ✅ Checklist de Implementação

- [x] Backend - Atualizar `ServicoCalculoCargaHoraria`
- [x] Backend - Adicionar método de carregamento de config
- [x] Backend - Atualizar chamadas existentes
- [x] Frontend - Adicionar nova tab
- [x] Frontend - Criar interface de configuração
- [x] Frontend - Adicionar funções de carga/salvamento
- [x] Config - Estruturar JSON
- [x] Testes - Criar script de teste
- [x] Testes - Validar todos os cenários
- [x] Docs - Documentação completa
- [x] Docs - Resumo de implementação
- [x] Verificar sintaxe Python
- [x] Testar integração

---

**Status**: ✅ **IMPLEMENTAÇÃO COMPLETA E TESTADA**

**Data**: Outubro 2025
