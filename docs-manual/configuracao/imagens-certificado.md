# Imagens do Certificado

Guia completo para configurar imagens que aparecem nos certificados PDF do Pint of Science Brasil.

## 🎯 Imagens Utilizadas

Os certificados usam **3 tipos de imagens**:

| Imagem                   | Onde Aparece    | Tamanho Recomendado |
| ------------------------ | --------------- | ------------------- |
| **Logo Pint of Science** | Topo central    | 200x100px (PNG)     |
| **Assinatura Digital**   | Rodapé central  | 300x80px (PNG)      |
| **Logo Patrocinador**    | Lateral direita | 150x350px (PNG)     |

!!! info "Formato"

    Use sempre **PNG** para manter transparência e qualidade. Máximo **2MB** por imagem.

## 🚀 Acessando Configuração de Imagens

1. Login como **superadmin**
2. Menu **⚙️ Administração**
3. Aba **🖼️ Certificado**
4. Seção "Gerenciar Imagens do Certificado"

## 📤 Upload de Imagens

### Selecionando o Ano

1. No topo da seção, selecione o **ano** no dropdown
2. Sistema mostra status das imagens para aquele ano:
   - ✓ Logo disponível
   - ⚠️ Logo não encontrado

### Upload do Logo Pint of Science

1. Clique em **"Upload Logo Principal"**
2. Selecione arquivo PNG/JPG (max 2MB)
3. Aguarde confirmação: "✅ Logo salvo! (XX KB)"

**Onde é usado**: Topo central do certificado, identifica o evento.

### Upload da Assinatura

1. Clique em **"Upload Assinatura"**
2. Selecione imagem da assinatura digital
3. Aguarde confirmação: "✅ Assinatura salva!"

**Onde é usado**: Rodapé, valida autenticidade do certificado.

### Upload do Logo do Patrocinador

1. Clique em **"Upload Logo Patrocinador"**
2. Selecione logo único ou composição de logos
3. Aguarde confirmação: "✅ Logo salvo!"

**Onde é usado**: Coluna lateral direita do certificado.

!!! tip "Múltiplos Patrocinadores"

    Se houver vários patrocinadores, crie uma **imagem única** com todos os logos organizados verticalmente antes do upload.

## 📁 Estrutura de Diretórios

As imagens são salvas em:

```
static/
├── 2024/
│   ├── pint_logo.png
│   ├── pint_signature.png
│   └── sponsor_logo.png
├── 2025/
│   ├── pint_logo.png
│   ├── pint_signature.png
│   └── sponsor_logo.png
└── 2026/
    ├── pint_logo.png
    ├── pint_signature.png
    └── sponsor_logo.png
```

Cada ano tem seu próprio diretório.

## ⚙️ Configuração Automática

Após upload, o sistema atualiza automaticamente:

```json
// static/certificate_config.json
{
  "2025": {
    "imagens": {
      "pint_logo": "2025/pint_logo.png",
      "pint_signature": "2025/pint_signature.png",
      "sponsor_logo": "2025/sponsor_logo.png"
    }
  }
}
```

Não é necessário editar o JSON manualmente.

## 🎨 Especificações Técnicas

### Logo Principal (Pint of Science)

```
Formato: PNG (transparência recomendada)
Dimensões ideais: 200x100px
Dimensões máximas: 400x200px
Tamanho arquivo: < 500KB
Proporção: 2:1 (largura:altura)
```

**Dicas**:

- Fundo transparente para melhor integração
- Alta resolução (pelo menos 150 DPI)
- Cores vibrantes (será exibido colorido)

### Assinatura Digital

```
Formato: PNG (transparência recomendada)
Dimensões ideais: 300x80px
Dimensões máximas: 400x120px
Tamanho arquivo: < 300KB
Proporção: 4:1 (largura:altura)
```

**Dicas**:

- Escaneie assinatura em alta resolução
- Remova fundo (deixe transparente)
- Use linha preta ou azul escuro
- Pode incluir nome digitado abaixo da assinatura

### Logo Patrocinador

```
Formato: PNG (transparência recomendada)
Dimensões ideais: 150x350px
Tamanho arquivo: < 2MB
Proporção: ~2.3:1 (altura:largura)
```

**Dicas**:

- Se múltiplos logos, organize verticalmente
- Mantenha espaçamento entre logos
- Use alta resolução
- Proporção ideal: altura = 2,35 × largura

## 🔄 Alterando Imagens

### Substituir Imagem Existente

1. Selecione o ano
2. Faça upload da nova imagem
3. Sistema sobrescreve automaticamente
4. Certificados gerados após usarão nova imagem

!!! warning "Certificados Antigos"

    Certificados já gerados/baixados **não são alterados**. Apenas novos certificados usam nova imagem.

### Configurar Ano Futuro

```
Situação: Preparar imagens para 2026

Ação:
1. Selecionar "2026" no dropdown
2. Fazer upload das 3 imagens
3. Sistema cria pasta 2026/ automaticamente
4. Configuração salva em certificate_config.json
```

## 🧪 Testando Imagens

### Gerar Certificado de Teste

Após upload:

1. Vá para aba **👨‍👨‍👦‍👦 Participantes** (se coordenador)
2. Selecione um participante teste
3. Clique em "Baixar Certificado"
4. Abra PDF e verifique:
   - Logo aparece centralizado no topo
   - Assinatura aparece no rodapé
   - Logo patrocinador na lateral direita
   - Imagens nítidas e bem posicionadas

### Checklist de Validação

- ✔ Logo principal visível e centralizado
- ✔ Assinatura legível no rodapé
- ✔ Logo patrocinador na lateral
- ✔ Todas as imagens nítidas (não pixelizadas)
- ✔ Proporções adequadas (não distorcidas)
- ✔ Cores corretas
- ✔ Texto do certificado não sobrepõe imagens

## 🎯 Casos de Uso

### Caso 1: Configurar Primeiro Evento

```
Preparar imagens para Pint of Science 2025

Passos:
1. Obter logo oficial do Pint of Science
2. Escanear assinatura do coordenador geral
3. Receber logos dos patrocinadores
4. Criar composição de logos (se múltiplos)
5. Fazer upload das 3 imagens para ano 2025
6. Gerar certificado teste
7. Ajustar se necessário
```

### Caso 2: Trocar Assinatura

```
Novo coordenador geral assume em 2026

Ação:
1. Escanear nova assinatura
2. Tratar imagem (remover fundo, ajustar tamanho)
3. Selecionar ano 2026
4. Upload da nova assinatura
5. Manter logos anteriores (ou atualizar se mudaram)
```

### Caso 3: Novo Patrocinador

```
Evento 2026 tem novo patrocinador

Ação:
1. Receber logo do novo patrocinador
2. Abrir editor de imagem (Photoshop, GIMP, etc)
3. Criar composição vertical com todos os logos:
   - Logo Patrocinador A
   - Espaço
   - Logo Patrocinador B
   - Espaço
   - Logo Patrocinador C (novo)
4. Exportar PNG (150x350px aprox)
5. Fazer upload para ano 2026
```

## 🛠️ Ferramentas Recomendadas

### Edição de Imagens

- **GIMP** (gratuito): Remover fundos, redimensionar
- **Photoshop**: Edição profissional
- **Canva**: Criar composições de logos
- **Remove.bg**: Remover fundo de imagens online

### Otimização

- **TinyPNG**: Comprimir PNG sem perder qualidade
- **ImageOptim** (Mac): Otimizar imagens
- **Squoosh**: Otimizador online

### Conversão

- **CloudConvert**: Converter formatos
- **OnlineConvert**: JPG ↔ PNG

## ⚠️ Problemas Comuns

### Problema: "Arquivo muito grande"

**Causa**: Imagem com mais de 2MB

**Solução**:

1. Use ferramenta de compressão (TinyPNG)
2. Reduza dimensões (mantenha proporção)
3. Exporte com qualidade 85-90%

---

### Problema: Imagem Aparece Pixelizada

**Causa**: Resolução muito baixa

**Solução**:

1. Use imagem com pelo menos 150 DPI
2. Dimensões mínimas recomendadas
3. Não redimensione imagens pequenas

---

### Problema: Logo Patrocinador Cortado

**Causa**: Proporção inadequada

**Solução**:

1. Ajuste para proporção ~2.3:1 (altura:largura)
2. Exemplo: se largura = 150px, altura = 350px
3. Use editor para ajustar canvas

---

### Problema: Fundo Branco Aparece

**Causa**: Imagem não tem transparência

**Solução**:

1. Abra em GIMP/Photoshop
2. Remova fundo
3. Salve como PNG (não JPG)
4. Faça novo upload

---

!!! success "Imagens Configuradas!"

    Com imagens de alta qualidade configuradas, seus certificados terão aparência profissional!
