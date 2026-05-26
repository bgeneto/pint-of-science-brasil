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
from pathlib import Path

# Importar módulos do sistema
from app.core import settings
from app.db import init_database, db_manager
from app.models import Evento, Cidade, Funcao, ParticipanteCreate
from app.services import inscrever_participante, baixar_certificado
from app.auth import (
    show_login,
    logout,
    is_user_logged_in,
    get_current_user_info,
    auth_manager,
    login_coordenador,
)
from app.utils import validar_email, formatar_data_exibicao, limpar_texto

# Configuração da página
st.set_page_config(
    page_title=f"Home - {settings.app_name}",
    page_icon="🍺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CRITICAL: Check authentication cookie IMMEDIATELY after page config
# This MUST be done before any other Streamlit operations
# The authenticator automatically checks cookies when login() is called
try:
    # Call the authenticator's login with location='unrendered' to check cookie without showing form
    # This will restore session from cookie if it exists
    if auth_manager.authenticator:
        name, authentication_status, username = auth_manager.authenticator.login(
            location="unrendered"
        )
        # If cookie restored the session, update our custom session keys
        if authentication_status and username and not st.session_state.get("logged_in"):
            auth_manager.handle_login_result(name, authentication_status, username)
except Exception as e:
    pass  # Ignore errors in cookie restoration, user will just need to login again

# CSS customizado para melhorar a aparência
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #c67b5c 0%, #a0563f 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }

    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }

    .info-message {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }

    /* Melhorar espaçamento das tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }

    /* Esconder elementos do Streamlit */
    .stDeployButton {
        display: none;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

            # Buscar TODOS os eventos (para permitir download de certificados de anos anteriores)
            todos_eventos = evento_repo.get_all(Evento)

            # Buscar cidades e funções
            cidades = cidade_repo.get_all_ordered()
            funcoes = funcao_repo.get_all_ordered()

            # Extrair dados do evento atual antes de fechar a sessão
            evento_data = None
            if evento_atual:
                evento_data = {
                    "id": evento_atual.id,
                    "ano": evento_atual.ano,
                    "datas_evento": evento_atual.datas_evento,
                }

            # Extrair dados de TODOS os eventos antes de fechar a sessão
            eventos_data = []
            for evento in todos_eventos:
                eventos_data.append(
                    {
                        "id": evento.id,
                        "ano": evento.ano,
                        "datas_evento": evento.datas_evento,
                    }
                )

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

            return evento_data, eventos_data, cidades_data, funcoes_data

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None, [], [], []


def formulario_inscricao(evento_atual, cidades, funcoes) -> Dict[str, Any]:
    """Exibe o formulário de inscrição de participantes."""
    st.subheader("📝 Formulário de Inscrição")
    st.write("Preencha os dados abaixo para se inscrever no evento atual.")

    # Informações do evento
    if evento_atual:
        st.success(f"🎯 Evento Atual: **Pint of Science {evento_atual['ano']}**")

    # Inicializar resultado
    resultado = {"sucesso": False, "mensagem": "", "email": ""}

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
                options=[("", None)]
                + [(f"{c['nome']} - {c['estado']}", c["id"]) for c in cidades],
                format_func=lambda x: x[0] if x and x[0] else "Selecione...",
                help="Cidade onde você participará do evento",
                index=0,
            )

            # Find default index for "Palestrante"
            default_funcao_index = next(
                (i for i, f in enumerate(funcoes) if f["nome_funcao"] == "Palestrante"),
                0,  # Default to first option if "Palestrante" not found
            )

            funcao_selecionada = st.selectbox(
                "Função *",
                options=[(f["nome_funcao"], f["id"]) for f in funcoes],
                format_func=lambda x: x[0] if x else "Selecione...",
                help="Sua função no evento",
                index=default_funcao_index,
            )

        titulo_apresentacao = st.text_input(
            "Título da Apresentação (somente se aplicável)",
            placeholder="Se você for palestrante, informe o título",
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
        st.markdown("📋 Termo de Consentimento *")
        consentimento = st.checkbox(
            "Eu concordo em ter meus dados utilizados para geração de certificados e comunicação do evento.",
            help="Seus dados serão criptografados e utilizados apenas para os fins do evento",
        )

        # Botão de envio
        submit_button = st.form_submit_button(
            "🚀 Realizar Inscrição", type="primary", width="content"
        )

        if submit_button:
            # Validação dos dados
            if (
                not all(
                    [
                        nome,
                        email,
                        datas_participacao,
                    ]
                )
                or not cidade_selecionada[1]
                or not funcao_selecionada[1]
            ):
                mostrar_mensagem(
                    "error", "Por favor, preencha todos os campos obrigatórios."
                )
                return resultado

            if not validar_email(email):
                mostrar_mensagem(
                    "error", "Por favor, informe um endereço de e-mail válido."
                )
                return resultado

            if not consentimento:
                mostrar_mensagem(
                    "error", "Você precisa concordar com o termo de consentimento."
                )
                return resultado

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
            )

            # Realizar inscrição
            with st.spinner("Processando sua inscrição..."):
                sucesso, mensagem, participante_id = inscrever_participante(
                    dados_inscricao
                )

            if sucesso:
                resultado["sucesso"] = True
                resultado["mensagem"] = mensagem
                resultado["email"] = email
                st.session_state["inscricao_realizada"] = True
                st.session_state["email_inscricao"] = email
            else:
                mostrar_mensagem("error", mensagem)

    return resultado


def formulario_download_certificado(evento_atual, todos_eventos, funcoes) -> bool:
    """Exibe o formulário para download de certificados."""
    st.subheader("📜 Download de Certificado")
    st.write("Digite seu e-mail para baixar seu certificado:")

    # Informações importantes
    st.info(
        """
    ℹ️ **Importante:**
    - Apenas participantes com apresentação validada pelos coordenadores podem baixar certificados
    - Se você tem mais de uma inscrição no mesmo evento, selecione a função correspondente ao certificado desejado
    - Se você acabou de se inscrever, aguarde a validação pelos coordenadores após a sua apresentação
    - Você receberá um e-mail quando seu certificado estiver disponível
    """
    )

    with st.form("form_download"):
        email = st.text_input(
            "E-mail cadastrado *",
            placeholder="seu-email@dominio.com",
            help="Use o mesmo e-mail da sua inscrição",
        )

        # Sort events by year descending (most recent first)
        eventos_ordenados = (
            sorted(todos_eventos, key=lambda e: e["ano"], reverse=True)
            if todos_eventos
            else []
        )

        # Find the index of the current event to set as default
        default_index = 0  # Fallback to most recent
        if evento_atual and eventos_ordenados:
            try:
                default_index = next(
                    (
                        i
                        for i, e in enumerate(eventos_ordenados)
                        if e["id"] == evento_atual["id"]
                    ),
                    0,  # Fallback to most recent if current event not found
                )
            except Exception:
                default_index = 0

        evento_id = st.selectbox(
            "Evento *",
            options=(
                [
                    (f"Pint of Science {evento['ano']}", evento["id"])
                    for evento in eventos_ordenados
                ]
                if eventos_ordenados
                else []
            ),
            format_func=lambda x: x[0] if x else "Selecione...",
            help="Selecione o evento para baixar o certificado",
            index=(
                default_index if eventos_ordenados else None
            ),  # Default to current event
        )

        funcao_selecionada = st.selectbox(
            "Função *",
            options=[("", None)]
            + [(funcao["nome_funcao"], funcao["id"]) for funcao in funcoes],
            format_func=lambda x: x[0] if x and x[0] else "Selecione...",
            help="Selecione a mesma função usada na inscrição",
            index=0,
        )

        submit_button = st.form_submit_button(
            "👁️ Visualizar Certificado", type="primary", width="content"
        )

    # Process form submission OUTSIDE the form context
    if submit_button:
        if not email:
            mostrar_mensagem("error", "Por favor, informe seu e-mail.")
            return False

        if not validar_email(email):
            mostrar_mensagem(
                "error", "Por favor, informe um endereço de e-mail válido."
            )
            return False

        if not evento_id:
            mostrar_mensagem("error", "Por favor, selecione um evento.")
            return False

        if not funcao_selecionada[1]:
            mostrar_mensagem("error", "Por favor, selecione a função.")
            return False

        # Baixar certificado
        with st.spinner("Verificando seu certificado..."):
            sucesso, pdf_bytes, mensagem = baixar_certificado(
                email.lower().strip(),
                evento_id[1] if evento_id else None,
                funcao_selecionada[1],
            )

        if sucesso and pdf_bytes:
            # Gerar nome do arquivo usando o ano do evento selecionado
            from datetime import datetime

            # Get the selected event's year
            ano_selecionado = next(
                (e["ano"] for e in eventos_ordenados if e["id"] == evento_id[1]),
                evento_atual["ano"] if evento_atual else datetime.now().year,
            )

            nome_arquivo = f"Certificado-PintOfScience-{ano_selecionado}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            st.success(f"🎉 {mensagem}")

            # Display PDF preview
            st.markdown("### 📄 Pré-visualização do Certificado")
            st.pdf(pdf_bytes)

            # Provide download button
            st.download_button(
                label="📥 Baixar PDF",
                data=pdf_bytes,
                file_name=nome_arquivo,
                mime="application/pdf",
                width="content",
            )
            return True
        else:
            mostrar_mensagem("error", mensagem)
            return False

    return False


def formulario_login_coordenador() -> bool:
    """Exibe o formulário de login para coordenadores."""
    st.subheader("🔐 Área Restrita - Coordenadores")
    st.write("Acesso exclusivo para coordenadores")

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
            "🔓 Entrar", type="primary", width="content"
        )

        if submit_button:
            if not email or not senha:
                mostrar_mensagem("error", "Por favor, preencha e-mail e senha.")
                return False

            # Realizar login com validação customizada
            with st.spinner("Autenticando..."):
                sucesso = login_coordenador(email.strip().lower(), senha)

            if sucesso:
                # Redirecionar imediatamente para a página de validação
                st.switch_page("pages/1_👨‍👨‍👦‍👦_Participantes.py")
            # Mensagens de erro já são mostradas por login_coordenador()

    return False


def mostrar_menu_usuario_logado() -> None:
    """Exibe o menu do usuário logado na sidebar."""
    user_info = get_current_user_info()

    if user_info:
        st.sidebar.markdown("### 👤 Usuário Logado")
        st.sidebar.write(f"**Nome:** {user_info['name']}")
        st.sidebar.write(f"**E-mail:** {user_info['email']}")
        st.sidebar.write(
            f"**Tipo:** {'Superadmin' if user_info['is_superadmin'] else 'Coordenador'}"
        )

        if user_info.get("login_time"):
            tempo_login = formatar_data_exibicao(user_info["login_time"])
            st.sidebar.write(f"**Login:** {tempo_login}")

        if st.sidebar.button("🔒 Sair", width="stretch"):
            auth_manager.clear_session()
            st.rerun()


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
        # Verificar se usuário está logado
        if is_user_logged_in():
            mostrar_menu_usuario_logado()

        # Documentação
        st.markdown("### 📄 Documentação")

        # Link para PDF do manual
        col1, col2 = st.columns(2)

        with col1:
            # Verifica se o PDF existe
            pdf_path = Path("docs-site/pdf/manual-completo-pint-brasil.pdf")
            if pdf_path.exists():
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Manual",
                        data=pdf_file,
                        file_name="Manual-Pint-of-Science-Brasil.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        help="Baixe o manual completo do sistema em PDF",
                    )

        with col2:
            # Link para documentação HTML local via MkDocs
            st.link_button(
                "🌍 Docs",
                f"{settings.base_url}/docs/",
                use_container_width=True,
                help="Página de documentação do sistema",
            )

        st.markdown("---")
        st.markdown("### 📊 Status do Sistema")

        # Mostrar informações do sistema
        try:
            from app.db import check_database_health

            health = check_database_health()

            if health["status"] == "healthy":
                st.success("✅ Sistema Online")
                # st.info(
                #    f"📊 {health.get('details', {}).get('table_counts', {}).get('participantes', 0)} participantes"
                # )
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
            "🎉 Inscrição realizada com sucesso! Uma excelente participação para você!"
        )
        st.info(
            f"📧 Enviamos um e-mail de confirmação para: {st.session_state.get('email_inscricao', '')}"
        )

    # Carregar dados para os formulários
    evento_atual, todos_eventos, cidades, funcoes = carregar_dados_formulario()

    if not evento_atual:
        st.warning("⚠️ Nenhum evento encontrado. Contate o administrador do sistema.")
        return

    # Verificar se foi redirecionado para login
    if st.session_state.get("redirect_to_login"):
        st.info(
            "ℹ️ Por favor, faça login na aba **🔐 Coordenadores** para acessar esta área."
        )
        st.session_state["active_tab"] = "🔐 Coordenadores"
        st.session_state["redirect_to_login"] = False

    # Inicializar aba ativa se não existir
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "📝 Inscrição"

    # Abas para organizar o conteúdo (usando segmented control para permitir controle programático)
    active_tab = st.segmented_control(
        "Navegação",
        options=["📝 Inscrição", "📜 Certificado", "🔐 Coordenadores"],
        key="active_tab",
        label_visibility="collapsed",
    )

    if active_tab == "📝 Inscrição":
        resultado_inscricao = formulario_inscricao(evento_atual, cidades, funcoes)

        # Mostrar mensagens de resultado da inscrição
        if resultado_inscricao["sucesso"]:
            st.success(
                "🎉 Inscrição realizada com sucesso! Uma excelente participação para você!"
            )
            st.info(
                f"📧 Enviamos um e-mail de confirmação para: {resultado_inscricao['email']}"
            )
    elif active_tab == "📜 Certificado":
        formulario_download_certificado(evento_atual, todos_eventos, funcoes)
    elif active_tab == "🔐 Coordenadores":
        if is_user_logged_in():
            st.switch_page("pages/1_👨‍👨‍👦‍👦_Participantes.py")
        else:
            formulario_login_coordenador()

    # Rodapé
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>© Pint of Science Brasil</strong> - Sistema de Inscrição e Emissão de Certificados</p>
        <p>Desenvolvido por bgeneto com ❤️ para a comunidade científica brasileira</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
