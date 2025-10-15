# Validar Participantes

Guia completo para coordenadores validarem as inscrições de participantes no Sistema Pint of Science Brasil.

## 🎯 O que é Validação?

Validar um participante significa **confirmar oficialmente** que aquela pessoa participou efetivamente do evento. Somente após validação o certificado fica disponível para download.

### Importância da Validação

- ✅ Garante que apenas participantes reais recebam certificados
- ✅ Mantém a integridade e credibilidade dos certificados
- ✅ Permite controle de carga horária adequada
- ✅ Gera dados confiáveis para relatórios

!!! warning "Responsabilidade"

    Como coordenador, você é responsável por validar **apenas participações reais**. Nunca valide quem não esteve presente!

## 📋 Antes de Validar

### Checklist Pré-Validação

Antes de começar, tenha em mãos:

- ✔ **Lista de presença física** do evento
- ✔ **Relação de funções** de cada participante
- ✔ **Datas exatas** do evento em sua cidade
- ✔ **Informações sobre palestrantes** e voluntários confirmados

### Acesso à Página

1. Faça [login no sistema](acesso-sistema.md)
2. No menu lateral, clique em:

```
👨‍👨‍👦‍👦 Participantes
```

Você verá a página de gerenciamento de participantes.

## 🖥️ Interface de Validação

### Dashboard Principal

Ao acessar, você vê:

#### Métricas (Cards Superiores)

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 👥 Total    │ │ ✅ Validados │ │ ⏳ Pendentes  │ │ 📍 Cidades  │
│     150     │ │      120    │ │      30     │ │      3      │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

#### Filtros

Abaixo das métricas, você tem filtros para facilitar a busca:

| Filtro     | Opções                                                 |
| ---------- | ------------------------------------------------------ |
| **Cidade** | Todas as suas cidades autorizadas                      |
| **Status** | Todos / Validados / Pendentes                          |
| **Função** | Todas / Participante / Palestrante / Voluntário / etc. |
| **Busca**  | Nome ou e-mail parcial                                 |

#### Tabela de Participantes

Lista com colunas:

- ☑️ **Checkbox** - Para seleção em lote
- 👤 **Nome** - Nome completo do participante
- 📧 **E-mail** - E-mail de contato
- 📍 **Cidade** - Cidade de participação
- 👔 **Função** - Função exercida
- 📅 **Datas** - Datas de participação
- ✅ **Status** - Validado / Pendente
- 🔧 **Ações** - Botões de ação individual

## 🔍 Filtrando Participantes

### Por Status

Para ver apenas participantes não validados:

1. No filtro **"Status"**, selecione **"Pendentes"**
2. A lista será filtrada automaticamente
3. Você verá apenas quem aguarda validação

### Por Cidade

Se você gerencia múltiplas cidades:

1. No filtro **"Cidade"**, selecione a cidade desejada
2. Apenas participantes daquela cidade aparecerão

### Por Função

Para validar por categoria:

1. No filtro **"Função"**, escolha:
   - Palestrantes
   - Voluntários
   - Participantes do público
   - Coordenadores
   - Etc.

### Por Nome/E-mail

Para buscar alguém específico:

1. Digite nome ou e-mail parcial no campo de busca
2. A lista filtra em tempo real
3. Exemplo: digitando "maria" mostra "Maria Silva", "Maria Santos", etc.

!!! tip "Dica"

    Combine múltiplos filtros! Exemplo: Cidade "São Paulo" + Status "Pendentes" + Função "Palestrante"

## ✅ Validando Participantes

### Método 1: Validação Individual

Para validar um participante por vez:

1. **Localize o participante** na lista
2. **Verifique os dados**:
   - Nome está correto?
   - E-mail está correto?
   - Função adequada?
   - Datas corretas?
3. **Clique no botão** "✅ Validar" na coluna Ações
4. **Confirme** a ação no popup
5. **Aguarde** a confirmação (verde)

**Resultado:**

- Status muda para "✅ Validado"
- Certificado fica disponível para download
- Sistema gera hash de validação
- Ação é registrada em log de auditoria

### Método 2: Validação em Lote (Recomendado)

Para validar múltiplos participantes de uma vez:

1. **Selecione participantes**:

   - Marque checkbox de cada um
   - Ou use "Selecionar Todos" (se houver)

2. **Clique em "✅ Validar Selecionados"**

   - Botão aparece acima ou abaixo da tabela

3. **Revise a lista no popup**:

   - Confirme que todos estão corretos
   - Veja quantos serão validados

4. **Confirme a ação**

5. **Aguarde processamento**:
   - Barra de progresso pode aparecer
   - Todos são validados simultaneamente

**Vantagens:**

- ⚡ Muito mais rápido
- 🎯 Eficiente para muitos participantes
- 📊 Uma única entrada no log de auditoria

!!! success "Boa prática"

    Use validação em lote após verificar lista de presença. Filtre por cidade e data, confira todos, selecione e valide de uma vez!

## ❌ Invalidando Participantes

### Quando Invalidar?

Você pode precisar **remover a validação** se:

- Validou por engano
- Descobriu que pessoa não participou
- Dados precisam ser corrigidos
- Participante solicitou exclusão

### Como Invalidar:

1. Localize o participante **já validado**
2. Clique em **"❌ Invalidar"** na coluna Ações
3. **Confirme** a ação
4. **Justifique** (opcional, mas recomendado)

**Efeitos:**

- Status volta para "Pendente"
- Certificado para de estar disponível
- Hash de validação é removido
- Download não funciona mais
- Ação registrada em auditoria

!!! warning "Atenção"

    Se o participante já baixou o certificado, ele ficará inválido. Ao tentar validar online, aparecerá como "inválido".

## 📝 Verificando Dados Antes de Validar

### Dados Essenciais a Verificar:

#### 1. Nome Completo

- ✅ Está completo (não abreviado)?
- ✅ Ortografia correta?
- ✅ Sem erros de digitação?
- ✅ Capitalização adequada?

**Exemplos:**

- ✅ Correto: `Maria da Silva Santos`
- ❌ Errado: `MARIA SILVA` (tudo maiúsculo)
- ❌ Errado: `M. Silva` (abreviado)

#### 2. E-mail

- ✅ Formato válido (@dominio.com)?
- ✅ Sem erros de digitação?
- ✅ Participante tem acesso?

**Exemplos:**

- ✅ Correto: `maria.silva@gmail.com`
- ❌ Errado: `maria.silva@gmaiil.com` (erro)

#### 3. Função

- ✅ Função corresponde ao papel real?
- ✅ Não confundir Voluntário com Participante?
- ✅ Coordenadores estão marcados corretamente?

#### 4. Datas de Participação

- ✅ Apenas dias em que esteve presente?
- ✅ Todas as datas marcadas?
- ✅ Não há datas extras/erradas?

**Exemplo:**

- Evento: 19, 20 e 21 de maio
- Participante esteve: 20 e 21
- ✅ Devem estar marcados: 20 e 21
- ❌ Não marcar: 19 (não participou)

#### 5. Cidade

- ✅ Cidade correta?
- ✅ Não confundir cidades próximas?

## 🔧 Corrigindo Dados

Se encontrar erros:

### Opção 1: Corrigir Antes de Validar

1. Use o [editor de dados](gerenciar-participantes.md)
2. Corrija os campos necessários
3. Depois valide

### Opção 2: Não Validar Ainda

1. Deixe como "Pendente"
2. Entre em contato com participante
3. Solicite informações corretas
4. Atualize e valide depois

!!! tip "Recomendação"

    Sempre corrija erros **antes** de validar. Mudanças pós-validação são mais trabalhosas.

## 📊 Estratégias de Validação Eficiente

### Estratégia 1: Por Dia do Evento

```
1. Filtre por data específica (ex: 20/05)
2. Compare com lista de presença daquele dia
3. Valide todos em lote
4. Repita para cada dia
```

### Estratégia 2: Por Função

```
1. Primeiro valide palestrantes (lista menor, mais fácil)
2. Depois valide voluntários
3. Por último, participantes do público (lista maior)
```

### Estratégia 3: Por Status de Dados

```
1. Primeiro valide quem tem todos os dados corretos
2. Deixe para depois quem precisa correção
3. Corrija tudo junto
4. Valide o restante
```

### Estratégia 4: Sessões de Validação

```
Defina horários específicos para validar:
- Segunda: Palestrantes e coordenadores
- Quarta: Voluntários
- Sexta: Participantes do público
```

## ⏱️ Quanto Tempo Leva?

### Tempos Médios:

| Método                | Tempo por Participante | 100 Participantes |
| --------------------- | ---------------------- | ----------------- |
| **Individual**        | ~20 segundos           | ~33 minutos       |
| **Lote (10 por vez)** | ~5 segundos            | ~8 minutos        |
| **Lote (50 por vez)** | ~2 segundos            | ~3 minutos        |

!!! success "Dica de Produtividade"

    Use validação em lote para economizar tempo! Com 100 participantes, você economiza 30 minutos!

## 📧 Notificações Automáticas

### E-mails Após Validação

Se o sistema estiver configurado, participantes podem receber e-mail automático quando validados:

**Conteúdo típico:**

```
Assunto: Seu certificado Pint of Science 2025 está disponível!

Olá [Nome],

Sua participação no Pint of Science 2025 foi validada!

Seu certificado já está disponível para download.

Acesse: [link do sistema]
Aba: Baixar Certificado
Use o e-mail: [email]

Atenciosamente,
Equipe Pint of Science
```

!!! info "Configuração"

    O envio automático depende de configuração. Se não estiver ativo, oriente participantes a baixarem manualmente.

## 📋 Checklist de Validação

Use este checklist após cada sessão de validação:

- ✔ Todos os dados verificados?
- ✔ Funções estão corretas?
- ✔ Datas conferidas com lista de presença?
- ✔ Erros de digitação corrigidos?
- ✔ Participantes reais (não validei ninguém falso)?
- ✔ Coordenadores marcados adequadamente?
- ✔ Carga horária será calculada corretamente?
- ✔ Documentei casos especiais (se houver)?

## 🆘 Problemas Comuns

### Erro ao validar

**Solução:**

1. Recarregue a página (F5)
2. Tente validar novamente
3. Se persistir, tente individual em vez de lote
4. Verifique sua conexão

### Validação não aparece imediatamente

**Solução:**

- Aguarde 2-3 segundos
- Recarregue a página
- Status deve atualizar

### Participante reclama que certificado não está disponível

**Verificações:**

1. Status está como "Validado"?
2. Validação foi há quanto tempo? (pode levar minutos)
3. Participante está usando e-mail correto?

## 📚 Próximos Passos

Após validar participantes:

- [Gerenciar Participantes](gerenciar-participantes.md) - Editar dados se necessário
- [Enviar Certificados](enviar-certificados.md) - Enviar por e-mail (opcional)
- [Relatórios](relatorios.md) - Ver estatísticas de validação

---

!!! success "Parabéns!"

    Você agora sabe como validar participantes eficientemente. Lembre-se: qualidade é mais importante que velocidade!
