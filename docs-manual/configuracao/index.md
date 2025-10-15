# Configuração do Sistema

Bem-vindo à documentação de **configuração** do Sistema Pint of Science Brasil! Esta seção contém guias para personalizar aspectos visuais e funcionais do sistema.

## 🎯 O que Pode ser Configurado?

O sistema permite configurar:

- 🖼️ **Imagens dos Certificados**: Logos, assinaturas e patrocinadores
- 🎨 **Cores e Fontes**: Personalização visual dos certificados
- ⏱️ **Carga Horária**: Cálculo de horas por função e evento
- ⚙️ **Configurações Avançadas**: Parâmetros técnicos e integrações

## 🚀 Acessando as Configurações

1. Faça login como **superadmin**
2. Acesse **⚙️ Administração** no menu lateral
3. Use as abas específicas:
   - **🖼️ Certificado** → Imagens e cores
   - **⏱️ Carga Horária** → Configuração de horas

## 📚 Guias de Configuração

### 🖼️ Imagens do Certificado

Configure logos e imagens que aparecem nos certificados PDF.

- [Guia completo de imagens](imagens-certificado.md)

**O que você pode fazer**:

- Upload do logo do Pint of Science
- Upload da assinatura digital
- Upload de logos de patrocinadores
- Configurar imagens diferentes por ano

### 🎨 Cores e Personalização

Customize as cores usadas nos certificados.

- [Guia de cores e fontes](cores-fontes.md)

**O que você pode fazer**:

- Definir cor primária
- Definir cor secundária
- Configurar cor do texto
- Configurar cor de destaque
- Definir cores diferentes por ano

### ⏱️ Carga Horária

Configure como a carga horária é calculada para diferentes funções.

- [Guia de carga horária](carga-horaria.md)

**O que você pode fazer**:

- Definir horas por dia de evento
- Definir horas totais do evento
- Especificar funções que recebem carga horária completa
- Configurar cálculo diferente por ano

### ⚙️ Configurações Avançadas

Parâmetros técnicos e integrações externas.

- [Guia de configurações avançadas](avancadas.md)

**O que você pode fazer**:

- Configurar integração com serviço de e-mail (Brevo)
- Definir chave de criptografia
- Configurar conexão com banco de dados
- Ajustar parâmetros de sessão

## 🔧 Estrutura de Arquivos de Configuração

### certificate_config.json

Arquivo principal de configuração dos certificados:

```
static/certificate_config.json
```

**Estrutura**:

```json
{
  "2024": {
    "cores": {...},
    "imagens": {...},
    "carga_horaria": {...}
  },
  "2025": {
    "cores": {...},
    "imagens": {...},
    "carga_horaria": {...}
  },
  "_default": {
    "cores": {...},
    "imagens": {...}
  }
}
```

### .env

Arquivo com configurações sensíveis e de ambiente:

```
.env (raiz do projeto)
```

**Conteúdo típico**:

```bash
DATABASE_URL=sqlite:///data/pint_of_science.db
ENCRYPTION_KEY=sua_chave_fernet_aqui
BREVO_API_KEY=sua_chave_brevo
BREVO_SENDER_EMAIL=contato@exemplo.com
```

### Imagens

Diretório com imagens dos certificados:

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
```

## 🎯 Configuração por Ano

### Por que Configurar por Ano?

Cada edição do Pint of Science pode ter:

- **Visual diferente**: Novas cores, novos logos
- **Patrocinadores diferentes**: Logos mudam a cada ano
- **Carga horária diferente**: Duração pode variar

### Como Funciona

1. **Sistema busca configuração do ano específico**

   ```
   Certificado 2025 → Busca config de 2025
   ```

2. **Se não encontrar, usa configuração padrão**

   ```
   Certificado 2026 (não configurado) → Usa _default
   ```

3. **Isso permite**:
   - Gerar certificados de anos passados com visual correto
   - Preparar configuração de anos futuros
   - Manter consistência histórica

## 📋 Checklist de Configuração

### Antes de Lançar Novo Evento

- [ ] **Imagens do certificado**

  - [ ] Logo do Pint of Science atualizado
  - [ ] Assinatura digital do coordenador geral
  - [ ] Logos dos patrocinadores

- [ ] **Cores**

  - [ ] Cor primária definida
  - [ ] Cor secundária definida
  - [ ] Cores testadas em certificado de amostra

- [ ] **Carga horária**

  - [ ] Horas por dia configuradas
  - [ ] Horas totais definidas
  - [ ] Funções especiais listadas

- [ ] **Teste completo**
  - [ ] Gerar certificado de teste
  - [ ] Verificar visual
  - [ ] Confirmar cálculos
  - [ ] Validar dados exibidos

### Durante o Evento

- [ ] Monitorar geração de certificados
- [ ] Verificar reclamações de participantes
- [ ] Corrigir problemas rapidamente

### Após o Evento

- [ ] Revisar estatísticas
- [ ] Arquivar configuração do ano
- [ ] Documentar mudanças para próximo ano

## 💡 Boas Práticas

### Para Gestão de Configurações

1. **Documente mudanças** - Anote alterações em cada ano
2. **Teste antes de produção** - Sempre gere certificado de teste
3. **Mantenha backup** - Copie arquivos de config regularmente
4. **Use versionamento** - Git para rastrear mudanças no certificate_config.json
5. **Comunique alterações** - Informe equipe sobre mudanças visuais

### Para Imagens

1. **Use formatos adequados** - PNG para logos com transparência
2. **Otimize tamanho** - Máximo 2MB por imagem
3. **Mantenha proporções** - Logos quadrados ou retangulares padronizados
4. **Teste em PDF** - Veja como aparece no certificado final

### Para Cores

1. **Use paleta consistente** - Cores que combinam entre si
2. **Considere legibilidade** - Contraste adequado texto/fundo
3. **Teste impressão** - Se certificados forem impressos, teste cores CMYK
4. **Documente códigos** - Anote hex codes para referência futura

## ⚠️ Cuidados Importantes

### Alterações em Produção

!!! danger "Atenção"

    Alterações de configuração afetam **certificados gerados após a mudança**. Certificados já baixados permanecem com configuração antiga.

### Backup Antes de Modificar

Sempre faça backup antes de alterações críticas:

```bash
# Backup do arquivo de configuração
cp static/certificate_config.json static/certificate_config.json.backup

# Backup das imagens
tar -czf static_backup_$(date +%Y%m%d).tar.gz static/
```

### Validação Após Alteração

Após qualquer mudança:

1. Gere certificado de teste
2. Verifique visual completo
3. Confirme dados corretos
4. Teste download

## 🔒 Segurança das Configurações

### Dados Sensíveis

!!! warning "Nunca Comite no Git"

    - `ENCRYPTION_KEY`
    - `BREVO_API_KEY`
    - Senhas de banco de dados
    - Tokens de API

Use `.env` (já no `.gitignore`) para dados sensíveis.

### Permissões de Acesso

- ✅ **Superadmins**: Acesso total às configurações
- ❌ **Coordenadores**: Não acessam configurações
- ❌ **Participantes**: Não veem configurações

### Auditoria

Alterações de configuração são registradas nos logs:

- Upload de imagens
- Mudança de cores
- Alteração de carga horária

## 🆘 Suporte

### Problemas Comuns

| Problema                          | Seção do Manual                   |
| --------------------------------- | --------------------------------- |
| Imagem não aparece no certificado | [Imagens](imagens-certificado.md) |
| Cores estão erradas               | [Cores](cores-fontes.md)          |
| Carga horária calculada errada    | [Carga Horária](carga-horaria.md) |
| E-mails não são enviados          | [Avançadas](avancadas.md)         |

### Contato

Para suporte técnico sobre configurações:

1. Consulte documentação específica
2. Verifique logs de erro
3. Entre em contato com equipe técnica

---

!!! success "Configuração Completa"

    Com todas as configurações ajustadas, seu sistema está pronto para gerar certificados profissionais e personalizados!
