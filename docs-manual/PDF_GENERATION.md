# Geração de Documentação em PDF

Este projeto usa uma abordagem **profissional e robusta** para gerar PDFs a partir da documentação MkDocs:

## 🎯 Arquitetura

```
MkDocs Material → HTML Perfeito → WeasyPrint → PDF Profissional
```

### Benefícios desta Abordagem

✅ **Separação de responsabilidades**: MkDocs faz HTML, WeasyPrint faz PDF
✅ **Layout perfeito**: Usa o HTML já renderizado pelo Material theme
✅ **Confiável**: Não depende de plugins bugados
✅ **Rápido**: ~8 segundos vs 30+ segundos do plugin
✅ **Todas as páginas**: 27 artigos completos incluídos
✅ **Sem símbolos indesejados**: Remove automaticamente ¶ e outros permalinks

## 🚀 Como Usar

### Opção 1: Script Interativo (Recomendado)

```bash
./build-docs.sh
```

Escolha a opção desejada no menu:

- **1**: Servidor local para desenvolvimento
- **2**: Build HTML apenas
- **3**: Gerar PDF apenas
- **4**: Build completo (HTML + PDF)
- **5**: Limpar builds anteriores

### Opção 2: Comandos Diretos

```bash
# Gerar apenas HTML
mkdocs build --clean

# Gerar apenas PDF (requer HTML já gerado)
python3 generate_pdf.py

# Gerar ambos
mkdocs build --clean && python3 generate_pdf.py
```

### Opção 3: Com Parâmetros

```bash
# PDF com verbose logging
python3 generate_pdf.py --verbose

# PDF em local customizado
python3 generate_pdf.py --output docs/manual.pdf

# Especificar diretório do site
python3 generate_pdf.py --site-dir build
```

## 📄 Arquivos Gerados

| Arquivo                        | Descrição                  | Tamanho |
| ------------------------------ | -------------------------- | ------- |
| `site/`                        | Documentação HTML completa | ~5 MB   |
| `site/pdf/manual-completo.pdf` | PDF profissional           | ~630 KB |

## 🔧 Tecnologias

- **MkDocs Material**: Geração de HTML com tema Material Design
- **WeasyPrint**: Conversão profissional HTML → PDF
- **BeautifulSoup**: Processamento e limpeza do HTML
- **Python 3.11+**: Runtime

## 📝 Estrutura do Código

```
generate_pdf.py          # Script principal de geração
├── MkDocsPDFGenerator   # Classe principal
│   ├── get_navigation_pages()     # Extrai navegação do index.html
│   ├── create_combined_html()     # Combina todas as páginas
│   └── generate_pdf()             # Gera o PDF final
└── main()               # Entry point com CLI
```

## 🎨 Customização

### Estilos CSS

Os estilos estão embutidos no `generate_pdf.py` (linhas 78-357). Para customizar:

1. Edite as regras CSS na string de estilos
2. Execute novamente: `python3 generate_pdf.py`

### Fontes

Atualmente usa **Google Fonts Roboto**:

- Body: Roboto 10pt
- Headers: Roboto Condensed
- Code: Roboto Mono

Para mudar, edite o `@import` no CSS e as regras `font-family`.

### Layout da Capa

Edite o template da capa em `create_combined_html()` (linha 377-386).

## 🐛 Troubleshooting

### Erro: "Site directory not found"

**Solução**: Gere o HTML primeiro com `mkdocs build`

### Erro: "WeasyPrint not installed"

**Solução**: Instale com `pip install weasyprint`

### Erro: "BeautifulSoup not installed"

**Solução**: Instale com `pip install beautifulsoup4`

### Warnings sobre "Anchor defined twice"

**Normal**: São avisos do WeasyPrint sobre âncoras duplicadas. Não afeta o PDF final.

### Erro ao carregar imagem

**Causa**: Imagem referenciada mas não encontrada no `site/`
**Solução**: Verifique os caminhos das imagens no Markdown original

## 📊 Comparação com Plugin mkdocs-with-pdf

| Aspecto             | `mkdocs-with-pdf`      | `generate_pdf.py` |
| ------------------- | ---------------------- | ----------------- |
| **Páginas geradas** | ❌ 12 páginas          | ✅ 27 páginas     |
| **Tempo**           | 🐌 30+ segundos        | ⚡ 8 segundos     |
| **Confiabilidade**  | ⚠️ Bugs frequentes     | ✅ Estável        |
| **Permalinks**      | ❌ Símbolos ¶ visíveis | ✅ Removidos      |
| **Layout**          | ⚠️ Inconsistente       | ✅ Perfeito       |
| **Tamanho arquivo** | 5.5 MB                 | 630 KB            |

## 🔒 Sem Modificar o MkDocs

Esta solução **não interfere** com:

- Configuração do MkDocs (`mkdocs.yml`)
- Site HTML gerado
- Tema Material
- Navegação e busca

O PDF é gerado **separadamente** a partir do HTML já pronto.

## 📚 Mais Informações

- [WeasyPrint Documentation](https://weasyprint.readthedocs.io/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## 🤝 Contribuindo

Para melhorar o gerador de PDF:

1. Edite `generate_pdf.py`
2. Teste com `python3 generate_pdf.py --verbose`
3. Valide o PDF gerado
4. Commit suas mudanças

## 📄 Licença

Mesmo do projeto principal.
