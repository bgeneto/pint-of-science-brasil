# Implementação: Permissões de Coordenadores por Cidade

## 📋 Resumo

Implementada funcionalidade completa para permitir que coordenadores (não apenas superadmins) gerenciem participantes de suas cidades associadas.

## ✅ O que foi implementado

### 1. **Carregamento de Cidades no Login** (`app/auth.py`)
- ✅ Modificado `handle_login_result()` para carregar cidades associadas ao coordenador
- ✅ Cidades armazenadas em `st.session_state['allowed_cities']` como lista de IDs
- ✅ Superadmins não têm restrição (lista vazia = todas as cidades)
- ✅ Coordenadores sem cidades associadas recebem lista vazia e aviso

### 2. **Interface de Associação** (`pages/2_⚙️_Administração.py`)
- ✅ Nova função `gerenciar_associacoes_coordenador_cidade()`
- ✅ Interface com `st.multiselect` para associar coordenadores a múltiplas cidades
- ✅ Expanders por coordenador mostrando cidades atuais e permitindo edição
- ✅ Botão de salvar individual por coordenador
- ✅ Integrada na aba "Coordenadores" da página de administração

### 3. **Filtro Automático por Cidade** (`pages/1_👨‍👨‍👦‍👦_Participantes.py`)
- ✅ Modificado `carregar_dados_validacao()` para filtrar participantes por cidade
- ✅ Superadmin vê todos os participantes (comportamento anterior mantido)
- ✅ Coordenador vê apenas participantes de suas cidades associadas
- ✅ Coordenador sem cidades vê aviso e nenhum participante
- ✅ Modificado `mostrar_filtros()` para:
  - Superadmin: filtro de cidade habilitado (pode filtrar entre todas)
  - Coordenador: filtro desabilitado, mostra info das cidades associadas

### 4. **Permissão de Edição para Coordenadores**
- ✅ Criada variável `can_edit = is_superadmin or bool(allowed_cities)`
- ✅ Modificado `tabela_validacao_participantes()`:
  - Campos editáveis para coordenadores (exceto "Cidade" - só superadmin)
  - Nome, Email, Função, Título, Datas editáveis por coordenadores
  - Mensagem informativa diferenciada para coordenadores
- ✅ Modificado `processar_validacao()`:
  - Detecção de mudanças habilitada para coordenadores
  - Botão "Salvar Edições" visível para coordenadores
  - Regeneração de hash de validação funciona para todos

## 🎯 Regras de Negócio

### Superadmin
- ✅ Vê todos os participantes de todas as cidades
- ✅ Pode editar todos os campos (incluindo trocar cidade)
- ✅ Pode validar/desvalidar qualquer participante
- ✅ Filtro de cidade totalmente funcional

### Coordenador Regular (com cidades associadas)
- ✅ Vê apenas participantes de suas cidades
- ✅ Pode editar campos (exceto cidade)
- ✅ Pode validar/desvalidar participantes de suas cidades
- ✅ Filtro de cidade desabilitado (já filtrado automaticamente)
- ✅ Vê info das cidades no lugar do filtro

### Coordenador Regular (sem cidades associadas)
- ✅ Não vê nenhum participante
- ✅ Recebe aviso para contatar administrador
- ✅ Não pode editar nem validar

## 📊 Tabelas Envolvidas

### `coordenador_cidade_link` (N:N)
```sql
coordenador_id INTEGER FK → coordenadores.id
cidade_id INTEGER FK → cidades.id
PRIMARY KEY (coordenador_id, cidade_id)
```

### Session State
```python
st.session_state['allowed_cities']  # Lista de IDs de cidades [1, 5, 8]
st.session_state['is_superadmin']    # Boolean
```

## 🧪 Como Testar

### 1. Executar Script de Teste
```bash
python test_coordenador_cidades.py
```

Verifica:
- ✅ Associações existentes
- ✅ Coordenadores sem cidades
- ✅ Fluxo de login simulado

### 2. Teste Manual no Streamlit

#### Como Superadmin:
1. `streamlit run 🏠_Home.py`
2. Login com credenciais de superadmin
3. Ir para "Administração" → aba "Coordenadores"
4. Rolar até "🗺️ Associar Coordenadores a Cidades"
5. Expandir coordenador
6. Selecionar cidades no multiselect
7. Clicar "💾 Salvar"

#### Como Coordenador Regular:
1. Fazer login com coordenador regular
2. Ir para "Participantes"
3. Verificar:
   - ✅ Vê apenas participantes das cidades associadas
   - ✅ Info das cidades mostrada em vez do filtro
   - ✅ Pode editar campos (exceto cidade)
   - ✅ Pode validar participantes

#### Como Coordenador Sem Cidades:
1. Fazer login com coordenador sem associações
2. Ir para "Participantes"
3. Verificar:
   - ✅ Aviso: "Você não está associado a nenhuma cidade"
   - ✅ Nenhum participante exibido

## 📝 Arquivos Modificados

1. **`app/auth.py`** (linhas ~210-225)
   - Busca cidades na tabela `coordenador_cidade_link`
   - Popula `allowed_cities` no login

2. **`pages/2_⚙️_Administração.py`** (linhas ~465-560)
   - Nova função `gerenciar_associacoes_coordenador_cidade()`
   - Chamada adicionada na aba de coordenadores

3. **`pages/1_👨‍👨‍👦‍👦_Participantes.py`**
   - `carregar_dados_validacao()`: filtro por cidade (linhas ~130-180)
   - `tabela_validacao_participantes()`: permissões de edição (linhas ~260-365)
   - `processar_validacao()`: detecção de mudanças (linhas ~400-640)
   - `mostrar_filtros()`: filtro adaptativo (linhas ~760-820)

4. **`test_coordenador_cidades.py`** (novo arquivo)
   - Script de teste automatizado

## 🔒 Segurança

- ✅ Coordenadores só veem dados de suas cidades (filtro no backend)
- ✅ Coordenadores não podem trocar cidade de participantes
- ✅ Superadmins continuam com acesso total
- ✅ Session state validado em cada carregamento de dados
- ✅ Filtro aplicado no nível de query SQL (não apenas UI)

## 🚀 Próximos Passos

1. ✅ Executar `streamlit run 🏠_Home.py`
2. ✅ Login como superadmin
3. ✅ Associar coordenadores existentes às suas cidades
4. ✅ Testar login como coordenador regular
5. ✅ Verificar que tudo funciona conforme esperado

## ❓ Troubleshooting

### Coordenador não vê participantes
- Verificar se tem cidades associadas na página de Administração
- Verificar se existem participantes nessas cidades
- Checar logs: `allowed_cities` deve ter IDs

### Coordenador não pode editar
- Verificar `can_edit = is_superadmin or bool(allowed_cities)`
- Se `allowed_cities` estiver vazia, não pode editar

### Associações não salvam
- Verificar permissões de escrita no banco
- Checar logs de erro no console
- Verificar se tabela `coordenador_cidade_link` existe

## 📚 Referências

- `CLAUDE.md`: Requisitos originais
- `.github/copilot-instructions.md`: Guia de arquitetura
- `app/models.py`: Modelo `CoordenadorCidadeLink`
