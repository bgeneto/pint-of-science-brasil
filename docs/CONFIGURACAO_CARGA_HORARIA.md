# Configuração de Carga Horária - Documentação

## Visão Geral

A funcionalidade de **Configuração de Carga Horária** permite que superadmins personalizem como a carga horária é calculada e exibida nos certificados gerados pelo sistema, com configurações específicas por ano de evento.

## Localização

A configuração está disponível na página de **Administração** (`pages/2_⚙️_Administração.py`), na aba **⏱️ Carga Horária** (tab6).

## Funcionalidades

### 1. Configuração por Ano

Cada evento/ano mantém sua própria configuração de carga horária, garantindo:
- Flexibilidade para diferentes edições do evento
- Histórico de configurações preservado
- Geração consistente de certificados retroativos

### 2. Parâmetros Configuráveis

#### a) Horas por Dia (`horas_por_dia`)
- **Descrição**: Define quantas horas equivalem a 1 dia de participação
- **Valor padrão**: 4 horas
- **Faixa**: 1-24 horas
- **Uso**: Aplicado a participantes com funções comuns

**Exemplo**:
- Se configurado para 4h e o participante compareceu 3 dias → 12h no certificado

#### b) Horas por Evento (`horas_por_evento`)
- **Descrição**: Carga horária total do evento (independente dos dias)
- **Valor padrão**: 40 horas
- **Faixa**: 1-200 horas
- **Uso**: Aplicado apenas às funções selecionadas

**Exemplo**:
- Coordenadores recebem sempre 40h, independente de terem participado 1 ou 5 dias

#### c) Funções de Evento Completo (`funcoes_evento_completo`)
- **Descrição**: Lista de IDs de funções que recebem carga horária total
- **Valor padrão**: Lista vazia `[]`
- **Tipo**: Lista de IDs (integers)
- **Uso**: Define quais funções ignoram o cálculo por dias

**Exemplos de funções típicas**:
- Coordenador(a) Local
- Coordenador(a) Regional
- Organizador(a)
- Coordenador(a) Geral

### 3. Lógica de Cálculo

O sistema utiliza a seguinte lógica ao gerar certificados:

```python
def calcular_carga_horaria(datas_participacao, evento_datas, evento_ano, funcao_id):
    config = carregar_configuracao(evento_ano)

    # Verificar se a função recebe carga horária total
    if funcao_id in config['funcoes_evento_completo']:
        return config['horas_por_evento']  # Ex: 40h

    # Caso contrário, calcular por dias
    dias_unicos = contar_dias_participacao(datas_participacao)
    return dias_unicos * config['horas_por_dia']  # Ex: 3 dias × 4h = 12h
```

## Estrutura de Dados

### Arquivo de Configuração

**Localização**: `static/certificate_config.json`

**Estrutura**:
```json
{
  "2025": {
    "cores": { ... },
    "imagens": { ... },
    "carga_horaria": {
      "horas_por_dia": 4,
      "horas_por_evento": 40,
      "funcoes_evento_completo": [1, 2, 3]
    }
  }
}
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `horas_por_dia` | int | Horas equivalentes a 1 dia |
| `horas_por_evento` | int | Carga horária total do evento |
| `funcoes_evento_completo` | list[int] | IDs das funções com CH total |

## Interface do Usuário

### Tela de Configuração

A interface oferece:

1. **Seletor de Ano**: Escolha o evento/ano para configurar
2. **Campo Horas por Dia**: Input numérico com exemplo dinâmico
3. **Campo Horas por Evento**: Input numérico para CH total
4. **Multiselect de Funções**: Selecione funções que recebem CH total
5. **Preview de Configuração**: Métricas visuais do que será salvo
6. **Exemplos Práticos**: Expandable com casos de uso
7. **Botão Salvar**: Persiste configuração no JSON

### Validações

- Horas por dia: 1-24
- Horas por evento: 1-200
- Funções: Apenas IDs válidos da tabela `funcoes`

## Exemplos de Uso

### Cenário 1: Evento de 3 dias, 4h por dia

**Configuração**:
```json
{
  "horas_por_dia": 4,
  "horas_por_evento": 40,
  "funcoes_evento_completo": [1, 2]
}
```

**Resultados**:
- Palestrante (função comum) que participou 2 dias → **8h**
- Palestrante que participou 3 dias → **12h**
- Coordenador Local (função ID 1) que participou 1 dia → **40h**
- Coordenador Regional (função ID 2) que participou 3 dias → **40h**

### Cenário 2: Evento intensivo, 6h por dia

**Configuração**:
```json
{
  "horas_por_dia": 6,
  "horas_por_evento": 60,
  "funcoes_evento_completo": [1, 5, 8]
}
```

**Resultados**:
- Palestrante que participou 2 dias → **12h**
- Organizador(a) (função ID 5) → **60h** (sempre)

## Impacto nos Certificados

A carga horária configurada é exibida no certificado PDF na seguinte linha:

```
"...realizado em [Cidade] - [Estado], no(s) dia(s) [Datas],
com carga horária de [XX] horas."
```

O valor `[XX]` é determinado pela lógica de cálculo descrita acima.

## Integração com o Código

### Classes Afetadas

1. **`ServicoCalculoCargaHoraria`** (`app/services.py`):
   - Método: `calcular_carga_horaria()` - atualizado para aceitar `evento_ano` e `funcao_id`
   - Método novo: `_carregar_configuracao_carga_horaria()` - carrega config do JSON

2. **`GeradorCertificado`** (`app/services.py`):
   - Usa `participante.carga_horaria_calculada` (já calculado na inscrição)

3. **Página Administração** (`pages/2_⚙️_Administração.py`):
   - Funções novas:
     - `carregar_configuracao_carga_horaria()`
     - `salvar_configuracao_carga_horaria()`
     - `configurar_carga_horaria()`

### Pontos de Cálculo

A carga horária é calculada em dois momentos:

1. **Na inscrição** (`inscrever_participante()`):
   ```python
   carga_horaria, _ = servico_calculo_carga_horaria.calcular_carga_horaria(
       dados_inscricao.datas_participacao,
       evento.datas_evento,
       evento.ano,  # ← Novo parâmetro
       dados_inscricao.funcao_id  # ← Novo parâmetro
   )
   ```

2. **Na validação** (`validar_inscricao()`):
   - Usa mesma lógica para verificar se carga horária é válida

### Persistência

O valor calculado é armazenado em `participantes.carga_horaria_calculada`, garantindo:
- Performance (não recalcula a cada geração de certificado)
- Consistência (valor fixo mesmo se configuração mudar)
- Histórico (preserva o cálculo original da inscrição)

## Retrocompatibilidade

O sistema mantém total compatibilidade com dados existentes:

- Se `evento_ano` não for passado → usa valor padrão (4h/dia)
- Se `funcao_id` não for passado → calcula por dias
- Se configuração não existir → usa defaults hardcoded
- Participantes já cadastrados mantém sua `carga_horaria_calculada` original

## Testes

Execute o script de teste:

```bash
python test_carga_horaria.py
```

**Casos testados**:
1. ✅ Salvar configuração no JSON
2. ✅ Calcular CH por dias (função comum)
3. ✅ Calcular CH total (função especial)
4. ✅ Calcular sem configuração (fallback)

## Troubleshooting

### Problema: Certificados não refletem nova configuração

**Causa**: Carga horária já foi calculada e armazenada na inscrição

**Solução**:
- Configuração afeta apenas **novas inscrições**
- Para recalcular participantes existentes, seria necessário script de migração

### Problema: Função não aparece no multiselect

**Causa**: Função não está cadastrada na tabela `funcoes`

**Solução**:
1. Vá para aba "🎭 Funções"
2. Cadastre a função desejada
3. Retorne para aba "⏱️ Carga Horária"

### Problema: Erro ao salvar configuração

**Causa**: Permissões de escrita ou JSON malformado

**Solução**:
1. Verificar permissões da pasta `static/`
2. Verificar logs do sistema
3. Validar JSON existente com `jq` ou similar

## Roadmap / Melhorias Futuras

- [ ] Script de recálculo em massa para participantes existentes
- [ ] Interface para visualizar participantes afetados por configuração
- [ ] Histórico de mudanças de configuração (auditoria)
- [ ] Validação de conflitos entre anos
- [ ] Exportar/importar configurações entre anos
- [ ] Suporte a múltiplas faixas de CH (Junior/Senior/Master)

## Referências

- **Arquivo principal**: `app/services.py` (classe `ServicoCalculoCargaHoraria`)
- **Interface**: `pages/2_⚙️_Administração.py` (função `configurar_carga_horaria()`)
- **Config**: `static/certificate_config.json`
- **Testes**: `test_carga_horaria.py`

---

**Última atualização**: Outubro 2025
**Autor**: Sistema Pint of Science Brasil
