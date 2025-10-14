"""
Página de Validação de Certificados

Permite que qualquer pessoa valide a autenticidade de um certificado
usando o hash de validação fornecido no certificado.
"""

import streamlit as st
from datetime import datetime
from app.db import (
    db_manager,
    get_participante_repository,
    get_evento_repository,
    get_cidade_repository,
    get_funcao_repository,
)
from app.core import settings
from app.models import Participante, Evento, Cidade, Funcao
from app.services import servico_criptografia, servico_calculo_carga_horaria

st.set_page_config(
    page_title=f"Validar Certificado - {settings.app_name}",
    page_icon="✅",
    layout="centered",
)

# Custom CSS para reduzir tamanho da fonte nos metrics
st.markdown(
    """
    <style>
    .header-main {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Reduzir tamanho da fonte do valor do metric */
    [data-testid="stMetricValue"] {
        font-size: 1.33rem !important;
    }

    /* Reduzir tamanho da fonte do label do metric */
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
    }

    /* Ajustar espaçamento */
    [data-testid="metric-container"] {
        padding: 0.5rem 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Título da página
st.markdown(
    """
    <div class="header-main">
        <h1>✅ Validação de Certificado</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Instruções
st.info(
    """
    **ℹ️ Como validar seu certificado:**

    1. Localize o código de validação no rodapé do seu certificado PDF
    2. Cole o código no campo abaixo
    3. Clique em “Validar Certificado"

    O código de validação tem 64 caracteres (letras e números).
    """
)

# Verificar se há hash na URL (vindo do link no PDF)
query_params = st.query_params
hash_from_url = query_params.get("hash", None)

# Campo para inserir o hash
if hash_from_url:
    hash_validacao = st.text_input(
        "Código de Validação:",
        value=hash_from_url,
        max_chars=64,
        help="Hash de 64 caracteres encontrado no certificado",
    )
else:
    hash_validacao = st.text_input(
        "Código de Validação:",
        placeholder="Insira o código de validação do certificado",
        max_chars=64,
        help="Hash de 64 caracteres encontrado no certificado",
    )

# Botão de validação
if st.button("🔍 Validar Certificado", type="primary", width="content"):
    if not hash_validacao or len(hash_validacao) != 64:
        st.error("❌ Código de validação inválido! Deve ter exatamente 64 caracteres.")
    else:
        with st.spinner("Verificando autenticidade..."):
            try:
                with db_manager.get_db_session() as session:
                    participante_repo = get_participante_repository(session)
                    evento_repo = get_evento_repository(session)
                    cidade_repo = get_cidade_repository(session)
                    funcao_repo = get_funcao_repository(session)

                    # Buscar participante pelo hash
                    participante = (
                        session.query(Participante)
                        .filter(Participante.hash_validacao == hash_validacao)
                        .first()
                    )

                    if not participante:
                        st.error(
                            "❌ **Certificado NÃO ENCONTRADO**\n\n"
                            "Este código de validação não corresponde a nenhum certificado "
                            "emitido pelo Pint of Science Brasil.\n\n"
                            "**Possíveis causas:**\n"
                            "- Código digitado incorretamente\n"
                            "- Certificado falsificado\n"
                            "- Certificado ainda não foi emitido"
                        )
                    else:
                        # Descriptografar dados
                        nome_completo = servico_criptografia.descriptografar(
                            participante.nome_completo_encrypted
                        )
                        email = servico_criptografia.descriptografar(
                            participante.email_encrypted
                        )

                        # Verificar HMAC para garantir integridade
                        hash_esperado = (
                            servico_criptografia.gerar_hash_validacao_certificado(
                                participante.id,
                                participante.evento_id,
                                email,
                                nome_completo,
                            )
                        )

                        if hash_validacao != hash_esperado:
                            st.error(
                                "❌ **Certificado INVÁLIDO**\n\n"
                                "A assinatura digital deste certificado foi comprometida.\n"
                                "Este certificado pode ter sido adulterado ou falsificado."
                            )
                        else:
                            # Buscar dados relacionados
                            evento = evento_repo.get_by_id(
                                Evento, participante.evento_id
                            )
                            cidade = cidade_repo.get_by_id(
                                Cidade, participante.cidade_id
                            )
                            funcao = funcao_repo.get_by_id(
                                Funcao, participante.funcao_id
                            )

                            # Calcular carga horária on-the-fly
                            carga_horaria, _ = (
                                servico_calculo_carga_horaria.calcular_carga_horaria(
                                    participante.datas_participacao,
                                    evento.datas_evento,
                                    evento.ano,
                                    participante.funcao_id,
                                )
                            )

                            # Certificado válido
                            st.success("✅ **CERTIFICADO AUTÊNTICO**")
                            st.balloons()

                            st.markdown("---")
                            st.subheader("📋 Informações do Certificado")

                            # Exibir informações em colunas
                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric("👤 Participante", nome_completo)
                                st.metric(
                                    "🎭 Função", funcao.nome_funcao if funcao else "N/A"
                                )
                                st.metric(
                                    "📍 Cidade",
                                    (
                                        f"{cidade.nome} - {cidade.estado}"
                                        if cidade
                                        else "N/A"
                                    ),
                                )

                            with col2:
                                st.metric(
                                    "📅 Evento",
                                    (
                                        f"Pint of Science {evento.ano}"
                                        if evento
                                        else "N/A"
                                    ),
                                )
                                st.metric(
                                    "⏱️ Carga Horária",
                                    f"{carga_horaria}h",
                                )
                                st.metric(
                                    "✅ Status",
                                    (
                                        "Validado"
                                        if participante.validado
                                        else "Aguardando validação"
                                    ),
                                )

                            # Informações adicionais
                            st.markdown("---")
                            st.markdown("**📄 Detalhes Adicionais:**")

                            if participante.titulo_apresentacao:
                                st.markdown(
                                    f"**Título da apresentação:**  \n{participante.titulo_apresentacao}"
                                )

                            # Formatar datas de participação
                            datas_list = [
                                d.strip()
                                for d in participante.datas_participacao.split(",")
                            ]
                            datas_formatadas = []
                            for data in datas_list:
                                try:
                                    dt = datetime.fromisoformat(data)
                                    datas_formatadas.append(dt.strftime("%d/%m/%Y"))
                                except:
                                    datas_formatadas.append(data)

                            st.markdown(
                                f"**Datas de participação:**  \n{', '.join(datas_formatadas)}"
                            )

                            # Data de inscrição
                            try:
                                dt_inscricao = datetime.fromisoformat(
                                    participante.data_inscricao
                                )
                                st.markdown(
                                    f"**Data de inscrição:**  \n{dt_inscricao.strftime('%d/%m/%Y às %H:%M')}"
                                )
                            except:
                                st.markdown(
                                    f"**Data de inscrição:**  \n{participante.data_inscricao}"
                                )

                            # Código de validação
                            st.markdown("---")
                            st.markdown("**🔒 Código de Validação (Hash):**")
                            st.code(hash_validacao, language=None)

                            st.info(
                                "Este certificado foi verificado em "
                                f"{datetime.now().strftime('%d/%m/%Y às %H:%M')} e confirmado como autêntico."
                            )

            except Exception as e:
                st.error(f"❌ Erro ao validar certificado: {str(e)}")
                st.exception(e)

# Rodapé informativo
st.markdown("---")
st.markdown(
    """
    ### 🔐 Sobre a Validação

    Todos os certificados emitidos pelo Pint of Science Brasil possuem um **código único de validação**
    que garante sua autenticidade. Este código é gerado usando criptografia HMAC-SHA256 e não pode ser
    falsificado.

    **Como funciona:**
    - Cada certificado recebe um hash único baseado nos dados do participante
    - O hash é verificável mas não pode ser reproduzido sem a chave secreta
    - Mesmo pequenas alterações nos dados invalidam o certificado
    - Não armazenamos cópias dos PDFs - a validação é feita através do banco de dados

    Se você encontrar algum problema com a validação, entre em contato com os organizadores do evento.
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="text-align: center; color: #95a5a6; margin-top: 40px;">'
    "“Levando a ciência para o bar” - © Pint of Science Brasil"
    "</p>",
    unsafe_allow_html=True,
)
