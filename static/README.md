# Diretório Static - Imagens e Configurações

Este diretório contém as imagens e configurações utilizadas na geração dos certificados **organizadas por ano do evento**.

## Estrutura de Diretórios

```
static/
├── 2024/                      # Imagens do evento de 2024
│   ├── pint_logo.png
│   ├── pint_signature.png
│   └── sponsor_logo.png
├── 2025/                      # Imagens do evento de 2025
│   ├── pint_logo.png
│   ├── pint_signature.png
│   └── sponsor_logo.png
├── certificate_config.json    # Configurações de cores e imagens por ano
└── README.md                  # Este arquivo
```

## ⚠️ IMPORTANTE: Configuração por Ano

**Cada ano de evento mantém sua própria configuração visual independente:**

- ✅ Permite regenerar certificados de anos anteriores com design original
- ✅ Evita que alterações afetem certificados já emitidos
- ✅ Mantém histórico visual do evento ao longo dos anos
- ✅ Facilita gestão de patrocinadores diferentes por ano

## Arquivos de Imagem

### `{ano}/pint_logo.png`
- **Propósito**: Logo principal do Pint of Science
- **Localização no certificado**: Canto superior direito
- **Formato**: PNG/JPG/WEBP
- **Tamanho máximo**: 2MB
- **Recomendação**: Fundo transparente, dimensões aproximadas 400x400px

### `{ano}/pint_signature.png`
- **Propósito**: Assinatura digital do coordenador geral
- **Localização no certificado**: Parte inferior central
- **Formato**: PNG/JPG/WEBP
- **Tamanho máximo**: 2MB
- **Recomendação**: Fundo transparente, dimensões aproximadas 600x180px

### `{ano}/sponsor_logo.png`
- **Propósito**: Logo do(s) patrocinador(es)
- **Localização no certificado**: Coluna lateral esquerda (ocupa toda a altura)
- **Formato**: PNG/JPG/WEBP
- **Tamanho máximo**: 2MB
- **Recomendação**: Se houver múltiplos patrocinadores, criar uma composição única com todos os logos empilhados verticalmente

## Arquivo de Configuração

### `certificate_config.json`
Arquivo JSON contendo as configurações de cores e caminhos de imagens **por ano**.

**Nova estrutura (desde v2.0):**
```json
{
  "2024": {
    "cores": {
      "cor_primaria": "#e74c3c",
      "cor_secundaria": "#c0392b",
      "cor_texto": "#2c3e50",
      "cor_destaque": "#f39c12"
    },
    "imagens": {
      "pint_logo": "2024/pint_logo.png",
      "pint_signature": "2024/pint_signature.png",
      "sponsor_logo": "2024/sponsor_logo.png"
    }
  },
  "2025": {
    "cores": {
      "cor_primaria": "#e74c3c",
      "cor_secundaria": "#c0392b",
      "cor_texto": "#2c3e50",
      "cor_destaque": "#f39c12"
    },
    "imagens": {
      "pint_logo": "2025/pint_logo.png",
      "pint_signature": "2025/pint_signature.png",
      "sponsor_logo": "2025/sponsor_logo.png"
    }
  },
  "_default": {
    "cores": { ... },
    "imagens": { ... }
  }
}
```

**Explicação:**
- **Chave principal**: Ano do evento (string)
- **`cores`**: Paleta de cores específica do ano
- **`imagens`**: Caminhos relativos das imagens (dentro de `static/`)
- **`_default`**: Configuração fallback para anos não configurados

## Upload de Imagens

As imagens podem ser enviadas através da página de administração:
1. Faça login como Superadmin
2. Acesse **Administração** → **🖼️ Certificado**
3. **Selecione o ano do evento** no dropdown
4. Faça o upload das imagens nos campos correspondentes

## Configuração de Cores

As cores podem ser personalizadas através da página de administração:
1. Faça login como Superadmin
2. Acesse **Administração** → **🖼️ Certificado**
3. **Selecione o ano do evento** no dropdown
4. Escolha as cores usando os color pickers
5. Visualize o preview das cores
6. Salve a configuração

## Observações

- ✅ As configurações são **isoladas por ano** - não afetam outros anos
- ✅ Certificados gerados usam as configurações do **ano do evento**, não do ano atual
- ✅ Imagens são organizadas em subpastas por ano (`static/2024/`, `static/2025/`, etc.)
- ✅ O sistema mantém o aspect ratio das imagens automaticamente
- ⚠️ **IMPORTANTE**: Sempre configure o ano correto antes de fazer upload
- 💡 **Dica**: Faça backup das imagens antes de sobrescrever

## Exemplos de Uso

### Cenário 1: Configurar evento de 2025
1. Selecione "2025" no dropdown
2. Upload das 3 imagens → Salvas em `static/2025/`
3. Configure cores → Salvas na chave `"2025"` do JSON

### Cenário 2: Regenerar certificado de 2024
- Sistema automaticamente usa imagens de `static/2024/`
- Sistema usa cores da chave `"2024"` do JSON
- **Resultado**: Certificado idêntico ao design original de 2024

### Cenário 3: Novo evento (2026) sem configuração
- Sistema usa configuração `"_default"` como fallback
- Superadmin é notificado para criar configuração específica

## Migração de Configurações Antigas

Se você tem imagens na raiz de `static/` (estrutura antiga):

```bash
# Mover imagens para o ano correto
mkdir -p static/2024
mv static/pint_logo.png static/2024/
mv static/pint_signature.png static/2024/
mv static/sponsor_logo.png static/2024/
```

O sistema atualizará automaticamente o JSON quando fizer upload pela interface.
