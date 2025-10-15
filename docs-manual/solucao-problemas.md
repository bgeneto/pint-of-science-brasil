# Solução de Problemas

Guia de resolução para os problemas mais comuns no Sistema Pint of Science Brasil.

## 🔧 Problemas de Acesso

### Não consigo acessar o sistema

**Sintomas:**

- Página não carrega
- Erro de conexão
- Tela em branco

**Soluções:**

1. **Verifique sua conexão com internet**

   ```
   - Tente abrir outro site (google.com)
   - Reinicie seu roteador se necessário
   - Use conexão móvel alternativa
   ```

2. **Limpe cache do navegador**

   - Chrome/Edge: `Ctrl + Shift + Delete`
   - Firefox: `Ctrl + Shift + Delete`
   - Safari: `Cmd + Option + E`

3. **Tente outro navegador**

   - Chrome (recomendado)
   - Firefox
   - Edge
   - Safari

4. **Desative extensões temporariamente**
   - AdBlock pode bloquear recursos
   - VPNs podem causar problemas
   - Tente modo anônimo/privado

### Página carrega mas está quebrada/desconfigurada

**Solução:**

- Force recarga: `Ctrl + Shift + R` (Windows/Linux) ou `Cmd + Shift + R` (Mac)
- Limpe cache específico do site
- Verifique se JavaScript está ativado

---

## 👤 Problemas de Login (Coordenadores)

### Esqueci minha senha

**Solução:**

- Entre em contato com o administrador do sistema
- Não há sistema de recuperação automática de senha
- Informe seu e-mail de cadastro

### Login não funciona / credenciais rejeitadas

**Possíveis causas e soluções:**

| Causa              | Solução                                 |
| ------------------ | --------------------------------------- |
| Senha incorreta    | Verifique Caps Lock, tente novamente    |
| E-mail incorreto   | Confirme e-mail exato com administrador |
| Conta desativada   | Entre em contato com administrador      |
| Problema de sessão | Limpe cookies e tente novamente         |

**Como limpar cookies:**

1. Chrome: Configurações → Privacidade → Limpar dados de navegação → Cookies
2. Firefox: Preferências → Privacidade → Limpar dados → Cookies
3. Edge: Configurações → Privacidade → Escolher o que limpar → Cookies

### Sessão expira muito rápido

**Soluções:**

- Sessões duram 30 dias se você não fechar o navegador
- Não use modo anônimo/privado (não salva cookies)
- Verifique se cookies estão habilitados
- Não bloqueie cookies de terceiros

### Não consigo fazer logout

**Solução:**

- Feche o navegador completamente
- Limpe cookies manualmente
- Abra novamente e faça login do zero

---

## 📝 Problemas na Inscrição

### Formulário não envia / erro ao enviar

**Soluções:**

1. **Verifique campos obrigatórios**

   - Todos os campos com asterisco (\*) devem estar preenchidos
   - Mensagens de erro aparecem em vermelho

2. **Verifique formato do e-mail**

   - Deve conter @ e domínio
   - Exemplo correto: `usuario@dominio.com`
   - Sem espaços antes/depois

3. **Selecione ao menos uma data**

   - Marque checkboxes das datas de participação
   - Pelo menos uma data é obrigatória

4. **Conexão com internet**
   - Verifique se não caiu durante o envio
   - Tente novamente

### "E-mail já cadastrado"

**Causa:**
Você já se inscreveu com este e-mail antes.

**Soluções:**

- Use outro e-mail
- Entre em contato com coordenador para verificar seu cadastro existente
- Se foi erro, peça ao coordenador para remover e reinscrever

### Cidade/Função não aparece na lista

**Solução:**

- Recarregue a página (F5)
- Se persistir, entre em contato com administrador
- Pode ser que sua cidade ainda não foi cadastrada

### Dados não aceitam caracteres especiais

**Se o sistema rejeitar:**

- Tente sem acentos primeiro (ex: Jose em vez de José)
- Entre em contato com coordenador para corrigir depois
- Reporte o problema ao suporte técnico

---

## 📥 Problemas no Download de Certificado

### "Nenhum certificado encontrado"

**Possíveis causas:**

1. **Ainda não foi validado**

   - Aguarde coordenador validar (1-7 dias)
   - Tente novamente amanhã

2. **E-mail incorreto**

   - Digite EXATAMENTE como inscreveu
   - Tente maiúsculas/minúsculas diferentes
   - Exemplo: `Maria@email.com` ≠ `maria@email.com`

3. **Não se inscreveu**
   - Verifique se completou a inscrição
   - Faça a inscrição se ainda não fez

**Checklist de verificação:**

- ✔ Estou usando o e-mail correto?
- ✔ Passou mais de 24h desde a inscrição?
- ✔ Confirmei inscrição com coordenador?
- ✔ Tentei variações do e-mail (maiúsculas)?

### PDF não baixa / download falha

**Soluções:**

1. **Tente novamente**

   - Clique no botão de download novamente
   - Aguarde completamente o download

2. **Verifique espaço em disco**

   - Certifique-se que tem espaço livre
   - Certificados têm ~500 KB

3. **Desative bloqueadores**

   - AdBlock pode bloquear download
   - Desative temporariamente

4. **Tente outro navegador**
   - Chrome geralmente funciona melhor

### PDF baixa mas não abre

**Possíveis causas e soluções:**

| Problema                | Solução                               |
| ----------------------- | ------------------------------------- |
| Não tem leitor de PDF   | Instale Adobe Reader ou use navegador |
| Download incompleto     | Baixe novamente                       |
| Arquivo corrompido      | Baixe novamente                       |
| Versão antiga do leitor | Atualize Adobe Reader                 |

**Como abrir PDF:**

- Windows: Clique direito → Abrir com → Adobe Reader / Edge
- Mac: Duplo clique (abre no Preview)
- Linux: Evince, Okular, ou navegador
- Mobile: Adobe Acrobat Reader app

---

## ✅ Problemas na Validação

### Link de validação não funciona

**Soluções:**

1. **Copie o código manualmente**

   - Abra o PDF
   - Copie o código no rodapé
   - Vá em "Validar Certificado" no menu
   - Cole o código

2. **Verifique conexão**

   - Link precisa de internet
   - Tente novamente

3. **Tente em outro dispositivo**
   - Link pode não funcionar em alguns apps de PDF mobile
   - Abra no computador

### "Certificado inválido"

**Possíveis causas:**

1. **Código copiado incorretamente**

   - Copie novamente, completo
   - Não deixe espaços extras

2. **Certificado foi revogado**

   - Coordenador invalidou posteriormente
   - Entre em contato com coordenador

3. **PDF foi editado**
   - Se modificou o PDF, hash fica inválido
   - Baixe novamente o original

---

## 🔒 Problemas de Coordenadores

### Não vejo participantes da minha cidade

**Possíveis causas:**

1. **Nenhuma inscrição ainda**

   - Aguarde participantes se inscreverem

2. **Filtro ativo**

   - Verifique filtros na página
   - Clique em "Limpar Filtros"

3. **Permissões incorretas**
   - Entre em contato com administrador
   - Verifique suas cidades autorizadas

### Erro ao validar participante

**Soluções:**

1. **Recarregue a página**

   - F5 ou Ctrl+R
   - Tente validar novamente

2. **Valide um por vez**

   - Se lote não funcionar, tente individual

3. **Verifique sessão**
   - Pode ter expirado
   - Faça logout e login novamente

### Não consigo editar dados

**Verificações:**

1. **Você tem permissão?**

   - Apenas coordenadores autorizados podem editar
   - Verifique com administrador

2. **Campo é editável?**

   - Alguns campos são bloqueados
   - Exemplo: IDs, hashes, timestamps

3. **Erro de validação**
   - Dados devem passar validação
   - Exemplo: e-mail deve ter formato válido

---

## 📧 Problemas com E-mail

### Não recebi e-mail do sistema

**Verificações:**

1. **Pasta de spam**

   - Verifique lixo eletrônico
   - Verifique promoções (Gmail)
   - Adicione `@brevo.com` aos contatos seguros

2. **E-mail correto?**

   - Confirme que usou e-mail certo na inscrição
   - Tente verificar com coordenador

3. **Sistema pode não estar configurado**
   - Nem sempre há envio automático
   - Baixe manualmente pela plataforma

### E-mail chegou mas sem anexo

**Solução:**

- Sempre há opção de baixar manualmente
- Vá em "Baixar Certificado" no sistema
- Use seu e-mail para buscar

---

## 💻 Problemas Técnicos

### Sistema está lento

**Causas comuns:**

- Muitos usuários simultâneos (período de pico)
- Conexão lenta
- Computador sobrecarregado

**Soluções:**

- Aguarde alguns minutos
- Feche outras abas/programas
- Tente em horário alternativo

### Botões não respondem

**Soluções:**

1. **Aguarde**

   - Alguns processos demoram
   - Não clique múltiplas vezes

2. **Recarregue página**

   - F5 ou Ctrl+R

3. **Desative extensões**
   - Extensões podem bloquear JavaScript
   - Tente modo anônimo

### Tela fica em branco após ação

**Soluções:**

- Aguarde 10-15 segundos
- Recarregue a página
- Volte e tente novamente
- Verifique console do navegador (F12)

### Erros de "Session State"

**Solução:**

- Feche o navegador completamente
- Limpe cache e cookies
- Abra novamente
- Faça login do zero

---

## 📱 Problemas Mobile

### Layout quebrado no celular

**Soluções:**

- Rotacione o dispositivo (paisagem)
- Atualize a página
- Use navegador atualizado
- Tente Chrome mobile

### Formulário difícil de preencher

**Dicas:**

- Aumente zoom (pinça)
- Desative autocorretor para e-mail
- Use teclado físico se disponível
- Preencha em computador se possível

### Download não funciona em mobile

**Soluções:**

- Verifique permissões de download
- Use Chrome ou Safari
- Verifique espaço de armazenamento
- Tente compartilhar para nuvem

---

## 🆘 Quando Entrar em Contato com Suporte

Entre em contato se:

- ❌ Problema persiste após tentar todas as soluções
- ❌ Erro técnico que você não entende
- ❌ Dados incorretos que você não pode corrigir
- ❌ Suspeita de bug no sistema
- ❌ Precisa de ajuda com permissões/acesso

**Como reportar problemas:**

1. **Descreva o problema claramente**

   - O que você tentou fazer?
   - O que aconteceu?
   - Qual mensagem de erro apareceu?

2. **Forneça informações do sistema**

   - Navegador e versão
   - Sistema operacional
   - Se é mobile ou desktop

3. **Prints de tela**

   - Tire screenshots do problema
   - Inclua mensagens de erro completas

4. **Passos para reproduzir**
   - Liste exatamente o que fazer
   - Para que suporte possa testar

---

## 📞 Canais de Suporte

Veja a página de [Suporte](suporte.md) para informações de contato.

---

!!! tip "Dica Final"

    90% dos problemas são resolvidos com: recarga de página, limpeza de cache, ou outro navegador. Tente isso primeiro!
