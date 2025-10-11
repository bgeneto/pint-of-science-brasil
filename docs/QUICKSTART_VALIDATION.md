# Guia Rápido: Sistema de Validação de Certificados

## 🎯 O que foi implementado?

Sistema completo de validação de certificados **sem armazenar PDFs**, usando assinatura digital HMAC-SHA256.

## ✨ Novidades

1. **Link de validação no certificado**: Todo PDF agora inclui um link clicável no rodapé
2. **Página pública de validação**: `/Validar_Certificado` permite que qualquer pessoa verifique autenticidade
3. **Hash único por certificado**: Impossível falsificar sem a chave secreta
4. **Sem armazenamento de PDFs**: Validação feita contra dados do banco

## 🚀 Como instalar (atualização)

### 1. Gerar chave secreta para certificados

```bash
# Opção 1: Usando o script auxiliar
python utils/generate_certificate_key.py

# Opção 2: Diretamente com Python
python -c "import secrets; print('CERTIFICATE_SECRET_KEY=' + secrets.token_hex(32))"
```

**Saída exemplo:**
```
CERTIFICATE_SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

### 2. Adicionar ao arquivo `.env`

Abra seu `.env` e adicione:

```bash
# Certificate Secret Key para validação HMAC
CERTIFICATE_SECRET_KEY=sua_chave_de_64_caracteres_aqui

# BASE_URL (se ainda não tiver)
BASE_URL=http://localhost:8501  # ou seu domínio em produção
```

⚠️ **IMPORTANTE**:
- Esta chave é **crítica** - não compartilhe publicamente
- Faça backup em local seguro
- Use a **mesma chave** em dev e prod

### 3. Executar migração do banco de dados

```bash
# Adicionar coluna hash_validacao e gerar hashes para certificados existentes
python utils/migrate_add_hash_validation.py
```

**O script vai:**
- ✅ Adicionar coluna `hash_validacao` na tabela `participantes`
- ✅ Gerar hashes para todos os participantes validados
- ✅ Exibir relatório de sucesso/erros

### 4. Reiniciar a aplicação

```bash
# Se estiver usando Streamlit diretamente
streamlit run 🏠_Home.py

# Se estiver usando Docker
docker-compose restart
```

## 🎉 Como testar

### Teste 1: Gerar novo certificado

1. Login como coordenador/superadmin
2. Validar um participante
3. Baixar certificado como participante
4. Verificar no PDF:
   - Link clicável no rodapé
   - Formato: `https://seu-dominio.com/Validar_Certificado?hash=...`

### Teste 2: Validar certificado

1. Copiar o código de 64 caracteres do certificado
2. Acessar `/Validar_Certificado`
3. Colar o código
4. Clicar em "Validar Certificado"
5. Deve mostrar: ✅ CERTIFICADO AUTÊNTICO

### Teste 3: Detectar falsificação

1. Pegar o código de um certificado válido
2. Modificar 1 caractere do código
3. Tentar validar
4. Deve mostrar: ❌ CERTIFICADO NÃO ENCONTRADO

## 📋 Checklist de produção

Antes de colocar em produção, verifique:

- [ ] `CERTIFICATE_SECRET_KEY` definida no `.env`
- [ ] Chave tem exatamente 64 caracteres hexadecimais
- [ ] Backup da chave em local seguro (senha manager, vault, etc.)
- [ ] `BASE_URL` aponta para domínio de produção (https://...)
- [ ] Migração executada com sucesso
- [ ] Teste manual funcionando
- [ ] Certificados antigos (se houver) receberam hash

## 🔍 Arquivos modificados

```
Novos arquivos:
├── pages/3_✅_Validar_Certificado.py        # Página pública de validação
├── utils/generate_certificate_key.py         # Gerador de chave secreta
├── utils/migrate_add_hash_validation.py      # Migração do banco
└── docs/CERTIFICATE_VALIDATION.md            # Documentação completa

Arquivos modificados:
├── app/models.py                              # Adicionado campo hash_validacao
├── app/core.py                                # Adicionado CERTIFICATE_SECRET_KEY e BASE_URL
├── app/services.py                            # Funções de geração/verificação de hash
├── .env.example                               # Documentação das novas env vars
└── README.md                                  # Atualizado com nova funcionalidade
```

## 🆘 Troubleshooting

### Erro: "CERTIFICATE_SECRET_KEY não configurada"

**Solução**: Adicionar `CERTIFICATE_SECRET_KEY` no `.env` usando o script de geração.

### Erro: "no such column: hash_validacao"

**Solução**: Executar o script de migração:
```bash
python utils/migrate_add_hash_validation.py
```

### Certificado mostra "NÃO ENCONTRADO" mas é válido

**Possíveis causas:**
1. Hash não foi gerado (executar migração)
2. Chave secreta diferente entre dev/prod
3. Dados do participante foram modificados após emissão

### Link no PDF não é clicável

**Causa**: `BASE_URL` não está configurado ou está incorreto.

**Solução**: Verificar/corrigir `BASE_URL` no `.env` e regenerar certificado.

## 📚 Documentação completa

Para entender o funcionamento interno, arquitetura de segurança e casos de uso avançados:

👉 [`docs/CERTIFICATE_VALIDATION.md`](../docs/CERTIFICATE_VALIDATION.md)

## 🎯 Próximos passos

Após instalação:

1. Testar validação com certificados reais
2. Comunicar aos participantes sobre a nova funcionalidade
3. Adicionar link de validação em emails enviados
4. Configurar monitoramento (opcional):
   - Log de tentativas de validação
   - Alertas para hashes inválidos (possível ataque)

---

**Dúvidas?** Consulte a documentação completa ou abra uma issue no GitHub.
