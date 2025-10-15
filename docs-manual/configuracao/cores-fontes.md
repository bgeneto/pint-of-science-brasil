# Cores e Personalização

Guia completo para personalizar cores dos certificados do Pint of Science Brasil.

## 🎨 Cores do Certificado

Os certificados usam **4 cores configuráveis**:

| Cor            | Uso                        | Padrão (2025)             |
| -------------- | -------------------------- | ------------------------- |
| **Primária**   | Títulos, bordas principais | #e74c3c (vermelho)        |
| **Secundária** | Subtítulos, detalhes       | #c0392b (vermelho escuro) |
| **Texto**      | Texto principal do corpo   | #2c3e50 (azul escuro)     |
| **Destaque**   | Elementos de ênfase        | #f39c12 (laranja)         |

## 🚀 Acessando Configuração

1. Login como **superadmin**
2. Menu **⚙️ Administração**
3. Aba **🖼️ Certificado**
4. Seção "Configurar Cores do Certificado"

## 🎨 Configurando Cores

### Via Interface Web

1. Selecione o **ano** no dropdown
2. Use os **color pickers** para cada cor:
   - Cor Primária
   - Cor Secundária
   - Cor de Texto
   - Cor de Destaque
3. Clique em **"💾 Salvar Cores"**
4. Gere certificado teste para ver resultado

### Via Arquivo JSON

Edite `static/certificate_config.json`:

```json
{
  "2025": {
    "cores": {
      "cor_primaria": "#e74c3c",
      "cor_secundaria": "#c0392b",
      "cor_texto": "#2c3e50",
      "cor_destaque": "#f39c12"
    }
  }
}
```

## 🎯 Onde Cada Cor é Usada

### Cor Primária

Usada em:

- Título principal ("Certificado")
- Borda externa do certificado
- Linha decorativa superior
- Elementos gráficos principais

### Cor Secundária

Usada em:

- Subtítulos
- Nome do evento
- Linha decorativa inferior
- Elementos de apoio

### Cor de Texto

Usada em:

- Corpo do texto do certificado
- Nome do participante (em negrito)
- Informações de data, local, função
- Carga horária por extenso

### Cor de Destaque

Usada em:

- Nome do participante (pode ter cor especial)
- Números importantes (carga horária)
- Elementos que precisam chamar atenção

## 🎨 Paletas Recomendadas

### Paleta 1: Clássica Pint of Science (2024)

```json
{
  "cor_primaria": "#e7ad3c", // Dourado
  "cor_secundaria": "#322bc0", // Azul profundo
  "cor_texto": "#000000", // Preto
  "cor_destaque": "#f39c12" // Laranja
}
```

Visual: Elegante, tradicional, sério

### Paleta 2: Moderna Vibrante (2025)

```json
{
  "cor_primaria": "#e74c3c", // Vermelho vibrante
  "cor_secundaria": "#c0392b", // Vermelho escuro
  "cor_texto": "#2c3e50", // Azul petróleo
  "cor_destaque": "#f39c12" // Laranja
}
```

Visual: Moderno, energético, jovial

### Paleta 3: Ciência Verde

```json
{
  "cor_primaria": "#27ae60", // Verde esperança
  "cor_secundaria": "#229954", // Verde escuro
  "cor_texto": "#2c3e50", // Azul escuro
  "cor_destaque": "#f39c12" // Laranja
}
```

Visual: Sustentável, científico, fresco

### Paleta 4: Azul Acadêmico

```json
{
  "cor_primaria": "#3498db", // Azul céu
  "cor_secundaria": "#2980b9", // Azul marinho
  "cor_texto": "#34495e", // Cinza escuro
  "cor_destaque": "#e67e22" // Laranja queimado
}
```

Visual: Profissional, acadêmico, confiável

## 🔧 Ferramentas Úteis

### Seleção de Cores

- **Adobe Color**: color.adobe.com (criar paletas harmoniosas)
- **Coolors**: coolors.co (gerador de paletas)
- **Color Hunt**: colorhunt.co (paletas prontas)
- **Paletton**: paletton.com (teoria das cores)

### Conversão de Cores

- **RGB para HEX**: `rgb(231, 76, 60)` → `#e74c3c`
- **HEX para RGB**: `#e74c3c` → `rgb(231, 76, 60)`

### Teste de Contraste

- **WebAIM Contrast Checker**: Verifica legibilidade texto/fundo
- **Contrast Ratio**: contrastrat io.com

## 💡 Boas Práticas

### Legibilidade

1. **Contraste adequado**: Texto escuro em fundo claro (ou vice-versa)
2. **Mínimo 4.5:1**: Razão de contraste para texto normal
3. **Mínimo 3:1**: Para textos grandes/títulos
4. **Teste impressão**: Cores podem parecer diferentes em papel

### Harmonia

1. **Use paleta consistente**: Cores que combinam entre si
2. **Máximo 4 cores**: Evite poluição visual
3. **Hierarquia clara**: Primária > Secundária > Texto > Destaque
4. **Considere daltonismo**: Evite depender só de vermelho/verde

### Identidade Visual

1. **Mantenha coerência**: Com identidade do Pint of Science
2. **Adapte por ano**: Pode variar, mas mantenha essência
3. **Documente escolhas**: Anote motivos das cores escolhidas
4. **Peça feedback**: Teste com diferentes pessoas

## 🧪 Testando Cores

### Passo a Passo

1. Configure cores para o ano
2. Crie participante teste
3. Gere certificado
4. Verifique:
   - ✔ Título legível
   - ✔ Texto corpo legível
   - ✔ Nome destaca adequadamente
   - ✔ Cores harmoniosas
   - ✔ Não há elementos invisíveis

### Teste de Impressão

Se certificados serão impressos:

1. Imprima amostra em impressora colorida
2. Verifique se cores saem como esperado
3. Teste em diferentes papéis (sulfite, couchê)
4. Ajuste se necessário (cores digitais ≠ impressas)

### Teste de Acessibilidade

1. Visualize em escala de cinza (simula daltonismo)
2. Use ferramenta de contraste
3. Peça feedback de pessoas com deficiência visual

## 🎯 Exemplos de Configuração

### Exemplo 1: Manter Padrão

```json
// Não alterar, usar cores default do sistema
{
  "2025": {
    // Se não especificar "cores", usa _default
  }
}
```

Sistema busca em `_default` automaticamente.

### Exemplo 2: Personalizar Ano

```json
// Cores específicas para 2026
{
  "2026": {
    "cores": {
      "cor_primaria": "#8e44ad", // Roxo
      "cor_secundaria": "#9b59b6", // Roxo claro
      "cor_texto": "#2c3e50", // Azul escuro
      "cor_destaque": "#f39c12" // Laranja
    }
  }
}
```

### Exemplo 3: Evento Temático

```json
// Tema "Oceanos" - tons de azul
{
  "2027": {
    "cores": {
      "cor_primaria": "#3498db", // Azul oceano
      "cor_secundaria": "#2980b9", // Azul profundo
      "cor_texto": "#1a5276", // Azul marinho
      "cor_destaque": "#16a085" // Verde-azulado
    }
  }
}
```

## ⚠️ Problemas Comuns

### Problema: Cores Não Aparecem no Certificado

**Causa**: Configuração não foi salva ou ano incorreto

**Solução**:

1. Verifique `certificate_config.json`
2. Confirme que seção do ano existe
3. Verifique sintaxe JSON (vírgulas, aspas)
4. Regenere certificado

---

### Problema: Texto Ilegível

**Causa**: Contraste insuficiente

**Solução**:

1. Use ferramenta de teste de contraste
2. Escureça cor de texto ou clareie fundo
3. Teste com pessoas reais
4. Ajuste até legível

---

### Problema: Cores Diferentes na Impressão

**Causa**: RGB (digital) vs CMYK (impressão)

**Solução**:

1. Cores digitais são RGB, impressoras usam CMYK
2. Faça teste de impressão antes de finalizar
3. Ajuste cores conforme necessário
4. Considere usar cores "print-safe"

---

### Problema: Cores Mudaram Sozinhas

**Causa**: Arquivo JSON foi sobrescrito ou cache

**Solução**:

1. Verifique conteúdo de `certificate_config.json`
2. Restaure de backup se necessário
3. Limpe cache do navegador
4. Regenere certificado

---

!!! success "Cores Configuradas!"

    Com cores bem escolhidas, seus certificados terão identidade visual marcante e profissional!
