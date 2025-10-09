"""
Página Principal - Pint of Science Certificate System

Esta é a página principal do sistema que inclui:
- Área pública para inscrição de participantes
- Área pública para download de certificados
- Área de login para coordenadores
- Interface completa e responsiva
"""

import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict, Any

# Importar módulos do sistema
from app.core import settings
from app.db import init_database, db_manager
from app.models import Evento, Cidade, Funcao, ParticipanteCreate
from app.services import inscrever_participante, baixar_certificado
from app.auth import (
    login_coordenador,
    logout_coordenador,
    is_user_logged_in,
    get_current_user_info,
)
from app.utils import validar_email, formatar_data_exibicao, limpar_texto

# Configuração da página
st.set_page_config(
    page_title=f"{settings.app_name}",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado para melhorar a aparência
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .section-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }

    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }

    .info-message {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
    }

    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        margin-bottom: 1rem;
    }

    /* Estilo para inputs */
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #ddd;
    }

    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 1px solid #ddd;
    }

    /* Estilo para botões */
    .stButton > button {
        background: #e74c3c;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: #c0392b;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Esconder elementos do Streamlit */
    .stDeployButton {
        display: none;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1avcm2n ez1byc5 {
        visibility: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Funções auxiliares
def mostrar_mensagem(tipo: str, mensagem: str) -> None:
    """Exibe uma mensagem formatada."""
    if tipo == "success":
        st.markdown(
            f'<div class="success-message">✅ {mensagem}</div>', unsafe_allow_html=True
        )
    elif tipo == "error":
        st.markdown(
            f'<div class="error-message">❌ {mensagem}</div>', unsafe_allow_html=True
        )
    elif tipo == "info":
        st.markdown(
            f'<div class="info-message">ℹ️ {mensagem}</div>', unsafe_allow_html=True
        )


def carregar_dados_formulario() -> tuple:
    """Carrega dados para os formulários (eventos, cidades, funções)."""
    try:
        with db_manager.get_db_session() as session:
            from app.db import (
                get_evento_repository,
                get_cidade_repository,
                get_funcao_repository,
            )

            evento_repo = get_evento_repository(session)
            cidade_repo = get_cidade_repository(session)
            funcao_repo = get_funcao_repository(session)

            # Buscar evento atual
            evento_atual = evento_repo.get_current_event()

            # Buscar cidades e funções
            cidades = cidade_repo.get_all_ordered()
            funcoes = funcao_repo.get_all_ordered()

            # Extrair dados do evento antes de fechar a sessão
            evento_data = None
            if evento_atual:
                evento_data = {
                    "id": evento_atual.id,
                    "ano": evento_atual.ano,
                    "datas_evento": evento_atual.datas_evento,
                }

            # Extrair dados das cidades antes de fechar a sessão
            cidades_data = []
            for cidade in cidades:
                cidades_data.append(
                    {
                        "id": cidade.id,
                        "nome": cidade.nome,
                        "estado": cidade.estado,
                    }
                )

            # Extrair dados das funções antes de fechar a sessão
            funcoes_data = []
            for funcao in funcoes:
                funcoes_data.append(
                    {
                        "id": funcao.id,
                        "nome_funcao": funcao.nome_funcao,
                    }
                )

            return evento_data, cidades_data, funcoes_data

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None, [], []


def formulario_inscricao(evento_atual, cidades, funcoes) -> bool:
    """Exibe o formulário de inscrição de participantes."""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)

    st.subheader("📝 Formulário de Inscrição")
    st.write("Preencha os dados abaixo para se inscrever no evento:")

    # Informações do evento
    if evento_atual:
        st.info(
            f"🎯 **Evento Atual:** Pint of Science {evento_atual['ano']} ({evento_atual['datas_evento']})"
        )

    # Formulário
    with st.form("form_inscricao"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Digite seu nome completo",
                help="Nome como deve aparecer no certificado",
            )

            email = st.text_input(
                "E-mail *",
                placeholder="seu-email@dominio.com",
                help="Será usado para confirmar inscrição e enviar o certificado",
            )

        with col2:
            cidade_selecionada = st.selectbox(
                "Cidade *",
                options=[(f"{c['nome']} - {c['estado']}", c["id"]) for c in cidades],
                format_func=lambda x: x[0] if x else "Selecione...",
                help="Cidade onde você participará do evento",
            )

            funcao_selecionada = st.selectbox(
                "Função *",
                options=[(f["nome_funcao"], f["id"]) for f in funcoes],
                format_func=lambda x: x[0] if x else "Selecione...",
                help="Sua função no evento",
            )

        titulo_apresentacao = st.text_input(
            "Título da Apresentação (opcional)",
            placeholder="Se você for apresentador, informe o título",
            help="Apenas se você for apresentar alguma palestra/mesa redonda",
        )

        datas_participacao = st.multiselect(
            "Datas de Participação *",
            options=evento_atual["datas_evento"] if evento_atual else [],
            format_func=lambda x: (
                datetime.fromisoformat(x).strftime("%d/%m/%Y")
                if isinstance(x, str)
                else str(x)
            ),  # Parse ISO string to date and format as DD/MM/YYYY
            help="Selecione quais dias você participará do evento",
        )

        # Termo de consentimento
        st.markdown("---")
        st.markdown("**📋 Termo de Consentimento:**")
        consentimento = st.checkbox(
            "Eu concordo em ter meus dados utilizados para geração de certificados e comunicação do evento.",
            help="Seus dados serão criptografados e utilizados apenas para os fins do evento",
        )

        # Botão de envio
        submit_button = st.form_submit_button(
            "🚀 Realizar Inscrição", type="primary", use_container_width=True
        )

        if submit_button:
            # Validação dos dados
            if not all(
                [
                    nome,
                    email,
                    cidade_selecionada,
                    funcao_selecionada,
                    datas_participacao,
                ]
            ):
                mostrar_mensagem(
                    "error", "Por favor, preencha todos os campos obrigatórios."
                )
                return False

            if not validar_email(email):
                mostrar_mensagem(
                    "error", "Por favor, informe um endereço de e-mail válido."
                )
                return False

            if not consentimento:
                mostrar_mensagem(
                    "error", "Você precisa concordar com o termo de consentimento."
                )
                return False

            # Preparar dados
            dados_inscricao = ParticipanteCreate(
                nome_completo=limpar_texto(nome),
                email=limpar_texto(email).lower(),
                titulo_apresentacao=(
                    limpar_texto(titulo_apresentacao) if titulo_apresentacao else None
                ),
                evento_id=evento_atual["id"] if evento_atual else 1,
                cidade_id=cidade_selecionada[1],
                funcao_id=funcao_selecionada[1],
                datas_participacao=(
                    ", ".join(datas_participacao) if datas_participacao else ""
                ),
                carga_horaria_calculada=0,  # Será calculado automaticamente
            )

            # Realizar inscrição
            with st.spinner("Processando sua inscrição..."):
                sucesso, mensagem, participante_id = inscrever_participante(
                    dados_inscricao
                )

            if sucesso:
                mostrar_mensagem("success", f"✨ {mensagem}")
                st.session_state["inscricao_realizada"] = True
                st.session_state["email_inscricao"] = email
                return True
            else:
                mostrar_mensagem("error", mensagem)
                return False

    st.markdown("</div>", unsafe_allow_html=True)
    return False


def formulario_download_certificado(evento_atual) -> bool:
    """Exibe o formulário para download de certificados."""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)

    st.subheader("📜 Download de Certificado")
    st.write("Digite seu e-mail para baixar seu certificado:")

    # Informações importantes
    st.info(
        """
    ℹ️ **Importante:**
    - Apenas participantes com inscrição validada podem baixar certificados
    - Se você acabou de se inscrever, aguarde a validação pelos organizadores
    - Você receberá um e-mail quando seu certificado estiver disponível
    """
    )

    with st.form("form_download"):
        email = st.text_input(
            "E-mail cadastrado *",
            placeholder="seu-email@dominio.com",
            help="Use o mesmo e-mail da sua inscrição",
        )

        evento_id = st.selectbox(
            "Evento",
            options=(
                [(f"Pint of Science {evento_atual['ano']}", evento_atual["id"])]
                if evento_atual
                else []
            ),
            format_func=lambda x: x[0] if x else "Selecione...",
            help="Selecione o evento para baixar o certificado",
        )

        submit_button = st.form_submit_button(
            "📥 Baixar Certificado", type="primary", use_container_width=True
        )

        if submit_button:
            if not email:
                mostrar_mensagem("error", "Por favor, informe seu e-mail.")
                return False

            if not validar_email(email):
                mostrar_mensagem(
                    "error", "Por favor, informe um endereço de e-mail válido."
                )
                return False

            # Baixar certificado
            with st.spinner("Verificando seu certificado..."):
                sucesso, pdf_bytes, mensagem = baixar_certificado(
                    email.lower().strip(), evento_id[1] if evento_id else 1
                )

            if sucesso and pdf_bytes:
                # Gerar nome do arquivo
                from datetime import datetime

                nome_arquivo = f"Certificado-PintOfScience-{evento_atual['ano'] if evento_atual else '2024'}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                st.success(f"🎉 {mensagem}")
                st.download_button(
                    label="📄 Clique aqui para baixar o PDF",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    use_container_width=True,
                )
                return True
            else:
                mostrar_mensagem("error", mensagem)
                return False

    st.markdown("</div>", unsafe_allow_html=True)
    return False


def formulario_login_coordenador() -> bool:
    """Exibe o formulário de login para coordenadores."""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)

    st.subheader("🔐 Área Restrita - Coordenadores")
    st.write("Acesso exclusivo para coordenadores e organizadores:")

    with st.form("form_login"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "E-mail", placeholder="seu-email@dominio.com", type="default"
            )

        with col2:
            senha = st.text_input(
                "Senha", placeholder="Digite sua senha", type="password"
            )

        submit_button = st.form_submit_button(
            "🚪 Entrar", type="primary", use_container_width=True
        )

        if submit_button:
            if not email or not senha:
                mostrar_mensagem("error", "Por favor, preencha e-mail e senha.")
                return False

            # Realizar login
            with st.spinner("Autenticando..."):
                sucesso = login_coordenador(email.strip().lower(), senha)

            if sucesso:
                st.success("🎉 Login realizado com sucesso!")
                st.rerun()
                return True
            else:
                mostrar_mensagem("error", "E-mail ou senha incorretos.")
                return False

    st.markdown("</div>", unsafe_allow_html=True)
    return False


def mostrar_menu_usuario_logado() -> None:
    """Exibe o menu do usuário logado na sidebar."""
    user_info = get_current_user_info()

    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Usuário Logado")
        st.sidebar.write(f"**Nome:** {user_info['name']}")
        st.sidebar.write(f"**E-mail:** {user_info['email']}")
        st.sidebar.write(
            f"**Tipo:** {'Superadmin' if user_info['is_superadmin'] else 'Coordenador'}"
        )

        if user_info.get("login_time"):
            tempo_login = formatar_data_exibicao(user_info["login_time"])
            st.sidebar.write(f"**Login:** {tempo_login}")

        if st.sidebar.button("🚪 Sair", use_container_width=True):
            logout_coordenador()


def main():
    """Função principal da aplicação."""

    # Inicializar banco de dados
    try:
        init_database()
    except Exception as e:
        st.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        st.error(
            "Por favor, verifique se o arquivo .env está configurado corretamente."
        )
        st.stop()

    # Cabeçalho principal
    st.markdown(
        """
    <div class="main-header">
        <h1>🍺 Pint of Science Brasil</h1>
        <h2>Sistema de Inscrição e Emissão de Certificados</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navegação")

        # Verificar se usuário está logado
        if is_user_logged_in():
            mostrar_menu_usuario_logado()

            st.markdown("### 📋 Acesso Rápido")
            if st.button("✅ Validação de Participantes", use_container_width=True):
                st.switch_page("pages/1_✅_Validação_de_Participantes.py")

            if get_current_user_info().get("is_superadmin"):
                if st.button("⚙️ Administração", use_container_width=True):
                    st.switch_page("pages/2_⚙️_Administração.py")

        st.markdown("---")
        st.markdown("### 📊 Status do Sistema")

        # Mostrar informações do sistema
        try:
            from app.db import check_database_health

            health = check_database_health()

            if health["status"] == "healthy":
                st.success("✅ Sistema Online")
                st.info(
                    f"📊 {health.get('details', {}).get('table_counts', {}).get('participantes', 0)} participantes"
                )
            elif health["status"] == "warning":
                st.warning("⚠️ Sistema Online (sem dados)")
            else:
                st.error("❌ Sistema com problemas")

        except Exception:
            st.info("📡 Verificando status...")

    # Conteúdo principal
    # Verificar se há mensagem de sucesso na sessão
    if st.session_state.get("inscricao_realizada"):
        st.success(
            "🎉 Inscrição realizada com sucesso! Aguarde a validação dos organizadores."
        )
        st.info(
            f"📧 Enviamos um e-mail de confirmação para: {st.session_state.get('email_inscricao', '')}"
        )

        if st.button("🔄 Fazer Nova Inscrição"):
            st.session_state["inscricao_realizada"] = False
            st.session_state["email_inscricao"] = None
            st.rerun()

    # Carregar dados para os formulários
    evento_atual, cidades, funcoes = carregar_dados_formulario()

    if not evento_atual:
        st.warning("⚠️ Nenhum evento encontrado. Contate o administrador do sistema.")
        return

    # Abas para organizar o conteúdo
    tab1, tab2, tab3 = st.tabs(["📝 Inscrição", "📜 Certificados", "🔐 Coordenadores"])

    with tab1:
        formulario_inscricao(evento_atual, cidades, funcoes)

    with tab2:
        formulario_download_certificado(evento_atual)

    with tab3:
        if is_user_logged_in():
            st.info(
                "✅ Você já está logado! Use o menu lateral para acessar as áreas restritas."
            )
        else:
            formulario_login_coordenador()

    # Rodapé
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Pint of Science Brasil</strong> - Sistema de Inscrição e Emissão Certificados</p>
        <p>Desenvolvido com ❤️ para a comunidade científica brasileira</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
