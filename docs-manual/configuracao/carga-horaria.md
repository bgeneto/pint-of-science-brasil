# Configuração de Carga Horária

Guia completo para configurar como a carga horária é calculada nos certificados do Pint of Science Brasil.

## 🎯 O que é Carga Horária?

A carga horária representa o **total de horas** que o participante dedicou ao evento, exibida no certificado.

Exemplo no certificado:

```
...participou do evento Pint of Science Brasil 2025, realizado em
Brasília-DF, nos dias 20, 21 e 22 de maio de 2025, na função de
Palestrante, com carga horária de 12 (doze) horas.
```

## 🧮 Como é Calculada?

### Regra Padrão

```
Carga Horária = Número de Dias Participados × Horas por Dia
```

**Exemplo**:

- Participante esteve presente em: 20/05, 21/05, 22/05 (3 dias)
- Horas por dia configuradas: 4h
- **Carga horária = 3 × 4 = 12 horas**

### Regra Especial (Funções de Evento Completo)

Algumas funções recebem carga horária do **evento completo**, independente dos dias:

```
Funções Especiais = Horas Totais do Evento
```

**Exemplo**:

- Função: Organizador(a) (função especial)
- Participou apenas dia 20/05 (1 dia)
- Evento tem 3 dias × 4h = 12h totais
- **Carga horária = 12 horas** (evento completo)

## 🚀 Acessando Configuração

1. Login como **superadmin**
2. Menu **⚙️ Administração**
3. Aba **⏱️ Carga Horária**

## ⚙️ Configurando Carga Horária

### Estrutura da Configuração

A configuração está em `static/certificate_config.json`:

```json
{
  "2025": {
    "carga_horaria": {
      "horas_por_dia": 4,
      "horas_por_evento": 40,
      "funcoes_evento_completo": [1, 2, 3]
    }
  }
}
```

### Parâmetros

| Parâmetro                   | Descrição                                  | Exemplo     |
| --------------------------- | ------------------------------------------ | ----------- |
| **horas_por_dia**           | Horas de atividade por dia de evento       | `4`         |
| **horas_por_evento**        | Total de horas do evento completo          | `40`        |
| **funcoes_evento_completo** | IDs das funções que recebem carga completa | `[1, 2, 3]` |

### Editando via Interface (futuro)

!!! info "Em Desenvolvimento"

    Interface visual para edição está planejada. Por enquanto, edite o arquivo JSON diretamente.

### Editando Manualmente

1. Abra `static/certificate_config.json`
2. Localize seção do ano desejado
3. Modifique valores em `carga_horaria`
4. Salve o arquivo

**Exemplo de edição**:

```json
// Antes
"2025": {
  "carga_horaria": {
    "horas_por_dia": 4,
    "horas_por_evento": 40,
    "funcoes_evento_completo": [1, 2]
  }
}

// Depois (aumentar horas e adicionar função)
"2025": {
  "carga_horaria": {
    "horas_por_dia": 5,
    "horas_por_evento": 50,
    "funcoes_evento_completo": [1, 2, 3, 5]
  }
}
```

## 🎯 Funções de Evento Completo

### O que são?

Funções que envolvem **participação em todo o evento**, mesmo que a pessoa não esteja fisicamente presente todos os dias.

### Exemplos Típicos

- **Organizador(a)**: Planejamento e execução do evento inteiro
- **Coordenador(a) Local**: Responsável pela cidade durante todo evento
- **Moderador(a)**: Conduz múltiplas sessões
- **Assessoria de Imprensa**: Cobertura de todo o evento

### Como Configurar

#### Passo 1: Identificar IDs das Funções

1. Acesse **⚙️ Administração** → **🎭 Funções**
2. Veja coluna **"ID"** na tabela
3. Anote IDs das funções desejadas

**Exemplo**:

```
ID: 1 - Nome: Organizador(a)
ID: 2 - Nome: Coordenador(a) Local
ID: 3 - Nome: Moderador(a)
ID: 5 - Nome: Assessoria de Imprensa
```

#### Passo 2: Adicionar ao JSON

```json
"funcoes_evento_completo": [1, 2, 3, 5]
```

#### Passo 3: Testar

1. Crie inscrição teste com função especial
2. Marque apenas 1 dia de participação
3. Gere certificado
4. Verifique se carga horária = horas totais do evento

## 📊 Exemplos de Configuração

### Configuração 1: Evento Curto (3 dias, 4h/dia)

```json
{
  "2025": {
    "carga_horaria": {
      "horas_por_dia": 4,
      "horas_por_evento": 12,
      "funcoes_evento_completo": [1, 2]
    }
  }
}
```

**Resultados**:

- Palestrante (3 dias) = 3 × 4 = **12h**
- Voluntário (2 dias) = 2 × 4 = **8h**
- Organizador (1 dia) = **12h** (evento completo)

### Configuração 2: Evento Longo (5 dias, 6h/dia)

```json
{
  "2026": {
    "carga_horaria": {
      "horas_por_dia": 6,
      "horas_por_evento": 30,
      "funcoes_evento_completo": [1, 2, 3]
    }
  }
}
```

**Resultados**:

- Palestrante (5 dias) = 5 × 6 = **30h**
- Voluntário (3 dias) = 3 × 6 = **18h**
- Coordenador (2 dias) = **30h** (evento completo)

### Configuração 3: Evento Intensivo (3 dias, 8h/dia)

```json
{
  "2027": {
    "carga_horaria": {
      "horas_por_dia": 8,
      "horas_por_evento": 24,
      "funcoes_evento_completo": [1, 2, 3, 4, 5]
    }
  }
}
```

**Resultados**:

- Palestrante (3 dias) = 3 × 8 = **24h**
- Voluntário (1 dia) = 1 × 8 = **8h**
- Organizador (1 dia) = **24h** (evento completo)

## 🔄 Alterando Configuração Existente

### Cenário: Aumentar Horas por Dia

```
Situação: Evento 2025 inicialmente 4h/dia, mas aumentou para 5h/dia

Antes:
"horas_por_dia": 4,
"horas_por_evento": 12

Depois:
"horas_por_dia": 5,
"horas_por_evento": 15
```

!!! warning "Impacto"

    Certificados gerados **após** a mudança usarão novas horas. Certificados já baixados não mudam.

### Cenário: Adicionar Função Especial

```
Situação: Decidiu que Fotógrafos também recebem carga completa

1. Identifique ID da função "Fotógrafo(a)": 8
2. Adicione ao array:

Antes:
"funcoes_evento_completo": [1, 2, 3]

Depois:
"funcoes_evento_completo": [1, 2, 3, 8]
```

### Cenário: Remover Função Especial

```
Situação: Moderadores não recebem mais carga completa

1. Identifique ID: Moderador(a) = 3
2. Remova do array:

Antes:
"funcoes_evento_completo": [1, 2, 3]

Depois:
"funcoes_evento_completo": [1, 2]
```

## 🧪 Testando Configuração

### Teste Manual

1. Criar participante teste com função normal
2. Marcar 2 dias de participação
3. Gerar certificado
4. Verificar: **carga = 2 × horas_por_dia**

5. Criar participante com função especial
6. Marcar 1 dia de participação
7. Gerar certificado
8. Verificar: **carga = horas_por_evento**

### Script de Teste

```python
# arquivo: utils/testar_carga_horaria.py
from app.services import servico_certificado

# Simular cálculo
evento_ano = 2025
funcao_id = 1  # Organizador
dias_participacao = ['20/05/2025']

carga, detalhes = servico_certificado.calcular_carga_horaria(
    evento_ano=evento_ano,
    funcao_id=funcao_id,
    dias_participacao=dias_participacao
)

print(f"Carga horária calculada: {carga}h")
print(f"Detalhes: {detalhes}")
```

Resultado esperado para função especial:

```
Carga horária calculada: 40h
Detalhes: Evento completo (função organizadora)
```

## 💡 Boas Práticas

### Definição de Horas

1. **Seja realista**: 4-6h/dia é típico para eventos sociais
2. **Considere preparação**: Organizadores têm horas extras de planejamento
3. **Padronize**: Use mesma duração em todos os dias (simplifica)
4. **Documente**: Anote motivos para horas escolhidas

### Funções Especiais

1. **Seja criterioso**: Apenas funções que realmente participam de todo evento
2. **Documente lista**: Mantenha registro de quais funções e por quê
3. **Comunique**: Informe coordenadores sobre funções especiais
4. **Revise anualmente**: Adapte para realidade de cada edição

### Alterações

1. **Faça antes do evento**: Não altere durante inscrições
2. **Comunique mudanças**: Avise equipe sobre alterações
3. **Teste após alterar**: Sempre gere certificado de teste
4. **Mantenha histórico**: Use Git para rastrear mudanças

## ⚠️ Problemas Comuns

### Problema: Carga Horária Está Errada

**Causa**: Configuração desatualizada ou dias marcados errados

**Diagnóstico**:

1. Verifique `certificate_config.json` para o ano
2. Confira dias de participação marcados no participante
3. Verifique se função está em `funcoes_evento_completo`

**Solução**:

- Corrija configuração ou dias de participação
- Regenere certificado

---

### Problema: Função Especial Não Recebe Carga Completa

**Causa**: ID da função não está no array

**Solução**:

1. Veja ID da função: **⚙️ Administração** → **🎭 Funções**
2. Adicione ID em `funcoes_evento_completo`
3. Teste novamente

---

### Problema: Todos Recebem Mesma Carga

**Causa**: Todas as funções estão marcadas como evento completo

**Solução**:

- Remova IDs desnecessários de `funcoes_evento_completo`
- Mantenha apenas funções que realmente participam de todo evento

---

!!! success "Carga Horária Configurada!"

    Com cálculo de horas configurado corretamente, seus certificados mostrarão informações precisas!
