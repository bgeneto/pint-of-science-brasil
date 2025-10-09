"""
Página Administrativa - Superadmin

Esta página permite que superadmins gerenciem todo o sistema:
- CRUD de coordenadores
- CRUD de eventos
- CRUD de cidades
- CRUD de funções
- Visualização de auditoria
- Gestão geral do sistema
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# Importar módulos do sistema
from app.auth import require_superadmin, get_current_user_info
from app.db import db_manager
from app.models import Evento, Cidade, Funcao, Coordenador, Auditoria
from app.auth import criar_coordenador, alterar_senha_coordenador
from app.utils import formatar_data_exibicao, limpar_texto, validar_email

# Configuração da página
st.set_page_config(page_title="Administração", page_icon="⚙️", layout="wide")

# Proteção de acesso
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
                get_auditoria_repository,
            )

            evento_repo = get_evento_repository(session)
            cidade_repo = get_cidade_repository(session)
            funcao_repo = get_funcao_repository(session)
            coord_repo = get_coordenador_repository(session)
            participante_repo = get_participante_repository(session)
            auditoria_repo = get_auditoria_repository(session)

            # Contar registros
            eventos_count = len(evento_repo.get_all(Evento))
            cidades_count = len(cidade_repo.get_all_ordered())
            funcoes_count = len(funcao_repo.get_all_ordered())
            coordenadores_count = len(coord_repo.get_all(Coordenador))
            participantes_count = len(participante_repo.get_all(Participante))
            auditoria_count = len(auditoria_repo.get_recent_logs(1000))

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
            help="Marque se este usuário deve ter acesso total ao sistema",
        )

        submit_button = st.form_submit_button(
            "👤 Criar Coordenador", type="primary", use_container_width=True
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
            st.dataframe(df, use_container_width=True)

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
                "Datas do Evento *",
                placeholder="Ex: 2024-05-13, 2024-05-14, 2024-05-15",
                help="Datas no formato YYYY-MM-DD (ISO), separadas por vírgula",
            )

        submit_button = st.form_submit_button(
            "📅 Criar Evento", type="primary", use_container_width=True
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
    """Lista eventos existentes."""
    st.subheader("📅 Eventos Cadastrados")

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_evento_repository

            evento_repo = get_evento_repository(session)
            eventos = evento_repo.get_all(Evento)

            if not eventos:
                st.info("📋 Nenhum evento cadastrado.")
                return

            # Preparar dados para exibição
            dados = []
            for evento in eventos:
                dados.append(
                    {
                        "ID": evento.id,
                        "Ano": evento.ano,
                        "Datas": evento.datas_evento,
                        "Data Criação": formatar_data_exibicao(evento.data_criacao),
                    }
                )

            df = pd.DataFrame(dados)
            df = df.sort_values("Ano", ascending=False)

            # Exibir tabela
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro ao listar eventos: {str(e)}")


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
            estado = st.text_input(
                "Estado (UF) *",
                placeholder="Ex: SP",
                max_length=2,
                help="Sigla do estado com 2 letras",
            )

        submit_button = st.form_submit_button(
            "🏙️ Criar Cidade", type="primary", use_container_width=True
        )

        if submit_button:
            if not all([nome, estado]):
                st.error("❌ Preencha todos os campos obrigatórios.")
                return False

            if len(estado) != 2 or not estado.isalpha():
                st.error("❌ Estado deve ter exatamente 2 letras.")
                return False

            try:
                with db_manager.get_db_session() as session:
                    from app.db import get_cidade_repository

                    cidade_repo = get_cidade_repository(session)

                    # Verificar se cidade já existe
                    existing = cidade_repo.get_by_nome_estado(nome, estado.upper())
                    if existing:
                        st.error(
                            f"❌ A cidade {nome}-{estado.upper()} já está cadastrada."
                        )
                        return False

                    # Criar cidade
                    cidade = cidade_repo.create_cidade(nome.strip(), estado.upper())

                    if cidade:
                        st.success(
                            f"✅ Cidade {nome}-{estado.upper()} criada com sucesso!"
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
            st.dataframe(df, use_container_width=True)

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
            "🎭 Criar Função", type="primary", use_container_width=True
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
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro ao listar funções: {str(e)}")


def mostrar_auditoria():
    """Exibe logs de auditoria recentes."""
    st.subheader("📊 Logs de Auditoria")

    try:
        with db_manager.get_db_session() as session:
            from app.db import get_auditoria_repository, get_coordenador_repository

            auditoria_repo = get_auditoria_repository(session)
            coord_repo = get_coordenador_repository(session)

            # Obter logs recentes
            logs = auditoria_repo.get_recent_logs(50)

            if not logs:
                st.info("📋 Nenhum log de auditoria encontrado.")
                return

            # Preparar dados para exibição
            dados = []
            for log in logs:
                coordenador = coord_repo.get_by_id(Coordenador, log.coordenador_id)
                coord_nome = (
                    coordenador.nome if coordenador else f"ID {log.coordenador_id}"
                )

                dados.append(
                    {
                        "ID": log.id,
                        "Coordenador": coord_nome,
                        "Ação": log.acao,
                        "Detalhes": log.detalhes or "-",
                        "Timestamp": formatar_data_exibicao(log.timestamp),
                    }
                )

            df = pd.DataFrame(dados)

            # Exibir tabela
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro ao carregar auditoria: {str(e)}")


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
        ["👤 Coordenadores", "📅 Eventos", "🏙️ Cidades", "🎭 Funções", "📊 Auditoria"]
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

    with tab5:
        st.markdown("---")
        # Logs de auditoria
        mostrar_auditoria()

    # Rodapé
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><em>Use esta área para gerenciar todos os aspectos do sistema.</em></p>
        <p><strong>Atenção:</strong> Todas as ações são registradas na auditoria do sistema.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
