"""
Página Administrativa - Superadmin

Esta página permite que superadmins gerenciem todo o sistema:
- CRUD de coordenadores
- CRUD de eventos
- CRUD de cidades
- CRUD de funções
- Gestão geral do sistema
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import json
from pathlib import Path

# Importar módulos do sistema
from app.auth import (
    require_superadmin,
    get_current_user_info,
    criar_coordenador,
    auth_manager,
)
from app.db import db_manager
from app.models import Evento, Cidade, Funcao, Coordenador, Participante
from app.utils import formatar_data_exibicao, limpar_texto, validar_email

# Configure logging
logger = logging.getLogger(__name__)

# CRITICAL: Check authentication cookie BEFORE require_superadmin
# This restores the session from cookie if it exists
try:
    if auth_manager.authenticator:
        name, authentication_status, username = auth_manager.authenticator.login(
            location="unrendered"
        )
        if authentication_status and username and not st.session_state.get("logged_in"):
            auth_manager.handle_login_result(name, authentication_status, username)
except Exception:
    pass  # Will be caught by require_superadmin below

# Proteção de acesso - agora é simples!
require_superadmin()

# Sidebar - Mostrar informações do usuário logado
with st.sidebar:
    user_info = get_current_user_info()
    if user_info:
        st.markdown("### 👤 Usuário Logado")
        st.write(f"**Nome:** {user_info['name']}")
        st.write(f"**E-mail:** {user_info['email']}")
        st.write(
            f"**Tipo:** {'Superadmin' if user_info['is_superadmin'] else 'Coordenador'}"
        )

        if user_info.get("login_time"):
            tempo_login = formatar_data_exibicao(user_info["login_time"])
            st.write(f"**Login:** {tempo_login}")

        if st.button("🔒 Sair", key="logout_btn", width="stretch"):
            auth_manager.clear_session()
            st.rerun()

# CSS customizado
st.markdown(
    """
<style>
    .header-admin {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .admin-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
    }

    /* Esconder elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


def mostrar_informacoes_usuario():
    """Exibe informações do usuário logado."""
    user_info = get_current_user_info()

    if user_info:
        st.info(
            f"👤 **Superadmin:** {user_info['name']} ({user_info['email']})  \n"
            f"⏰ **Login:** {formatar_data_exibicao(user_info.get('login_time', ''))}  \n"
            f"🔐 **Acesso:** Total (Superadmin)"
        )


def mostrar_estatisticas_gerais():
    """Exibe estatísticas gerais do sistema."""
    try:
        with db_manager.get_db_session() as session:
            from app.db import (
                get_evento_repository,
                get_cidade_repository,
                get_funcao_repository,
                get_coordenador_repository,
                get_participante_repository,
            )

            evento_repo = get_evento_repository(session)
            cidade_repo = get_cidade_repository(session)
            funcao_repo = get_funcao_repository(session)
            coord_repo = get_coordenador_repository(session)
            participante_repo = get_participante_repository(session)

            # Contar registros
            eventos_count = len(evento_repo.get_all(Evento))
            cidades_count = len(cidade_repo.get_all_ordered())
            funcoes_count = len(funcao_repo.get_all_ordered())
            coordenadores_count = len(coord_repo.get_all(Coordenador))
            participantes_count = len(participante_repo.get_all(Participante))

            # Participantes validados
            participantes_validados = len(
                participante_repo.get_validated_participants(
                    evento_repo.get_current_event().id
                    if evento_repo.get_current_event()
                    else 1
                )
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(
                    f"""
                <div class="admin-card">
                    <h3 style="color: #2c3e50; margin: 0;">{coordenadores_count}</h3>
                    <p style="color: #7f8c8d; margin: 0;">Coordenadores</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                <div class="admin-card">
                    <h3 style="color: #2c3e50; margin: 0;">{cidades_count}</h3>
                    <p style="color: #7f8c8d; margin: 0;">Cidades</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                <div class="admin-card">
                    <h3 style="color: #2c3e50; margin: 0;">{participantes_count}</h3>
                    <p style="color: #7f8c8d; margin: 0;">Participantes</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col4:
                st.markdown(
                    f"""
                <div class="admin-card">
                    <h3 style="color: #27ae60; margin: 0;">{participantes_validados}</h3>
                    <p style="color: #7f8c8d; margin: 0;">Validados</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {str(e)}")


@st.dialog("🗺️ Associar Cidades ao Coordenador", width="large")
def modal_associar_cidades_coordenador(coordenador_id: int, coordenador_nome: str):
    """Modal para associar cidades a um coordenador recém-criado."""
    st.markdown(
        f"""
        ### Associar cidades a **{coordenador_nome}**

        💡 **Importante:**
        - Selecione as cidades que este coordenador poderá gerenciar
        - Coordenadores só podem visualizar e validar participantes das cidades associadas
        - Você pode pular esta etapa e fazer a associação depois, se preferir
        """
    )

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_cidade_repository
            from app.models import CoordenadorCidadeLink

            cidade_repo = get_cidade_repository(session)
            cidades = cidade_repo.get_all_ordered()

            if not cidades:
                st.warning(
                    "⚠️ Nenhuma cidade cadastrada. Cadastre cidades primeiro na aba **🏙️ Cidades**."
                )
                if st.button("✅ Fechar", type="primary", use_container_width=True):
                    st.session_state["show_modal_associacao"] = False
                    st.rerun()
                return

            # Preparar options como tuplas
            cidades_options = [(c.id, f"{c.nome}-{c.estado}") for c in cidades]

            # Multiselect com cidades
            cidades_selecionadas = st.multiselect(
                "Selecione as cidades",
                options=cidades_options,
                format_func=lambda x: x[1] if isinstance(x, tuple) else str(x),
                help="Escolha uma ou mais cidades para associar ao coordenador",
                key=f"modal_cidades_coord_{coordenador_id}",
            )

            # Extrair apenas os IDs
            cidades_ids_selecionados = [
                c[0] if isinstance(c, tuple) else c for c in cidades_selecionadas
            ]

            if st.button(
                "💾 Salvar Associações",
                type="primary",
                use_container_width=True,
                disabled=len(cidades_ids_selecionados) == 0,
            ):
                try:
                    # Criar novas associações
                    for cidade_id in cidades_ids_selecionados:
                        novo_link = CoordenadorCidadeLink(
                            coordenador_id=coordenador_id, cidade_id=cidade_id
                        )
                        session.add(novo_link)

                    session.commit()

                    # Armazenar mensagem de sucesso
                    cidades_nomes = [
                        c[1]
                        for c in cidades_options
                        if c[0] in cidades_ids_selecionados
                    ]
                    st.session_state["show_success_associacao_modal"] = (
                        f"✅ {len(cidades_ids_selecionados)} cidade(s) associada(s) a {coordenador_nome}: "
                        f"{', '.join(cidades_nomes)}"
                    )
                    # Clear modal state and trigger rerun
                    del st.session_state["show_modal_associacao"]
                    del st.session_state["modal_coord_id"]
                    del st.session_state["modal_coord_nome"]
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"❌ Erro ao salvar associações: {str(e)}")

    except Exception as e:
        st.error(f"❌ Erro ao carregar cidades: {str(e)}")
        logger.error(f"Erro em modal_associar_cidades_coordenador: {str(e)}")


def formulario_criar_coordenador() -> bool:
    """Formulário para criar novo coordenador."""
    st.subheader("➕ Criar Novo Coordenador")

    with st.form("form_criar_coordenador"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Digite o nome completo",
                help="Nome como deve aparecer no sistema",
            )

            email = st.text_input(
                "E-mail *",
                placeholder="email@dominio.com",
                help="E-mail para login e comunicação",
            )

        with col2:
            senha = st.text_input(
                "Senha *",
                placeholder="Digite uma senha forte",
                type="password",
                help="Mínimo de 8 caracteres",
            )

            confirmar_senha = st.text_input(
                "Confirmar Senha *",
                placeholder="Digite a senha novamente",
                type="password",
            )

        is_superadmin = False  # do not allow creating superadmin from UI
        # is_superadmin = st.checkbox(
        #    "É Superadmin?",
        #    help="Marque se este usuário deve ter acesso total ao sistema, permitindo gerenciar outros coordenadores e configurações do sistema.",
        # )

        submit_button = st.form_submit_button(
            "👤 Criar Coordenador", type="primary", width="stretch"
        )

        if submit_button:
            # Validações
            if not all([nome, email, senha, confirmar_senha]):
                st.error("❌ Preencha todos os campos obrigatórios.")
                return False

            if not validar_email(email):
                st.error("❌ E-mail inválido.")
                return False

            if senha != confirmar_senha:
                st.error("❌ As senhas não coincidem.")
                return False

            if len(senha) < 8:
                st.error("❌ A senha deve ter pelo menos 8 caracteres.")
                return False

            # Criar coordenador
            with st.spinner("Criando coordenador..."):
                try:
                    # Get coordenador ID after creation
                    with db_manager.get_db_session() as session:
                        from app.db import get_coordenador_repository

                        # Create coordenador
                        sucesso = criar_coordenador(
                            nome=limpar_texto(nome),
                            email=limpar_texto(email).lower(),
                            senha=senha,
                            is_superadmin=is_superadmin,
                        )

                        if sucesso:
                            # Get the coordenador ID to pass to modal
                            coord_repo = get_coordenador_repository(session)
                            coordenador = coord_repo.get_by_email(
                                limpar_texto(email).lower()
                            )

                            if coordenador:
                                # Store info to show modal and success message
                                st.session_state["show_success_coordenador"] = (
                                    "✅ Coordenador criado com sucesso!"
                                )
                                # Only show modal if not superadmin
                                if not is_superadmin:
                                    st.session_state["show_modal_associacao"] = True
                                    st.session_state["modal_coord_id"] = coordenador.id
                                    st.session_state["modal_coord_nome"] = (
                                        coordenador.nome
                                    )
                                return True
                            else:
                                st.error(
                                    "❌ Coordenador criado, mas não foi possível carregar seus dados."
                                )
                                return False
                        else:
                            st.error("❌ Erro ao criar coordenador.")
                            return False

                except Exception as e:
                    st.error(f"❌ Erro ao criar coordenador: {str(e)}")
                    return False

    return False


def listar_coordenadores():
    """Lista e gerencia coordenadores existentes usando data_editor."""
    st.subheader("👤 Coordenadores Cadastrados")

    # Show success message if it exists in session state
    if "show_success_coordenador_edit" in st.session_state:
        st.success(st.session_state["show_success_coordenador_edit"])
        del st.session_state["show_success_coordenador_edit"]

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_coordenador_repository

            coord_repo = get_coordenador_repository(session)
            coordenadores = coord_repo.get_all(Coordenador)

            if not coordenadores:
                st.info("📋 Nenhum coordenador cadastrado.")
                return

            # Preparar dados para exibição e edição
            dados = []
            for coord in coordenadores:
                dados.append(
                    {
                        "ID": coord.id,
                        "Nome": coord.nome,
                        "Email": coord.email,
                        "Superadmin": coord.is_superadmin,
                    }
                )

            df = pd.DataFrame(dados)
            df = df.sort_values("ID", ascending=True)

            # Instruções de uso
            st.markdown(
                """
                💡 **Dicas de uso:**
                - Edite os valores diretamente nas células (clique duplo)
                - Marque/desmarque a coluna "Superadmin" para alterar permissões
                - Para **deletar**, deixe o campo "Nome" vazio
                - SEMPRE clique em **💾 Salvar Alterações** para confirmar as alterações
                - **ATENÇÃO**: Não é possível alterar a senha por aqui
                """
            )

            # Editor de dados
            edited_df = st.data_editor(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn(
                        "ID",
                        help="ID único do coordenador (somente leitura)",
                        disabled=True,
                    ),
                    "Nome": st.column_config.TextColumn(
                        "Nome",
                        help="Nome completo do coordenador",
                        required=True,
                        max_chars=200,
                    ),
                    "Email": st.column_config.TextColumn(
                        "Email",
                        help="Email para login (deve ser único)",
                        required=True,
                        max_chars=200,
                    ),
                    "Superadmin": st.column_config.CheckboxColumn(
                        "Superadmin",
                        help="Marque se o coordenador deve ter acesso total ao sistema",
                        default=False,
                    ),
                },
                hide_index=True,
                num_rows="fixed",  # Não permitir adicionar linhas (use o formulário de criação)
                key="coordenadores_editor",
            )

            # Botão para salvar alterações
            if st.button(
                "💾 Salvar Alterações", type="primary", key="salvar_coordenadores"
            ):
                salvar_alteracoes_coordenadores(edited_df, coordenadores, coord_repo)

    except Exception as e:
        st.error(f"❌ Erro ao listar coordenadores: {str(e)}")


def salvar_alteracoes_coordenadores(
    edited_df: pd.DataFrame, coordenadores_originais: list, coord_repo
):
    """Salva as alterações feitas no data_editor para coordenadores."""
    try:
        alteracoes = 0
        erros = []

        # Criar dicionário de coordenadores originais por ID
        coordenadores_por_id = {coord.id: coord for coord in coordenadores_originais}

        for _, row in edited_df.iterrows():
            coord_id = row["ID"]
            nome_novo = row["Nome"].strip() if row["Nome"] else ""
            email_novo = row["Email"].strip().lower() if row["Email"] else ""
            is_superadmin_novo = bool(row["Superadmin"])

            # Convert numpy/pandas types to Python types
            if hasattr(coord_id, "item"):
                coord_id = coord_id.item()

            # Skip rows com ID inválido
            if pd.isna(coord_id) or coord_id not in coordenadores_por_id:
                continue

            # Deletar coordenador se Nome estiver vazio
            if not nome_novo:
                coordenador = coordenadores_por_id[coord_id]

                # Verificar se não é o último superadmin
                if coordenador.is_superadmin:
                    superadmins_count = len(coord_repo.get_superadmins())
                    if superadmins_count <= 1:
                        erros.append(
                            f"Não é possível deletar {coordenador.nome}: é o único superadmin do sistema. "
                            "Crie outro superadmin antes de deletar este."
                        )
                        continue

                try:
                    # Se não é superadmin, deletar associações com cidades primeiro
                    if not coordenador.is_superadmin:
                        from app.models import CoordenadorCidadeLink

                        # Deletar todas as associações coordenador-cidade
                        links_existentes = (
                            coord_repo.session.query(CoordenadorCidadeLink)
                            .filter_by(coordenador_id=coordenador.id)
                            .all()
                        )
                        for link in links_existentes:
                            coord_repo.session.delete(link)

                    # Agora deletar o coordenador
                    coord_repo.delete(coordenador)
                    alteracoes += 1
                except Exception as e:
                    erros.append(f"Erro ao deletar {coordenador.nome}: {str(e)}")
                continue

            # Validar email
            if not validar_email(email_novo):
                erros.append(f"Email inválido para {nome_novo}: {email_novo}")
                continue

            # Atualizar coordenador existente
            coordenador = coordenadores_por_id[coord_id]

            # Verificar se houve mudanças
            mudou = False

            if coordenador.nome != nome_novo:
                coordenador.nome = nome_novo
                mudou = True

            if coordenador.email != email_novo:
                # Verificar se email já existe em outro coordenador
                existing = coord_repo.get_by_email(email_novo)
                if existing and existing.id != coord_id:
                    erros.append(
                        f"Email {email_novo} já está em uso por outro coordenador"
                    )
                    continue
                coordenador.email = email_novo
                mudou = True

            # Verificar mudança de permissão de superadmin
            if coordenador.is_superadmin != is_superadmin_novo:
                # Se está tentando remover superadmin, verificar se não é o último
                if coordenador.is_superadmin and not is_superadmin_novo:
                    superadmins_count = len(coord_repo.get_superadmins())
                    if superadmins_count <= 1:
                        erros.append(
                            f"Não é possível remover permissão de superadmin de {coordenador.nome}: "
                            "é o único superadmin do sistema."
                        )
                        continue

                coordenador.is_superadmin = is_superadmin_novo
                mudou = True

            if mudou:
                alteracoes += 1

        if alteracoes > 0:
            # Commit explicitamente
            try:
                coord_repo.session.commit()
                # Store success message in session state to show after rerun
                st.session_state["show_success_coordenador_edit"] = (
                    f"🎉 {alteracoes} alteração(ões) salva(s) com sucesso!"
                )
                st.rerun()
            except Exception as commit_error:
                coord_repo.session.rollback()
                st.error(f"❌ Erro ao salvar no banco de dados: {str(commit_error)}")
                erros.append(f"Erro de commit: {str(commit_error)}")
        elif erros:
            pass  # Erros já foram mostrados
        else:
            st.info("ℹ️ Nenhuma alteração detectada.")

        # Mostrar erros se houver
        if erros:
            with st.expander("⚠️ Erros encontrados"):
                for erro in erros:
                    st.error(erro)

    except Exception as e:
        st.error(f"❌ Erro ao salvar alterações: {str(e)}")


def gerenciar_associacoes_coordenador_cidade():
    """Gerencia as associações entre coordenadores e cidades."""
    st.subheader("🗺️ Associar Coordenadores a Cidades")

    # Mostrar mensagem de sucesso se existir
    if "show_success_associacao" in st.session_state:
        st.success(st.session_state["show_success_associacao"])
        del st.session_state["show_success_associacao"]

    st.markdown(
        """
        💡 **Importante:**
        - Superadmins têm acesso a todas as cidades automaticamente
        - Coordenadores regulares só veem e editam participantes das cidades associadas
        - Use esta seção para definir quais cidades cada coordenador pode gerenciar
        """
    )

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_coordenador_repository, get_cidade_repository
            from app.models import CoordenadorCidadeLink

            # Force session to reload all data from database
            # This ensures we see the latest associations created via modal
            session.expire_all()

            coord_repo = get_coordenador_repository(session)
            cidade_repo = get_cidade_repository(session)

            # Buscar coordenadores não-superadmin
            coordenadores = [
                c for c in coord_repo.get_all(Coordenador) if not c.is_superadmin
            ]
            cidades = cidade_repo.get_all_ordered()

            if not coordenadores:
                st.info("📋 Nenhum coordenador (não-superadmin) cadastrado.")
                return

            if not cidades:
                st.warning("⚠️ Nenhuma cidade cadastrada. Cadastre cidades primeiro.")
                return

            # Criar mapa de cidades por ID
            cidades_map = {c.id: f"{c.nome}-{c.estado}" for c in cidades}

            # Para cada coordenador, mostrar suas cidades associadas
            for coord in coordenadores:
                with st.expander(f"👤 {coord.nome} ({coord.email})", expanded=False):
                    # Buscar cidades já associadas
                    links_existentes = (
                        session.query(CoordenadorCidadeLink)
                        .filter_by(coordenador_id=coord.id)
                        .all()
                    )
                    cidades_atuais_ids = [link.cidade_id for link in links_existentes]

                    # Preparar options e default como tuplas para manter consistência
                    cidades_options = [(c.id, f"{c.nome}-{c.estado}") for c in cidades]
                    cidades_default = [
                        (cid, cidades_map[cid])
                        for cid in cidades_atuais_ids
                        if cid in cidades_map
                    ]

                    # Multiselect com cidades
                    cidades_selecionadas = st.multiselect(
                        "Cidades associadas",
                        options=cidades_options,
                        default=cidades_default,
                        format_func=lambda x: x[1] if isinstance(x, tuple) else str(x),
                        key=f"cidades_coord_{coord.id}",
                        help="Selecione as cidades que este coordenador pode gerenciar",
                    )

                    # Extrair apenas os IDs
                    cidades_ids_selecionados = [
                        c[0] if isinstance(c, tuple) else c
                        for c in cidades_selecionadas
                    ]

                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button(
                            "💾 Salvar",
                            key=f"salvar_cidades_{coord.id}",
                            type="primary",
                        ):
                            try:
                                # Deletar associações antigas
                                for link in links_existentes:
                                    session.delete(link)

                                # Criar novas associações
                                for cidade_id in cidades_ids_selecionados:
                                    novo_link = CoordenadorCidadeLink(
                                        coordenador_id=coord.id, cidade_id=cidade_id
                                    )
                                    session.add(novo_link)

                                session.commit()

                                # Armazenar mensagem de sucesso no session_state
                                st.session_state["show_success_associacao"] = (
                                    f"✅ Associações de {coord.nome} atualizadas com sucesso!"
                                )
                                st.rerun()
                            except Exception as e:
                                session.rollback()
                                st.error(f"❌ Erro ao salvar associações: {str(e)}")

    except Exception as e:
        st.error(f"❌ Erro ao gerenciar associações: {str(e)}")
        logger.error(f"Erro em gerenciar_associacoes_coordenador_cidade: {str(e)}")


def formulario_criar_evento() -> bool:
    """Formulário para criar novo evento."""
    st.subheader("📅 Criar Novo Evento")

    with st.form("form_criar_evento"):
        col1, col2 = st.columns(2)

        with col1:
            ano = st.number_input(
                "Ano do Evento *",
                min_value=2020,
                max_value=2100,
                value=datetime.now().year,
                step=1,
                help="Ano em que o evento ocorrerá",
            )

        with col2:
            datas_evento = st.text_input(
                "Datas do Evento (YYYY-MM-DD) *",
                placeholder="Ex: 2025-05-19, 2025-05-20, 2025-05-21",
                help="Datas no formato YYYY-MM-DD (ISO), separadas por vírgula",
            )

        submit_button = st.form_submit_button(
            "📅 Criar Evento", type="primary", width="stretch"
        )

        if submit_button:
            if not all([ano, datas_evento]):
                st.error("❌ Preencha todos os campos obrigatórios.")
                return False

            # Parse datas_evento - expect ISO format YYYY-MM-DD
            try:
                datas_list = []
                for d in datas_evento.split(","):
                    d = d.strip()
                    if d:
                        # Validate ISO format
                        try:
                            datetime.fromisoformat(d)
                            datas_list.append(d)
                        except ValueError:
                            raise ValueError(f"Data inválida: {d}")
                if not datas_list:
                    raise ValueError("Nenhuma data válida fornecida")
            except Exception as e:
                st.error(
                    f"❌ Formato de datas inválido. Use YYYY-MM-DD separado por vírgula. Erro: {str(e)}"
                )
                return False

            try:
                with db_manager.get_db_session() as session:
                    from app.db import get_evento_repository

                    evento_repo = get_evento_repository(session)

                    # Verificar se evento já existe
                    existing = evento_repo.get_by_ano(ano)
                    if existing:
                        st.error(f"❌ Já existe um evento para o ano {ano}.")
                        return False

                    # Criar evento with parsed list
                    evento = evento_repo.create_evento(ano, datas_list)

                    if evento:
                        # Store success message in session state to show after rerun
                        st.session_state["show_success_evento"] = (
                            f"✅ Evento {ano} criado com sucesso!"
                        )
                        return True
                    else:
                        st.error("❌ Erro ao criar evento.")
                        return False

            except Exception as e:
                st.error(f"❌ Erro ao criar evento: {str(e)}")
                return False

    return False


def listar_eventos():
    """Lista e permite editar eventos existentes usando data_editor."""
    st.subheader("📅 Eventos Cadastrados")

    # Show success message if it exists in session state
    if "show_success_evento_edit" in st.session_state:
        st.success(st.session_state["show_success_evento_edit"])
        del st.session_state["show_success_evento_edit"]

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_evento_repository

            evento_repo = get_evento_repository(session)
            eventos = evento_repo.get_all(Evento)

            if not eventos:
                st.info("📋 Nenhum evento cadastrado.")
                return

            # Preparar dados para exibição e edição
            dados = []
            for evento in eventos:
                # Converter datas_evento (JSON) para string legível
                datas_str = (
                    ", ".join(evento.datas_evento) if evento.datas_evento else ""
                )
                dados.append(
                    {
                        "ID": evento.id,
                        "Ano": evento.ano,
                        "Datas": datas_str,
                        "Data Criação": formatar_data_exibicao(evento.data_criacao),
                    }
                )

            df = pd.DataFrame(dados)
            df = df.sort_values("Ano", ascending=False)

            # Usar data_editor para permitir edição
            st.markdown(
                """
                    💡 **Dicas de uso:**
                    - Edite os valores diretamente nas células (use clique duplo)
                    - Para adicionar novo evento, clique em + (na parte superior-direita da tabela ou na última linha)
                    - Para deletar, deixe o campo Ano vazio (só funciona se não houver participantes)
                    - Clique em **Salvar Alterações** para confirmar
                """
            )

            # Editor de dados
            edited_df = st.data_editor(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn(
                        "ID",
                        help="ID único do evento (somente leitura)",
                        disabled=True,
                    ),
                    "Ano": st.column_config.NumberColumn(
                        "Ano",
                        help="Ano do evento (deve ser único)",
                        min_value=2020,
                        max_value=2100,
                        step=1,
                    ),
                    "Datas": st.column_config.TextColumn(
                        "Datas",
                        help="Datas do evento no formato YYYY-MM-DD, separadas por vírgula",
                    ),
                    "Data Criação": st.column_config.TextColumn(
                        "Data Criação",
                        help="Data de criação (somente leitura)",
                        disabled=True,
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                key="eventos_editor",
            )

            # Botão para salvar alterações
            if st.button("💾 Salvar Alterações", type="primary", key="salvar_eventos"):
                salvar_alteracoes_eventos(edited_df, eventos, evento_repo)

    except Exception as e:
        st.error(f"❌ Erro ao listar eventos: {str(e)}")


def salvar_alteracoes_eventos(
    edited_df: pd.DataFrame, eventos_originais: list, evento_repo
):
    """Salva as alterações feitas no data_editor para eventos."""
    try:
        alteracoes = 0
        erros = []

        # Criar dicionário de eventos originais por ID
        eventos_por_id = {evento.id: evento for evento in eventos_originais}

        for _, row in edited_df.iterrows():
            evento_id = row["ID"]
            ano_novo = row["Ano"]
            datas_str = row["Datas"].strip() if row["Datas"] else ""

            # Convert numpy/pandas types to Python types
            if hasattr(evento_id, "item"):  # numpy type
                evento_id = evento_id.item()
            if hasattr(ano_novo, "item"):  # numpy type
                ano_novo = ano_novo.item()

            # Skip rows that are completely empty or invalid
            if pd.isna(evento_id) and (
                pd.isna(ano_novo) or ano_novo == 0 or ano_novo == ""
            ):
                continue  # Skip empty rows added by data_editor

            # Handle different data types from data_editor
            if pd.isna(ano_novo) or ano_novo == 0 or ano_novo == "":
                # Deletar evento se Ano estiver vazio ou 0
                if not pd.isna(evento_id) and evento_id in eventos_por_id:
                    evento = eventos_por_id[evento_id]

                    # Verificar se há participantes associados ao evento
                    from app.db import get_participante_repository

                    participante_repo = get_participante_repository(evento_repo.session)
                    participantes_associados = participante_repo.get_by_evento_cidade(
                        evento_id
                    )

                    if participantes_associados:
                        erros.append(
                            f"Não é possível deletar o evento {evento.ano} pois há "
                            f"{len(participantes_associados)} participante(s) associado(s). "
                            "Transfira os participantes para outro evento antes de deletar."
                        )
                        continue

                    try:
                        evento_repo.delete(evento)
                        alteracoes += 1
                    except Exception as e:
                        erros.append(f"Erro ao deletar evento {evento.ano}: {str(e)}")
                continue

            # Parse datas
            try:
                if datas_str:
                    datas_list = []
                    for d in datas_str.split(","):
                        d = d.strip()
                        if d:
                            datetime.fromisoformat(d)  # Validar formato
                            datas_list.append(d)
                    if not datas_list:
                        raise ValueError("Nenhuma data válida")
                else:
                    raise ValueError("Datas são obrigatórias")
            except Exception as e:
                erros.append(f"Erro nas datas do evento {ano_novo}: {str(e)}")
                continue

            if not pd.isna(evento_id) and evento_id in eventos_por_id:
                # Atualizar evento existente
                evento = eventos_por_id[evento_id]

                # Verificar se houve mudanças
                mudou = False
                # Convert ano_novo to int safely
                try:
                    ano_int = int(ano_novo)
                except (ValueError, TypeError):
                    erros.append(f"Ano inválido: {ano_novo}")
                    continue

                if evento.ano != ano_int:
                    evento.ano = ano_int
                    mudou = True

                if evento.datas_evento != datas_list:
                    evento.datas_evento = datas_list
                    mudou = True

                if mudou:
                    alteracoes += 1

            # Skip rows that have ID but no valid ano (these might be unmodified existing rows)

        if alteracoes > 0:
            # Commit explicitamente antes do rerun
            try:
                evento_repo.session.commit()
                # Store success message in session state to show after rerun
                st.session_state["show_success_evento_edit"] = (
                    f"🎉 {alteracoes} alteração(ões) salva(s) com sucesso!"
                )
                st.rerun()
            except Exception as commit_error:
                evento_repo.session.rollback()
                st.error(f"❌ Erro ao salvar no banco de dados: {str(commit_error)}")
                erros.append(f"Erro de commit: {str(commit_error)}")
        elif erros:
            pass  # Erros já foram mostrados acima
        else:
            st.info("ℹ️ Nenhuma alteração detectada.")

        # Mostrar erros se houver
        if erros:
            with st.expander("⚠️ Erros encontrados"):
                for erro in erros:
                    st.error(erro)

    except Exception as e:
        st.error(f"❌ Erro ao salvar alterações: {str(e)}")


def formulario_criar_cidade() -> bool:
    """Formulário para criar nova cidade."""
    st.subheader("🏙️ Criar Nova Cidade")

    with st.form("form_criar_cidade"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input(
                "Nome da Cidade *",
                placeholder="Ex: São Paulo",
                help="Nome completo da cidade",
            )

        with col2:
            # Lista de estados brasileiros em ordem alfabética
            estados_brasileiros = [
                "AC",
                "AL",
                "AP",
                "AM",
                "BA",
                "CE",
                "DF",
                "ES",
                "GO",
                "MA",
                "MT",
                "MS",
                "MG",
                "PA",
                "PB",
                "PR",
                "PE",
                "PI",
                "RJ",
                "RN",
                "RS",
                "RO",
                "RR",
                "SC",
                "SP",
                "SE",
                "TO",
            ]

            estado = st.selectbox(
                "Estado (UF) *",
                options=estados_brasileiros,
                help="Selecione o estado brasileiro",
            )

        submit_button = st.form_submit_button(
            "🏙️ Criar Cidade", type="primary", width="stretch"
        )

        if submit_button:
            if not all([nome, estado]):
                st.error("❌ Preencha todos os campos obrigatórios.")
                return False

            try:
                with db_manager.get_db_session() as session:
                    from app.db import get_cidade_repository

                    cidade_repo = get_cidade_repository(session)

                    # Verificar se cidade já existe
                    existing = cidade_repo.get_by_nome_estado(nome, estado)
                    if existing:
                        st.error(f"❌ A cidade {nome}-{estado} já está cadastrada.")
                        return False

                    # Criar cidade
                    cidade = cidade_repo.create_cidade(nome.strip(), estado)

                    if cidade:
                        # Store success message in session state to show after rerun
                        st.session_state["show_success_cidade"] = (
                            f"✅ Cidade {nome}-{estado} criada com sucesso!"
                        )
                        return True
                    else:
                        st.error("❌ Erro ao criar cidade.")
                        return False

            except Exception as e:
                st.error(f"❌ Erro ao criar cidade: {str(e)}")
                return False

    return False


def listar_cidades():
    """Lista cidades existentes."""
    st.subheader("🏙️ Cidades Cadastradas")

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_cidade_repository

            cidade_repo = get_cidade_repository(session)
            cidades = cidade_repo.get_all_ordered()

            if not cidades:
                st.info("📋 Nenhuma cidade cadastrada.")
                return

            # Preparar dados para exibição
            dados = []
            for cidade in cidades:
                dados.append(
                    {
                        "ID": cidade.id,
                        "Nome": cidade.nome,
                        "Estado": cidade.estado,
                        "Completo": f"{cidade.nome}-{cidade.estado}",
                    }
                )

            df = pd.DataFrame(dados)

            # Exibir tabela
            st.dataframe(df, width="stretch")

    except Exception as e:
        st.error(f"❌ Erro ao listar cidades: {str(e)}")


def formulario_criar_funcao() -> bool:
    """Formulário para criar nova função."""
    st.subheader("🎭 Criar Nova Função")

    with st.form("form_criar_funcao"):
        nome_funcao = st.text_input(
            "Nome da Função *",
            placeholder="Ex: Organizador(a)",
            help="Nome da função no evento",
        )

        submit_button = st.form_submit_button(
            "🎭 Criar Função", type="primary", width="stretch"
        )

        if submit_button:
            if not nome_funcao:
                st.error("❌ Preencha o nome da função.")
                return False

            try:
                with db_manager.get_db_session() as session:
                    from app.db import get_funcao_repository

                    funcao_repo = get_funcao_repository(session)

                    # Verificar se função já existe
                    existing = funcao_repo.get_by_name(nome_funcao.strip())
                    if existing:
                        st.error(f"❌ A função '{nome_funcao}' já está cadastrada.")
                        return False

                    # Criar função
                    funcao = funcao_repo.create_funcao(nome_funcao.strip())

                    if funcao:
                        # Store success message in session state to show after rerun
                        st.session_state["show_success_funcao"] = (
                            f"✅ Função '{nome_funcao}' criada com sucesso!"
                        )
                        return True
                    else:
                        st.error("❌ Erro ao criar função.")
                        return False

            except Exception as e:
                st.error(f"❌ Erro ao criar função: {str(e)}")
                return False

    return False


def listar_funcoes():
    """Lista funções existentes."""
    st.subheader("🎭 Funções Cadastradas")

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_funcao_repository

            funcao_repo = get_funcao_repository(session)
            funcoes = funcao_repo.get_all_ordered()

            if not funcoes:
                st.info("📋 Nenhuma função cadastrada.")
                return

            # Preparar dados para exibição
            dados = []
            for funcao in funcoes:
                dados.append({"ID": funcao.id, "Função": funcao.nome_funcao})

            df = pd.DataFrame(dados)

            # Exibir tabela
            st.dataframe(df, width="stretch")

    except Exception as e:
        st.error(f"❌ Erro ao listar funções: {str(e)}")


def carregar_configuracao_certificado(ano: int) -> Dict[str, Any]:
    """
    Carrega configuração do certificado para um ano específico.

    Args:
        ano: Ano do evento

    Returns:
        Dicionário com configuração de cores para o ano
    """
    config_path = Path("static/certificate_config.json")

    # Configuração padrão
    default_config = {
        "cor_primaria": "#e74c3c",  # Laranja/vermelho do Pint of Science
        "cor_secundaria": "#c0392b",  # Tom mais escuro
        "cor_texto": "#2c3e50",  # Cinza escuro para texto
        "cor_destaque": "#f39c12",  # Laranja claro para destaques
    }

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                all_configs = json.load(f)

                ano_key = str(ano)

                # Buscar configuração do ano
                if ano_key in all_configs and "cores" in all_configs[ano_key]:
                    config = all_configs[ano_key]["cores"]
                    # Garantir que todas as chaves existam
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config

                # Fallback para _default
                if "_default" in all_configs and "cores" in all_configs["_default"]:
                    return all_configs["_default"]["cores"]

        # Se não encontrou, retorna padrão
        return default_config

    except Exception as e:
        logger.error(f"Erro ao carregar configuração para ano {ano}: {str(e)}")
        return default_config


def salvar_configuracao_certificado(ano: int, cores: Dict[str, str]) -> bool:
    """
    Salva configuração de cores do certificado para um ano específico.

    Args:
        ano: Ano do evento
        cores: Dicionário com cores

    Returns:
        True se salvou com sucesso
    """
    config_path = Path("static/certificate_config.json")

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Carregar configuração existente
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # Garantir estrutura do ano
        ano_key = str(ano)
        if ano_key not in config:
            config[ano_key] = {"cores": {}, "imagens": {}}

        if "cores" not in config[ano_key]:
            config[ano_key]["cores"] = {}

        # Atualizar cores
        config[ano_key]["cores"] = cores

        # Salvar
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True

    except Exception as e:
        logger.error(f"Erro ao salvar configuração para ano {ano}: {str(e)}")
        return False


def gerenciar_imagens_certificado():
    """Interface para upload e gerenciamento de imagens do certificado por ano."""
    st.subheader("🖼️ Imagens do Certificado")

    st.info(
        """
        📝 **Instruções:**
        - Selecione o ano do evento para configurar
        - Faça upload das imagens que serão usadas nos certificados daquele ano
        - Formatos aceitos: PNG, JPG, WEBP
        - Tamanho máximo: 3MB por arquivo
        - **IMPORTANTE**: Cada ano mantém sua própria configuração visual
        """
    )

    # Buscar eventos disponíveis
    with db_manager.get_db_session() as session:
        from app.db import get_evento_repository

        evento_repo = get_evento_repository(session)
        eventos = session.query(Evento).order_by(Evento.ano.desc()).all()
        # Eagerly load the anos before session closes
        anos_disponiveis = [evento.ano for evento in eventos]

    if not anos_disponiveis:
        st.warning("⚠️ Nenhum evento cadastrado. Crie um evento primeiro.")
        return

    # Seletor de ano
    ano_selecionado = st.selectbox(
        "📅 Selecione o ano do evento:",
        options=anos_disponiveis,
        index=0,
        help="Configurações de imagens são isoladas por ano do evento",
    )

    static_path = Path("static") / str(ano_selecionado)
    static_path.mkdir(parents=True, exist_ok=True)

    st.markdown(f"### Configurando imagens para o evento de **{ano_selecionado}**")
    st.caption(f"📁 As imagens serão salvas em: `static/{ano_selecionado}/`")

    st.markdown("---")

    # Upload das 3 imagens
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🏷️ Logo Pint of Science")
        st.caption("Logo principal (canto superior direito)")

        pint_logo_file = st.file_uploader(
            "Upload Logo Pint",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"pint_logo_upload_{ano_selecionado}",
            help="Logo do Pint of Science (recomendado: fundo transparente)",
        )

        if pint_logo_file:
            # Validar tamanho
            if pint_logo_file.size > 3 * 1024 * 1024:  # 3MB
                st.error("❌ Arquivo muito grande! Máximo: 3MB")
            else:
                try:
                    # Salvar arquivo
                    logo_path = static_path / "pint_logo.png"
                    with open(logo_path, "wb") as f:
                        f.write(pint_logo_file.getbuffer())
                    st.success(f"✅ Logo salvo! ({pint_logo_file.size / 1024:.1f} KB)")

                    # Atualizar configuração JSON
                    _atualizar_config_imagens(
                        ano_selecionado, "pint_logo", f"{ano_selecionado}/pint_logo.png"
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")

        # Mostrar status
        if (static_path / "pint_logo.png").exists():
            st.success("✓ Logo disponível")
        else:
            st.warning("⚠️ Logo não encontrado")

    with col2:
        st.markdown("#### ✍️ Assinatura")
        st.caption("Assinatura do responsável (parte inferior)")

        signature_file = st.file_uploader(
            "Upload Assinatura",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"signature_upload_{ano_selecionado}",
            help="Assinatura digital do coordenador geral",
        )

        if signature_file:
            if signature_file.size > 3 * 1024 * 1024:
                st.error("❌ Arquivo muito grande! Máximo: 3MB")
            else:
                try:
                    sig_path = static_path / "pint_signature.png"
                    with open(sig_path, "wb") as f:
                        f.write(signature_file.getbuffer())
                    st.success(
                        f"✅ Assinatura salva! ({signature_file.size / 1024:.1f} KB)"
                    )

                    # Atualizar configuração JSON
                    _atualizar_config_imagens(
                        ano_selecionado,
                        "pint_signature",
                        f"{ano_selecionado}/pint_signature.png",
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")

        if (static_path / "pint_signature.png").exists():
            st.success("✓ Assinatura disponível")
        else:
            st.warning("⚠️ Assinatura não encontrada")

    with col3:
        st.markdown("#### 🏢 Logo Patrocinador")
        st.caption("Logo do(s) patrocinador(es) (coluna lateral)")

        sponsor_file = st.file_uploader(
            "Upload Logo Patrocinador",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"sponsor_upload_{ano_selecionado}",
            help="Logo único ou composição com todos os patrocinadores",
        )

        if sponsor_file:
            if sponsor_file.size > 3 * 1024 * 1024:
                st.error("❌ Arquivo muito grande! Máximo: 3MB")
            else:
                try:
                    sponsor_path = static_path / "sponsor_logo.png"
                    with open(sponsor_path, "wb") as f:
                        f.write(sponsor_file.getbuffer())
                    st.success(f"✅ Logo salvo! ({sponsor_file.size / 1024:.1f} KB)")

                    # Atualizar configuração JSON
                    _atualizar_config_imagens(
                        ano_selecionado,
                        "sponsor_logo",
                        f"{ano_selecionado}/sponsor_logo.png",
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")

        if (static_path / "sponsor_logo.png").exists():
            st.success("✓ Logo disponível")
        else:
            st.warning("⚠️ Logo não encontrado")

    # Aviso importante
    st.markdown("---")
    st.info(
        f"💡 **Dica**: As imagens configuradas para {ano_selecionado} serão usadas "
        f"em todos os certificados gerados para esse ano, garantindo consistência visual "
        f"mesmo se você criar certificados no futuro para eventos passados."
    )


def _atualizar_config_imagens(ano: int, chave_imagem: str, caminho_relativo: str):
    """
    Atualiza a configuração de imagens no JSON para um ano específico.

    Args:
        ano: Ano do evento
        chave_imagem: 'pint_logo', 'pint_signature' ou 'sponsor_logo'
        caminho_relativo: Caminho relativo à pasta static/
    """
    config_path = Path("static/certificate_config.json")

    try:
        # Carregar configuração existente
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # Garantir estrutura do ano
        ano_key = str(ano)
        if ano_key not in config:
            config[ano_key] = {
                "cores": {
                    "cor_primaria": "#e74c3c",
                    "cor_secundaria": "#c0392b",
                    "cor_texto": "#2c3e50",
                    "cor_destaque": "#f39c12",
                },
                "imagens": {},
            }

        if "imagens" not in config[ano_key]:
            config[ano_key]["imagens"] = {}

        # Atualizar caminho da imagem
        config[ano_key]["imagens"][chave_imagem] = caminho_relativo

        # Salvar configuração
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Erro ao atualizar config de imagens: {e}")


def configurar_cores_certificado():
    """Interface para configuração de cores do certificado por ano."""
    st.subheader("🎨 Cores do Certificado")

    st.info(
        """
        🎨 **Personalize as cores:**
        - Selecione o ano do evento para configurar
        - Escolha as cores que serão usadas no design do certificado
        - **IMPORTANTE**: Cada ano mantém sua própria paleta de cores
        """
    )

    # Buscar eventos disponíveis
    with db_manager.get_db_session() as session:
        from app.db import get_evento_repository

        evento_repo = get_evento_repository(session)
        eventos = session.query(Evento).order_by(Evento.ano.desc()).all()
        # Eagerly load the anos before session closes
        anos_disponiveis = [evento.ano for evento in eventos]

    if not anos_disponiveis:
        st.warning("⚠️ Nenhum evento cadastrado. Crie um evento primeiro.")
        return

    # Seletor de ano
    ano_selecionado = st.selectbox(
        "📅 Selecione o ano do evento:",
        options=anos_disponiveis,
        index=0,
        key="ano_cores_certificado",
        help="Configurações de cores são isoladas por ano do evento",
    )

    st.markdown(f"### Configurando cores para o evento de **{ano_selecionado}**")
    st.markdown("---")

    # Carregar configuração atual do ano
    config = carregar_configuracao_certificado(ano_selecionado)

    col1, col2 = st.columns(2)

    with col1:
        cor_primaria = st.color_picker(
            "Cor Primária (Barra Lateral)",
            value=config.get("cor_primaria", "#e74c3c"),
            help="Cor principal usada na barra lateral do certificado",
            key=f"cor_primaria_{ano_selecionado}",
        )

        cor_secundaria = st.color_picker(
            "Cor Secundária (Título)",
            value=config.get("cor_secundaria", "#c0392b"),
            help="Cor usada no título do certificado",
            key=f"cor_secundaria_{ano_selecionado}",
        )

    with col2:
        cor_texto = st.color_picker(
            "Cor do Texto Principal",
            value=config.get("cor_texto", "#2c3e50"),
            help="Cor do texto principal do certificado",
            key=f"cor_texto_{ano_selecionado}",
        )

        cor_destaque = st.color_picker(
            "Cor de Destaque (Nome/Cidade)",
            value=config.get("cor_destaque", "#f39c12"),
            help="Cor para destacar informações importantes (nome, cidade, etc.)",
            key=f"cor_destaque_{ano_selecionado}",
        )

    # Preview das cores
    st.markdown("---")
    st.markdown("#### 👁️ Visualização das Cores")

    preview_cols = st.columns(4)
    with preview_cols[0]:
        st.markdown(
            f'<div style="background-color: {cor_primaria}; padding: 20px; border-radius: 5px; text-align: center; color: white;"><b>Primária</b><br>{cor_primaria}</div>',
            unsafe_allow_html=True,
        )
    with preview_cols[1]:
        st.markdown(
            f'<div style="background-color: {cor_secundaria}; padding: 20px; border-radius: 5px; text-align: center; color: white;"><b>Secundária</b><br>{cor_secundaria}</div>',
            unsafe_allow_html=True,
        )
    with preview_cols[2]:
        st.markdown(
            f'<div style="background-color: {cor_texto}; padding: 20px; border-radius: 5px; text-align: center; color: white;"><b>Texto</b><br>{cor_texto}</div>',
            unsafe_allow_html=True,
        )
    with preview_cols[3]:
        st.markdown(
            f'<div style="background-color: {cor_destaque}; padding: 20px; border-radius: 5px; text-align: center; color: white;"><b>Destaque</b><br>{cor_destaque}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Botão para salvar
    if st.button(
        f"💾 Salvar Configuração de Cores para {ano_selecionado}",
        type="primary",
        width="stretch",
    ):
        nova_config = {
            "cor_primaria": cor_primaria,
            "cor_secundaria": cor_secundaria,
            "cor_texto": cor_texto,
            "cor_destaque": cor_destaque,
        }

        if salvar_configuracao_certificado(ano_selecionado, nova_config):
            st.success(
                f"✅ Configuração de cores salva com sucesso para o evento de {ano_selecionado}!"
            )
            st.balloons()
        else:
            st.error("❌ Erro ao salvar configuração.")

    # Aviso importante
    st.info(
        f"💡 **Dica**: As cores configuradas para {ano_selecionado} serão usadas "
        f"em todos os certificados gerados para esse ano, garantindo consistência visual "
        f"mesmo se você gerar certificados no futuro para eventos passados."
    )


def main():
    """Função principal da página."""

    # Cabeçalho
    st.markdown(
        """
    <div class="header-admin">
        <h1>⚙️ Administração do Sistema</h1>
        <p>Área exclusiva para Superadmins</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Informações do usuário
    mostrar_informacoes_usuario()

    # Estatísticas gerais
    st.markdown("---")
    st.subheader("📊 Estatísticas Gerais")
    mostrar_estatisticas_gerais()

    # Abas para organizar o conteúdo
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["👤 Coordenadores", "📅 Eventos", "🏙️ Cidades", "🎭 Funções", "🖼️ Certificado"]
    )

    with tab1:
        st.markdown("---")

        # Show success message if it exists in session state
        if "show_success_coordenador" in st.session_state:
            st.success(st.session_state["show_success_coordenador"])
            del st.session_state["show_success_coordenador"]

        # Show success message from modal association
        if "show_success_associacao_modal" in st.session_state:
            st.success(st.session_state["show_success_associacao_modal"])
            del st.session_state["show_success_associacao_modal"]

        # Formulário de criação
        if formulario_criar_coordenador():
            st.rerun()

        # Show modal for city association if needed
        if st.session_state.get("show_modal_associacao", False):
            modal_associar_cidades_coordenador(
                st.session_state.get("modal_coord_id"),
                st.session_state.get("modal_coord_nome", "Coordenador"),
            )

        st.markdown("---")
        # Lista de coordenadores
        listar_coordenadores()

        st.markdown("---")
        # Associações coordenador-cidade
        gerenciar_associacoes_coordenador_cidade()

    with tab2:
        st.markdown("---")

        # Show success message if it exists in session state
        if "show_success_evento" in st.session_state:
            st.success(st.session_state["show_success_evento"])
            del st.session_state["show_success_evento"]

        # Formulário de criação
        if formulario_criar_evento():
            st.rerun()

        st.markdown("---")
        # Lista de eventos
        listar_eventos()

    with tab3:
        st.markdown("---")

        # Show success message if it exists in session state
        if "show_success_cidade" in st.session_state:
            st.success(st.session_state["show_success_cidade"])
            del st.session_state["show_success_cidade"]

        # Formulário de criação
        if formulario_criar_cidade():
            st.rerun()

        st.markdown("---")
        # Lista de cidades
        listar_cidades()

    with tab4:
        st.markdown("---")

        # Show success message if it exists in session state
        if "show_success_funcao" in st.session_state:
            st.success(st.session_state["show_success_funcao"])
            del st.session_state["show_success_funcao"]

        # Formulário de criação
        if formulario_criar_funcao():
            st.rerun()

        st.markdown("---")
        # Lista de funções
        listar_funcoes()

    with tab5:
        st.markdown("---")
        # Gerenciamento de imagens
        gerenciar_imagens_certificado()

        st.markdown("---")
        # Configuração de cores
        configurar_cores_certificado()

    # Rodapé
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><em>Use esta área para gerenciar todos os aspectos do sistema.</em></p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
