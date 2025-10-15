# Gestão de Funções

Guia completo para cadastrar e gerenciar funções dos participantes do Pint of Science Brasil.

## 🎯 O que são Funções?

Funções representam os **papéis desempenhados** pelos participantes no evento. Exemplos:

- 👨‍🏫 Palestrante
- 🎤 Moderador(a)
- 📋 Organizador(a)
- 🎨 Artista
- 🤝 Voluntário(a)
- 📸 Fotógrafo(a)
- 🎥 Cinegrafista

!!! info "Importância"

    As funções são fundamentais para:
    - Identificar o tipo de participação no certificado
    - Calcular carga horária diferenciada (algumas funções = evento completo)
    - Gerar estatísticas por tipo de participação
    - Filtrar e organizar participantes

## 🚀 Acessando a Gestão

1. Faça login como superadmin
2. Acesse **⚙️ Administração** no menu lateral
3. Clique na aba **🎭 Funções**

Você verá duas seções:

- **Criar Nova Função** (formulário)
- **Funções Cadastradas** (tabela de visualização)

## ➕ Criando Nova Função

### Passo a Passo

1. Digite o **Nome da Função** no campo de texto
2. Clique em **"🎭 Criar Função"**

### Exemplo de Criação

```
Nome da Função: Palestrante

Resultado: Função "Palestrante" criada com sucesso!
```

### Funções Comuns

Lista típica de funções em eventos Pint of Science:

```
- Palestrante
- Moderador(a)
- Organizador(a)
- Coordenador(a) Local
- Voluntário(a)
- Artista
- Músico(a)
- Fotógrafo(a)
- Cinegrafista
- Assessoria de Imprensa
- Designer
- Tradutor(a)
```

### Validações Automáticas

O sistema valida:

- ✅ Nome é obrigatório
- ✅ Nome deve ser único (não aceita duplicatas)
- ✅ Espaços extras são removidos automaticamente

## 📊 Visualizando Funções

### Tabela de Funções Cadastradas

A tabela mostra todas as funções em ordem alfabética:

| Coluna           | Descrição                             |
| ---------------- | ------------------------------------- |
| **ID**           | Identificador único do banco de dados |
| **Nome**         | Nome da função                        |
| **Data Criação** | Quando foi criada (DD/MM/YYYY HH:MM)  |

### Exemplo de Dados

```
ID: 5
Nome: Palestrante
Data Criação: 10/01/2024 15:30
```

### Ordenação

- Funções são exibidas em **ordem alfabética** por nome
- Facilita localização visual

## 🔄 Impacto em Outras Funcionalidades

### Formulário de Inscrição

- Participantes escolhem **função** no dropdown
- Apenas funções cadastradas aparecem
- Função é exibida no certificado

### Carga Horária

Funções podem ter tratamento diferenciado de carga horária:

```python
# Exemplo de configuração (certificate_config.json)
"funcoes_evento_completo": [1, 2, 3]
```

- IDs listados = participação em evento completo
- Recebem carga horária máxima independente dos dias

### Certificados

A função aparece no certificado:

```
Certificamos que [Nome] participou do evento
Pint of Science Brasil 2025 na função de Palestrante...
```

## 🎯 Casos de Uso Comuns

### Caso 1: Preparar Funções para Novo Evento

```
Situação: Cadastrar funções antes de abrir inscrições

Ação:
1. Listar todas as funções necessárias
2. Criar uma por uma:
   - Palestrante
   - Moderador(a)
   - Organizador(a)
   - Voluntário(a)
3. Testar dropdown no formulário de inscrição
```

### Caso 2: Adicionar Nova Função

```
Situação: Evento 2026 terá categoria nova "Podcaster"

Ação:
1. Acessar aba "🎭 Funções"
2. Digite: Podcaster
3. Criar função
4. Atualizar documentação interna sobre funções
```

### Caso 3: Corrigir Nome com Erro

```
Situação: Função cadastrada como "Palestrnte" (erro de digitação)

Problema: Nome errado já está em uso
Solução:
1. Criar função correta: "Palestrante"
2. Reatribuir participantes da função errada para correta
3. Deletar função errada (via banco de dados)
```

### Caso 4: Padronizar Nomenclatura

```
Situação: Algumas funções com/sem gênero

Inconsistente:
- Palestrante
- Organizador
- Moderadora

Padronizado:
- Palestrante
- Organizador(a)
- Moderador(a)

Ação: Criar funções padronizadas, migrar dados, deletar antigas
```

## 🎭 Nomenclatura de Funções

### Boas Práticas

1. **Use linguagem inclusiva**:

   - "Organizador(a)" em vez de "Organizador"
   - "Moderador(a)" em vez de "Moderadora"

2. **Seja específico**:

   - "Fotógrafo(a)" em vez de "Mídia"
   - "Tradutor(a) de Libras" em vez de "Tradutor(a)"

3. **Mantenha consistência**:

   - Se usa (a), use em todas: Voluntário(a), Palestrante
   - Se usa cargo, use em todas: "Coordenador(a) Local"

4. **Evite ambiguidade**:
   - "Voluntário(a) Geral" vs "Voluntário(a) de Credenciamento"
   - "Organizador(a) Local" vs "Organizador(a) Nacional"

### Exemplos de Nomenclatura Clara

```
✅ Bom:
- Palestrante
- Moderador(a) de Mesa
- Organizador(a) Local
- Voluntário(a) de Apoio
- Assessor(a) de Comunicação

❌ Evitar:
- Palestra (é ação, não função)
- Organização (é área, não função)
- Ajudante (muito genérico)
- Staff (em inglês)
```

## ⚙️ Configuração de Carga Horária

### Funções com Evento Completo

Algumas funções recebem carga horária do evento completo, independente dos dias participados:

```json
// Arquivo: static/certificate_config.json
"2025": {
  "carga_horaria": {
    "funcoes_evento_completo": [1, 2, 3]
  }
}
```

**IDs de exemplo**:

- 1 = Organizador(a)
- 2 = Coordenador(a) Local
- 3 = Moderador(a)

### Como Descobrir o ID de uma Função

1. Acesse aba "🎭 Funções"
2. Veja coluna **"ID"** na tabela
3. Anote o ID da função desejada
4. Use no `certificate_config.json`

### Exemplo Prático

```
Função: Organizador(a)
ID na tabela: 1

Configuração:
"funcoes_evento_completo": [1]

Resultado: Organizadores recebem 40h (evento completo)
           mesmo que tenham participado de apenas 1 dia
```

## 🗑️ Deletando Funções

!!! warning "Funcionalidade Limitada"

    A interface atual não permite deleção direta pela aba. Isso previne deleção acidental de funções em uso.

### Regras de Proteção

O sistema protege contra deleção se:

❌ **Há participantes com essa função**

- Dados históricos devem ser preservados
- Certificados já foram gerados

✅ **Função não está em uso**

- Pode ser deletada com segurança
- Geralmente é erro de cadastro ou função descontinuada

### Como Deletar (se necessário)

Para deletar função não utilizada:

1. Verificar que não há participantes com essa função
2. Usar acesso direto ao banco de dados
3. Ou criar script de migração para reatribuir participantes

## 📊 Estatísticas de Funções

### Informações Úteis

- Total de funções cadastradas
- Funções mais usadas
- Funções sem participantes (candidatas a remoção)
- Distribuição de participantes por função

### Exemplo de Distribuição

```
Palestrante: 45 participantes (30%)
Voluntário(a): 60 participantes (40%)
Organizador(a): 25 participantes (17%)
Moderador(a): 20 participantes (13%)
```

## ⚠️ Validações e Restrições

### Validações no Formulário

```
✅ Nome obrigatório
✅ Nome único (sem duplicatas)
✅ Remove espaços extras
✅ Não permite nome vazio
```

### Mensagens de Erro Comuns

| Erro                   | Causa             | Solução                          |
| ---------------------- | ----------------- | -------------------------------- |
| "Função já cadastrada" | Nome duplicado    | Verifique lista, pode já existir |
| "Nome obrigatório"     | Campo vazio       | Digite nome da função            |
| "Erro ao criar função" | Problema no banco | Tente novamente ou veja logs     |

## 💡 Dicas e Boas Práticas

### Para Cadastro

1. **Planeje funções antes** - Liste todas necessárias antes de criar evento
2. **Use nomes descritivos** - "Voluntário(a)" é melhor que "Apoio"
3. **Mantenha padrão** - Se usa (a) para gênero, use em todas
4. **Evite siglas** - "Fotógrafo(a)" não "Foto"
5. **Seja específico quando necessário** - "Tradutor(a) de Libras" se houver outros tradutores

### Para Organização

1. **Crie funções no início** - Antes de abrir inscrições
2. **Documente IDs importantes** - Anote IDs das funções que têm carga horária especial
3. **Revise anualmente** - Adapte para realidade de cada evento
4. **Remova descontinuadas** - Se alguma função não é mais usada

### Para Manutenção

1. **Não delete funções com histórico** - Preserve dados de eventos passados
2. **Padronize gradualmente** - Migre para nomenclatura consistente
3. **Comunique mudanças** - Informe coordenadores sobre novas funções

## 🔒 Segurança e Auditoria

### Registro de Ações

Ações em funções são registradas:

- ✅ Criação de função
- ✅ (Edição não disponível na interface atual)
- ✅ (Deleção apenas via banco de dados)

Acesse os logs na aba **"📊 Auditoria"**.

### Quem Pode Fazer O Quê

| Ação           | Superadmin  | Coordenador |
| -------------- | ----------- | ----------- |
| Ver funções    | ✅          | ✅          |
| Criar função   | ✅          | ❌          |
| Editar função  | ⚠️ (via BD) | ❌          |
| Deletar função | ⚠️ (via BD) | ❌          |

## 🆘 Problemas Comuns

### Problema: "Função já cadastrada"

**Causa**: Tentando criar função que já existe

**Solução**:

1. Verifique tabela de funções
2. Se existe, não precisa criar novamente
3. Use a função existente

---

### Problema: Função não Aparece no Dropdown

**Causa**: Cache do navegador ou função não criada

**Solução**:

1. Verifique se função foi realmente criada (aba Funções)
2. Faça logout e login
3. Limpe cache do navegador (Ctrl+Shift+Del)
4. Se não existe, crie primeiro

---

### Problema: Preciso Alterar Nome da Função

**Causa**: Erro de digitação ou mudança de nomenclatura

**Solução Temporária**:

1. Criar função com nome correto
2. Orientar uso da função correta daqui em diante
3. (Ideal: migrar participantes antigos via banco de dados)

---

### Problema: Carga Horária Errada para Função

**Causa**: Função não está configurada em `funcoes_evento_completo`

**Solução**:

1. Identifique ID da função (aba Funções)
2. Edite `static/certificate_config.json`
3. Adicione ID em `funcoes_evento_completo`
4. Exemplo:

```json
"funcoes_evento_completo": [1, 2, 3, 5]
```

---

!!! success "Pronto!"

    Agora você sabe como gerenciar as funções dos participantes do Pint of Science!
