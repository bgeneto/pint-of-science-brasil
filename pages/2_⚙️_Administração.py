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
        col1, col2 = st.columns([3, 1])

        with col1:
            st.info(
                f"👤 **Superadmin:** {user_info['name']} ({user_info['email']})  \n"
                f"⏰ **Login:** {formatar_data_exibicao(user_info.get('login_time', ''))}  \n"
                f"🔐 **Acesso:** Total (Superadmin)"
            )

        with col2:
            # Get current token for navigation
            current_token = st.query_params.get(
                "session_token"
            ) or st.session_state.get("persistent_session_token")
            if current_token:
                validation_url = (
                    f"pages/1_👨‍👨‍👦‍👦_Participantes.py?session_token={current_token}"
                )
                st.markdown(
                    f"""
                <a href="{validation_url}" target="_self" style="
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background: #27ae60;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    text-align: center;
                    margin-top: 1rem;
                ">✅ Validação</a>
                """,
                    unsafe_allow_html=True,
                )
            else:
                if st.button("✅ Validação", type="secondary"):
                    st.switch_page("pages/1_👨‍👨‍👦‍👦_Participantes.py")


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

        is_superadmin = st.checkbox(
            "É Superadmin?",
            help="Marque se este usuário deve ter acesso total ao sistema, permitindo gerenciar outros coordenadores e configurações do sistema.",
        )

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
                    sucesso = criar_coordenador(
                        nome=limpar_texto(nome),
                        email=limpar_texto(email).lower(),
                        senha=senha,
                        is_superadmin=is_superadmin,
                    )

                    if sucesso:
                        st.success("✅ Coordenador criado com sucesso!")
                        return True
                    else:
                        st.error("❌ Erro ao criar coordenador.")
                        return False

                except Exception as e:
                    st.error(f"❌ Erro ao criar coordenador: {str(e)}")
                    return False

    return False


def listar_coordenadores():
    """Lista e gerencia coordenadores existentes."""
    st.subheader("👤 Coordenadores Cadastrados")

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_coordenador_repository

            coord_repo = get_coordenador_repository(session)
            coordenadores = coord_repo.get_all(Coordenador)

            if not coordenadores:
                st.info("📋 Nenhum coordenador cadastrado.")
                return

            # Preparar dados para exibição
            dados = []
            for coord in coordenadores:
                dados.append(
                    {
                        "ID": coord.id,
                        "Nome": coord.nome,
                        "Email": coord.email,
                        "Tipo": "Superadmin" if coord.is_superadmin else "Coordenador",
                        "Data Cadastro": formatar_data_exibicao(
                            str(datetime.now())
                        ),  # Ajustar quando tiver data de cadastro
                    }
                )

            df = pd.DataFrame(dados)

            # Exibir tabela
            st.dataframe(df, width="stretch")

    except Exception as e:
        st.error(f"❌ Erro ao listar coordenadores: {str(e)}")


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
                placeholder="Ex: 2024-05-13, 2024-05-14, 2024-05-15",
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
                        st.success(f"✅ Evento {ano} criado com sucesso!")
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
                    - Para adicionar novo evento, clique em + (na parte superior-direita da tabela)
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
            if st.button("💾 Salvar Alterações", type="primary"):
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
                        st.success(f"✅ Evento {evento.ano} deletado com sucesso!")
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
                    st.success(f"✅ Evento {ano_int} atualizado com sucesso!")

            # Skip rows that have ID but no valid ano (these might be unmodified existing rows)

        if alteracoes > 0:
            # Commit explicitamente antes do rerun
            try:
                evento_repo.session.commit()
                st.success(f"🎉 {alteracoes} alteração(ões) salva(s) com sucesso!")
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
                        st.success(f"✅ Cidade {nome}-{estado} criada com sucesso!")
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
                        st.success(f"✅ Função '{nome_funcao}' criada com sucesso!")
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
    tab1, tab2, tab3, tab4 = st.tabs(
        ["👤 Coordenadores", "📅 Eventos", "🏙️ Cidades", "🎭 Funções"]
    )

    with tab1:
        st.markdown("---")
        # Formulário de criação
        if formulario_criar_coordenador():
            st.rerun()

        st.markdown("---")
        # Lista de coordenadores
        listar_coordenadores()

    with tab2:
        st.markdown("---")
        # Formulário de criação
        if formulario_criar_evento():
            st.rerun()

        st.markdown("---")
        # Lista de eventos
        listar_eventos()

    with tab3:
        st.markdown("---")
        # Formulário de criação
        if formulario_criar_cidade():
            st.rerun()

        st.markdown("---")
        # Lista de cidades
        listar_cidades()

    with tab4:
        st.markdown("---")
        # Formulário de criação
        if formulario_criar_funcao():
            st.rerun()

        st.markdown("---")
        # Lista de funções
        listar_funcoes()

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
