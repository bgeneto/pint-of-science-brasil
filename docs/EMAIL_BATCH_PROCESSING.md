# Email Batch Processing - Implementação

## 📧 Visão Geral

O sistema agora implementa **envio de emails em lote (batch processing)** para otimizar a comunicação com participantes validados, especialmente quando lidamos com dezenas ou centenas de destinatários simultaneamente.

## 🚀 Como Funciona

### Fluxo de Validação com Batch Email

1. **Coordenador seleciona participantes** na interface (via checkboxes)
2. **Clica em "Validar Selecionados"**
3. **Sistema processa validação** no banco de dados
4. **Coleta informações** de todos os participantes validados
5. **Envia emails em lote** (batch processing)

### Implementação Técnica

#### Arquivo: `app/services.py`

##### Novo Método: `enviar_emails_certificado_liberado_batch()`

```python
def enviar_emails_certificado_liberado_batch(
    self, destinatarios: List[Dict[str, str]]
) -> Tuple[int, int]:
    """
    Envia e-mails em lote usando processamento otimizado.

    Args:
        destinatarios: Lista de dicionários com 'nome', 'email', 'link_download'

    Returns:
        Tupla com (sucessos, falhas)
    """
```

**Características:**

- **Batch Size**: 100 emails por lote
- **Processamento sequencial otimizado**: Evita sobrecarga de memória
- **Logging detalhado**: Rastreia sucesso/falha por batch
- **Graceful degradation**: Falhas individuais não impedem o resto do batch
- **Timeout configurado**: 10 segundos por requisição

#### Modificação: `validar_participantes()`

A função foi refatorada para:

1. **Coletar emails durante validação** (dentro da transação do DB)
2. **Enviar emails após commit** (fora da sessão do DB)
3. **Reportar estatísticas** completas (validações + emails)

```python
# Coletar dados para envio de email em batch (apenas se validado)
if novo_status:
    emails_para_enviar.append({
        "nome": nome,
        "email": email,
        "link_download": link_download
    })

# Enviar emails em batch (fora da sessão do banco)
if emails_para_enviar and servico_email.is_configured():
    emails_enviados, emails_falhados = servico_email.enviar_emails_certificado_liberado_batch(
        emails_para_enviar
    )
```

## 📊 Vantagens da Implementação

### 1. **Performance**
- ✅ Evita N requisições individuais à API Brevo
- ✅ Reduz tempo total de processamento
- ✅ Não bloqueia sessão do banco de dados durante envio

### 2. **Confiabilidade**
- ✅ Transação do DB completa antes de enviar emails
- ✅ Falhas de email não revertem validações no DB
- ✅ Retry implícito por batch (se um batch falha, outros continuam)

### 3. **Observabilidade**
- ✅ Logs detalhados por batch
- ✅ Contadores de sucesso/falha
- ✅ Mensagens informativas para o usuário

### 4. **Escalabilidade**
- ✅ Suporta de 1 a centenas de destinatários
- ✅ Batch size configurável (atualmente 100)
- ✅ Timeout por requisição evita travamentos

## 🔧 Configuração

### Variáveis de Ambiente (`.env`)

```bash
# Brevo API Configuration
BREVO_API_KEY=your_api_key_here
BREVO_SENDER_EMAIL=noreply@pintofscience.com.br
BREVO_SENDER_NAME="Pint of Science Brasil"
BASE_URL=https://your-domain.com
```

### Limites da API Brevo

- **Rate Limit**: 300 emails/minuto (plano gratuito)
- **Daily Limit**: 300 emails/dia (plano gratuito)
- **Recomendado**: Plano pago para eventos com muitos participantes

## 📈 Exemplos de Uso

### Cenário 1: Validar 5 participantes
```
📧 Processando batch 1: 5 emails
✅ Batch 1 concluído: 5 sucessos até agora
🎉 Envio em lote concluído: 5 sucessos, 0 falhas
```

### Cenário 2: Validar 250 participantes
```
📧 Processando batch 1: 100 emails
✅ Batch 1 concluído: 100 sucessos até agora
📧 Processando batch 2: 100 emails
✅ Batch 2 concluído: 200 sucessos até agora
📧 Processando batch 3: 50 emails
✅ Batch 3 concluído: 250 sucessos até agora
🎉 Envio em lote concluído: 250 sucessos, 0 falhas
```

### Cenário 3: Com falhas parciais
```
📧 Processando batch 1: 100 emails
⚠️ Falha ao enviar para invalid@email: 400
✅ Batch 1 concluído: 99 sucessos até agora
🎉 Envio em lote concluído: 99 sucessos, 1 falhas
```

## 🎯 Mensagens para o Usuário

Após validação, o usuário vê uma mensagem consolidada:

```
🎉 Participantes validados com sucesso!
Processados 250 participantes. 250 atualizados com sucesso. 245 emails enviados. 5 emails falharam.
```

## 🐛 Troubleshooting

### Email não configurado
```python
⚠️ E-mails não enviados: serviço não configurado
```
**Solução**: Verificar variáveis BREVO_API_KEY e BREVO_SENDER_EMAIL no `.env`

### Rate limit excedido
```python
❌ Falha ao enviar para user@email: 429 - Rate limit exceeded
```
**Solução**:
- Aguardar 1 minuto antes de nova tentativa
- Considerar upgrade do plano Brevo
- Reduzir BATCH_SIZE para distribuir ao longo do tempo

### Timeout
```python
❌ Erro ao enviar para user@email: Timeout
```
**Solução**: Verificar conectividade de rede ou aumentar timeout (atualmente 10s)

## 🔮 Melhorias Futuras

1. **Retry automático** com backoff exponencial
2. **Fila assíncrona** (Celery/Redis) para envios muito grandes
3. **Brevo Contacts API** para importação em massa
4. **Templates do Brevo** em vez de HTML inline
5. **Webhooks** para rastrear aberturas/cliques

## 📚 Referências

- [Brevo API Documentation](https://developers.brevo.com/docs)
- [Brevo SMTP API](https://developers.brevo.com/reference/sendtransacemail)
- [Rate Limits](https://developers.brevo.com/docs/api-limits)

---

**Última atualização**: 14/10/2025
**Versão**: 1.0.0
**Autor**: Sistema Pint of Science Brasil
