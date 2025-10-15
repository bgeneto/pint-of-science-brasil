# 🖼️ Guia de Imagens para MkDocs

## Problema Resolvido

**Problema:** Imagens referenciadas como `static/2025/pint_logo.png` não apareciam no site gerado porque o MkDocs não tem acesso à pasta `static/` do projeto.

**Solução:** Copiar imagens para dentro da pasta `docs-manual/images/` e usar caminhos relativos corretos.

## 📁 Estrutura de Imagens

```
docs-manual/
├── images/                    # Pasta para todas as imagens da documentação
│   ├── pint_logo.png         # Logo do Pint of Science (copiado de static/)
│   ├── pint_signature.png    # Assinatura (copiado de static/)
│   ├── sponsor_logo.png      # Logo patrocinador (copiado de static/)
│   └── [suas screenshots aqui]
├── index.md                   # Página principal
├── participantes/
│   ├── como-se-inscrever.md
│   └── ...
└── coordenadores/
    └── ...
```

## 🔧 Como Adicionar Novas Imagens

### 1. Copiar do Projeto Static

```bash
# Copiar logos/assets existentes
cp static/2025/*.png docs-manual/images/

# Copiar de outros diretórios
cp path/to/image.png docs-manual/images/
```

### 2. Adicionar Screenshots

```bash
# Tire screenshots e salve na pasta images
# Nomeie de forma descritiva (sem espaços)
cp ~/Downloads/tela-inscricao.png docs-manual/images/tab-inscricao.png
cp ~/Downloads/tela-validacao.png docs-manual/images/validacao.png
```

### 3. Otimizar Imagens (Opcional)

```bash
# Redimensionar se muito grandes
convert docs-manual/images/screenshot.png -resize 1200x docs-manual/images/screenshot.png

# Ou usar ferramentas online como TinyPNG
```

## 📝 Como Referenciar no Markdown

### Caminho Relativo da Raiz

Para arquivos na raiz (`index.md`, `guia-rapido.md`, etc.):

```markdown
![Logo do Pint of Science](images/pint_logo.png)
![Screenshot da Tela](images/screenshot.png)
```

### Caminho Relativo de Subpasta

Para arquivos em subpastas (`participantes/*.md`, `coordenadores/*.md`):

```markdown
# De participantes/faq.md

![Screenshot](../images/screenshot.png)

# De administradores/gestao.md

![Logo](../images/pint_logo.png)
```

### Com Tamanho Personalizado

```markdown
![Logo](images/pint_logo.png){ width="300" }
![Screenshot](images/tela.png){ width="600" }
```

### Com Atributos HTML

```markdown
<img src="../images/logo.png" alt="Logo" width="300" style="border-radius: 10px;">
```

## ✅ Checklist de Imagens

Antes de adicionar uma imagem:

- ✔ Nome descritivo (sem espaços, use `-` ou `_`)
- ✔ Tamanho otimizado (<500KB idealmente)
- ✔ Formato adequado (PNG para logos, JPG para fotos)
- ✔ Copiar para `docs-manual/images/`
- ✔ Testar caminho relativo correto
- ✔ Adicionar texto alternativo (alt text)

## 🚀 Testando Imagens

### Build Local

```bash
mkdocs serve
# Acesse http://localhost:8000
# Verifique se imagens aparecem
```

### Build de Produção

```bash
mkdocs build
# Verifique em site/images/
ls -lh site/images/
```

### Verificar Console de Warnings

```bash
mkdocs build 2>&1 | grep -i "image\|png\|jpg"
# Não deve aparecer warnings sobre suas imagens
```

## 📦 Imagens no PDF

Quando gerar PDF, as imagens são incluídas automaticamente:

```bash
ENABLE_PDF_EXPORT=1 mkdocs build
# PDF em site/pdf/manual-usuario-pint-of-science.pdf
```

**Nota:** Imagens grandes podem aumentar o tamanho do PDF. Otimize antes!

## 🎨 Boas Práticas

### Nomes de Arquivo

✅ **Bom:**

- `pint_logo.png`
- `tela-inscricao.png`
- `validacao-certificado.png`
- `dashboard-coordenador.png`

❌ **Evite:**

- `Tela Inscrição.png` (espaços)
- `IMG_12345.png` (não descritivo)
- `screenshot.png` (genérico demais)
- `FOTO FINAL V2.png` (espaços, maiúsculas)

### Tamanhos Recomendados

| Tipo            | Largura     | Tamanho |
| --------------- | ----------- | ------- |
| Logo            | 200-400px   | <50KB   |
| Screenshot full | 1200-1600px | <300KB  |
| Icon/Thumbnail  | 64-128px    | <20KB   |
| Banner          | 800-1200px  | <200KB  |

### Formatos

- **PNG**: Logos, ícones, screenshots com texto
- **JPG**: Fotos, imagens com muitas cores
- **SVG**: Vetores (idealmente, mas nem sempre suportado em PDF)

## 🔄 Sincronizando com Static/

Se você atualizar imagens em `static/`, lembre-se de copiar para `docs-manual/images/`:

```bash
# Script para sincronizar (opcional)
#!/bin/bash
cp static/2025/*.png docs-manual/images/
echo "✅ Imagens sincronizadas!"
```

Ou adicione ao `.gitignore` se quiser link simbólico:

```bash
# NÃO RECOMENDADO (problemas no build)
# ln -s ../../static/2025 docs-manual/images/static
```

## 📊 Imagens Atuais

Imagens já disponíveis em `docs-manual/images/`:

- ✅ `pint_logo.png` (14KB) - Logo oficial
- ✅ `pint_signature.png` (33KB) - Assinatura
- ✅ `sponsor_logo.png` (121KB) - Logo patrocinador

Screenshots pendentes (mencionados na doc mas não existem ainda):

- ⏳ `tab-inscricao.png` - Aba de inscrição
- ⏳ `tab-download.png` - Aba de download
- ⏳ `validacao.png` - Página de validação
- ⏳ `dashboard-participantes.png` - Dashboard coordenador
- ⏳ Outros screenshots conforme necessário

## 🆘 Troubleshooting

### Imagem não aparece no site

1. **Verifique o caminho:**

   ```bash
   ls -lh docs-manual/images/sua-imagem.png
   ```

2. **Verifique caminho relativo:**

   - Raiz: `images/arquivo.png`
   - Subpasta: `../images/arquivo.png`

3. **Rebuild:**
   ```bash
   mkdocs build --clean
   mkdocs serve
   ```

### Imagem aparece quebrada

1. **Formato correto?** PNG/JPG funcionam melhor
2. **Arquivo corrompido?** Tente abrir localmente
3. **Permissões?** `chmod 644 docs-manual/images/*.png`

### Imagem muito grande no site

```markdown
# Reduzir tamanho inline

![Texto](images/grande.png){ width="600" }

# Ou usar CSS

<img src="images/grande.png" style="max-width: 800px;">
```

## 📚 Recursos

- [MkDocs Images Documentation](https://www.mkdocs.org/user-guide/writing-your-docs/#images-and-media)
- [Material for MkDocs - Images](https://squidfunk.github.io/mkdocs-material/reference/images/)
- [TinyPNG - Otimizador Online](https://tinypng.com/)
- [ImageMagick - CLI Tool](https://imagemagick.org/)

---

**Última atualização:** 2025-10-15
**Status:** ✅ Problema resolvido - Imagens funcionando corretamente
