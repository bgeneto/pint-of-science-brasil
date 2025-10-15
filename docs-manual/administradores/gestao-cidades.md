# Gestão de Cidades

Guia completo para cadastrar e gerenciar cidades participantes do Pint of Science Brasil.

## 🎯 O que são Cidades?

Cidades representam os **municípios participantes** do evento Pint of Science. Cada cidade tem:

- **Nome**: Nome do município (ex: Brasília, São Paulo)
- **Estado**: Sigla UF (ex: DF, SP, RJ)
- **Identificador único**: Nome-Estado (ex: Brasília-DF)

!!! info "Importância"

    As cidades são fundamentais para:
    - Organizar participantes por localidade
    - Associar coordenadores às suas regiões
    - Gerar estatísticas regionais
    - Filtrar dados por localização

## 🚀 Acessando a Gestão

1. Faça login como superadmin
2. Acesse **⚙️ Administração** no menu lateral
3. Clique na aba **🏙️ Cidades**

Você verá duas seções:

- **Criar Nova Cidade** (formulário)
- **Cidades Cadastradas** (tabela de visualização)

## ➕ Criando Nova Cidade

### Passo a Passo

1. Preencha o formulário "Criar Nova Cidade":

   - **Nome da Cidade**: Digite o nome do município
   - **Estado (UF)**: Selecione o estado no dropdown

2. Clique em **"🏙️ Criar Cidade"**

### Campos Obrigatórios

| Campo      | Tipo    | Validação                     | Observação            |
| ---------- | ------- | ----------------------------- | --------------------- |
| **Nome**   | Texto   | Obrigatório, único por estado | Nome do município     |
| **Estado** | Seleção | Obrigatório                   | Sigla UF com 2 letras |

### Estados Disponíveis

O dropdown contém todos os 27 estados brasileiros:

```
AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA,
PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO
```

### Exemplo de Criação

```
Nome da Cidade: Brasília
Estado (UF): DF

Resultado: Cidade "Brasília-DF" criada
```

### Validações Automáticas

O sistema valida:

- ✅ Nome e estado são obrigatórios
- ✅ Combinação nome + estado deve ser única
- ✅ Não permite duplicatas (mesma cidade no mesmo estado)
- ✅ Sigla do estado deve ter exatamente 2 letras

## 📊 Visualizando Cidades

### Tabela de Cidades Cadastradas

A tabela mostra todas as cidades em ordem alfabética:

| Coluna       | Descrição                              |
| ------------ | -------------------------------------- |
| **ID**       | Identificador único do banco de dados  |
| **Nome**     | Nome do município                      |
| **Estado**   | Sigla UF                               |
| **Completo** | Nome-Estado (formato usado no sistema) |

### Exemplo de Dados

```
ID: 15
Nome: Goiânia
Estado: GO
Completo: Goiânia-GO
```

### Ordenação

- Cidades são automaticamente ordenadas por **Nome-Estado** (ordem alfabética)
- Facilita localização visual de cidades

## 🗑️ Deletando Cidades

!!! warning "Funcionalidade Limitada"

    A interface atual não permite deleção direta de cidades pela aba. Isso é intencional para prevenir deleção acidental.

### Como Deletar Cidade (se necessário)

Para deletar uma cidade, você precisa:

1. Verificar que **não há participantes** associados
2. Verificar que **não há coordenadores** associados
3. Usar acesso direto ao banco de dados ou ferramenta administrativa

### Regras de Proteção

O sistema protege contra deleção se:

❌ **Há participantes da cidade**

- Dados históricos devem ser preservados
- Certificados já foram gerados

❌ **Há coordenadores associados**

- Remove associações primeiro
- Ou reatribua coordenadores

✅ **Cidade sem vínculos**

- Pode ser deletada com segurança
- Geralmente é erro de cadastro

## 🎯 Casos de Uso Comuns

### Caso 1: Cadastrar Cidades para Novo Evento

```
Situação: Pint of Science 2026 terá novos municípios

Ação:
1. Acessar aba "🏙️ Cidades"
2. Para cada nova cidade:
   - Digite nome
   - Selecione estado
   - Clique "Criar Cidade"
3. Exemplo:
   - Palmas-TO
   - Boa Vista-RR
   - Rio Branco-AC
```

### Caso 2: Correção de Nome Errado

```
Situação: Cidade foi cadastrada com nome errado

Problema: Cadastrou "Goiania" sem acento
Correto: Deveria ser "Goiânia"

Ação:
Como a tabela não é editável diretamente:
1. Criar cidade correta: "Goiânia-GO"
2. Reatribuir participantes e coordenadores
3. Deletar cidade errada (via banco de dados)
```

### Caso 3: Expandir para Novo Estado

```
Situação: Pint of Science chega pela primeira vez em Roraima

Ação:
1. Cadastrar "Boa Vista-RR"
2. Criar coordenador para Boa Vista
3. Associar coordenador à cidade
4. Aguardar inscrições
```

### Caso 4: Verificar Cidades Existentes

```
Situação: Antes de criar coordenador, verificar cidades disponíveis

Ação:
1. Acessar aba "🏙️ Cidades"
2. Visualizar lista completa
3. Anotar cidades para associar ao coordenador
4. Se cidade não existe, criar primeiro
```

## 🔄 Impacto em Outras Funcionalidades

### Participantes

- Participantes escolhem **cidade** no formulário de inscrição
- Dropdown mostra apenas cidades cadastradas
- Certificado exibe nome da cidade

### Coordenadores

- Coordenadores são **associados a cidades**
- Só veem participantes das cidades associadas
- Permissões baseadas em geografia

### Relatórios

- Estatísticas por cidade
- Distribuição geográfica
- Performance regional

## 📍 Formato Nome-Estado

### Por que "Nome-Estado"?

O sistema usa formato **"Nome-Estado"** como identificador único porque:

- ✅ Evita ambiguidade (ex: "São João" existe em vários estados)
- ✅ Facilita busca e filtros
- ✅ Melhora legibilidade
- ✅ Padrão reconhecido nacionalmente

### Exemplos

```
Correto:
- Brasília-DF
- São Paulo-SP
- Rio de Janeiro-RJ
- Belo Horizonte-MG

Incorreto:
- Brasília (falta estado)
- Brasília/DF (barra em vez de hífen)
- BRASILIA-DF (caps lock desnecessário)
```

## 📊 Estatísticas de Cidades

### Informações no Dashboard

```
🏙️ Cidades Cadastradas: 45
```

### Dados Úteis

- Total de cidades por região (N, NE, CO, SE, S)
- Total de cidades por estado
- Cidades com mais participantes
- Cidades sem coordenador

## ⚠️ Validações e Restrições

### Validações no Formulário

```
✅ Nome obrigatório
✅ Estado obrigatório
✅ Combinação nome+estado única
✅ Estado com 2 letras maiúsculas
```

### Mensagens de Erro Comuns

| Erro               | Causa                 | Solução                                   |
| ------------------ | --------------------- | ----------------------------------------- |
| "Cidade já existe" | Nome-Estado duplicado | Verifique lista, pode já estar cadastrada |
| "Estado inválido"  | Sigla não reconhecida | Use dropdown fornecido                    |
| "Nome obrigatório" | Campo vazio           | Preencha nome da cidade                   |

## 💡 Dicas e Boas Práticas

### Para Cadastro

1. **Use nomes oficiais** - Nome completo do município (ex: "Belo Horizonte" não "BH")
2. **Mantenha padrão** - Primeira letra maiúscula, demais minúsculas (ex: "São Paulo")
3. **Use acentuação correta** - "Goiânia" não "Goiania"
4. **Verifique antes de criar** - Confira se cidade não existe

### Para Organização

1. **Cadastre todas de uma vez** - No início da preparação do evento
2. **Agrupe por região** - Facilita gestão de coordenadores
3. **Documente mudanças** - Anote novas cidades a cada ano
4. **Revise periodicamente** - Identifique cidades inativas

### Para Manutenção

1. **Não delete cidades com histórico** - Preserve dados passados
2. **Corrija erros imediatamente** - Antes de associar coordenadores
3. **Mantenha consistência** - Use sempre mesmo padrão de nomenclatura

## 🔒 Segurança e Auditoria

### Registro de Ações

Ações em cidades são registradas:

- ✅ Criação de cidade
- ✅ (Edição não disponível na interface atual)
- ✅ (Deleção apenas via banco de dados)

Acesse os logs na aba **"📊 Auditoria"**.

### Quem Pode Fazer O Quê

| Ação           | Superadmin  | Coordenador |
| -------------- | ----------- | ----------- |
| Ver cidades    | ✅          | ✅          |
| Criar cidade   | ✅          | ❌          |
| Editar cidade  | ⚠️ (via BD) | ❌          |
| Deletar cidade | ⚠️ (via BD) | ❌          |

## 🗺️ Cidades por Região

### Distribuição Típica

```
Região Norte: 7 capitais + municípios do interior
Região Nordeste: 9 capitais + municípios do interior
Região Centro-Oeste: 4 capitais + municípios do interior
Região Sudeste: 4 capitais + municípios do interior
Região Sul: 3 capitais + municípios do interior

Total estimado: 40-50 cidades em eventos nacionais
```

## 🆘 Problemas Comuns

### Problema: "Cidade já cadastrada"

**Causa**: Tentando criar cidade que já existe

**Solução**:

1. Verifique tabela de cidades
2. Se existe, não precisa criar novamente
3. Use a cidade existente ao associar coordenador

---

### Problema: Cidade não Aparece no Dropdown

**Causa**: Participante ou coordenador não vê cidade esperada

**Solução**:

1. Verifique se cidade foi realmente criada (aba Cidades)
2. Se não existe, crie primeiro
3. Faça logout e login para atualizar cache

---

### Problema: Nome com Caractere Especial

**Causa**: Cidade tem hífen ou apóstrofo no nome

**Solução**:

- Use o nome oficial: "Feira de Santana" ✅
- Use acentuação: "São José dos Pinhais" ✅
- Mantenha hífens oficiais: "Passa-Quatro" ✅

---

### Problema: Coordenador Não Vê Cidade

**Causa**: Coordenador não está associado à cidade

**Solução**:

1. Vá em aba "👤 Coordenadores"
2. Seção "Associações Coordenador-Cidade"
3. Selecione coordenador
4. Associe cidade correta
5. Coordenador deve fazer logout/login

---

!!! success "Pronto!"

    Agora você sabe como gerenciar as cidades participantes do Pint of Science!
