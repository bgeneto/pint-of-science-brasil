"""
Página de Validação de Participantes - Coordenadores

Esta página permite que coordenadores validem as inscrições dos participantes,
visualizem dados e gerenciem o status de validação.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# Importar módulos do sistema
from app.auth import require_login, get_current_user_info
from app.db import db_manager
from app.models import Evento, Cidade, Funcao, Participante
from app.services import servico_criptografia, validar_participantes
from app.utils import formatar_data_exibicao, limpar_texto

# Configuração da página
st.set_page_config(
    page_title="Validação de Participantes", page_icon="✅", layout="wide"
)

# Proteção de acesso
require_login()

# CSS customizado
st.markdown(
    """
<style>
    .header-validation {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #27ae60;
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
            f"👤 **Usuário:** {user_info['name']} ({user_info['email']})  \n"
            f"🔐 **Tipo:** {'Superadmin' if user_info['is_superadmin'] else 'Coordenador'}  \n"
            f"⏰ **Login:** {formatar_data_exibicao(user_info.get('login_time', ''))}"
        )


def carregar_dados_validacao() -> tuple:
    """Carrega dados necessários para a validação."""
    try:
        with db_manager.get_db_session() as session:
            from app.db import (
                get_evento_repository,
                get_cidade_repository,
                get_funcao_repository,
                get_participante_repository,
            )

            evento_repo = get_evento_repository(session)
            cidade_repo = get_cidade_repository(session)
            funcao_repo = get_funcao_repository(session)
            participante_repo = get_participante_repository(session)

            # Buscar evento atual
            evento_atual = evento_repo.get_current_event()

            # Buscar cidades e funções
            cidades = {c.id: c for c in cidade_repo.get_all_ordered()}
            funcoes = {f.id: f for f in funcao_repo.get_all_ordered()}

            # Buscar participantes
            if evento_atual:
                participantes = participante_repo.get_by_evento_cidade(evento_atual.id)
            else:
                participantes = []

            return evento_atual, cidades, funcoes, participantes

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None, {}, {}, []


def preparar_dataframe_participantes(
    participantes: List[Participante],
    cidades: Dict[int, Cidade],
    funcoes: Dict[int, Funcao],
) -> pd.DataFrame:
    """Prepara um DataFrame com os dados dos participantes para exibição."""

    dados = []

    for participante in participantes:
        try:
            # Descriptografar dados sensíveis
            nome = servico_criptografia.descriptografar(
                participante.nome_completo_encrypted
            )
            email = servico_criptografia.descriptografar(participante.email_encrypted)

            # Obter informações relacionadas
            cidade = cidades.get(participante.cidade_id)
            funcao = funcoes.get(participante.funcao_id)

            # Preparar dados da linha
            linha = {
                "ID": participante.id,
                "Nome": nome,
                "Email": email,
                "Cidade": f"{cidade.nome}-{cidade.estado}" if cidade else "N/A",
                "Função": funcao.nome_funcao if funcao else "N/A",
                "Título Apresentação": participante.titulo_apresentacao or "-",
                "Datas Participação": participante.datas_participacao,
                "Carga Horária": f"{participante.carga_horaria_calculada}h",
                "Validado": participante.validado,
                "Data Inscrição": formatar_data_exibicao(participante.data_inscricao),
            }

            dados.append(linha)

        except Exception as e:
            st.warning(f"Erro ao processar participante {participante.id}: {str(e)}")
            continue

    # Criar DataFrame
    if dados:
        df = pd.DataFrame(dados)

        # Reordenar colunas
        colunas_ordenadas = [
            "ID",
            "Nome",
            "Email",
            "Cidade",
            "Função",
            "Título Apresentação",
            "Datas Participação",
            "Carga Horária",
            "Validado",
            "Data Inscrição",
        ]
        df = df[colunas_ordenadas]

        return df
    else:
        return pd.DataFrame()


def mostrar_estatisticas(participantes: List[Participante]) -> None:
    """Exibe estatísticas sobre os participantes."""

    total = len(participantes)
    validados = sum(1 for p in participantes if p.validado)
    pendentes = total - validados

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
        <div class="stats-card">
            <h3 style="color: #2c3e50; margin: 0;">{total}</h3>
            <p style="color: #7f8c8d; margin: 0;">Total de Participantes</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="stats-card">
            <h3 style="color: #27ae60; margin: 0;">{validados}</h3>
            <p style="color: #7f8c8d; margin: 0;">Participantes Validados</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="stats-card">
            <h3 style="color: #f39c12; margin: 0;">{pendentes}</h3>
            <p style="color: #7f8c8d; margin: 0;">Pendentes de Validação</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def tabela_validacao_participantes(
    df_participantes: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    """Exibe tabela editável para validação de participantes."""

    if df_participantes.empty:
        st.info("📋 Nenhum participante encontrado para este evento.")
        return None

    st.subheader("📋 Validação de Participantes")
    st.write("Marque os participantes que deseja validar:")

    # Preparar DataFrame para edição
    df_editavel = df_participantes.copy()

    # Adicionar coluna de seleção
    df_editavel["Selecionado"] = False

    # Formatar coluna Validado para exibição
    df_editavel["Status"] = df_editavel["Validado"].apply(
        lambda x: "✅ Validado" if x else "⏳ Pendente"
    )

    # Colunas para exibição na tabela
    colunas_exibicao = [
        "Selecionado",
        "Nome",
        "Email",
        "Cidade",
        "Função",
        "Carga Horária",
        "Status",
        "Data Inscrição",
    ]

    # Editar apenas colunas selecionadas
    df_para_editor = df_editavel[colunas_exibicao].copy()

    # Data editor com configurações
    edited_df = st.data_editor(
        df_para_editor,
        column_config={
            "Selecionado": st.column_config.CheckboxColumn(
                "Validar", help="Marque para validar este participante"
            ),
            "Nome": st.column_config.TextColumn("Nome", width="large", disabled=True),
            "Email": st.column_config.TextColumn("Email", width="large", disabled=True),
            "Cidade": st.column_config.TextColumn(
                "Cidade", width="medium", disabled=True
            ),
            "Função": st.column_config.TextColumn(
                "Função", width="medium", disabled=True
            ),
            "Carga Horária": st.column_config.TextColumn(
                "Carga Horária", width="small", disabled=True
            ),
            "Status": st.column_config.TextColumn(
                "Status", width="medium", disabled=True
            ),
            "Data Inscrição": st.column_config.TextColumn(
                "Data Inscrição", width="medium", disabled=True
            ),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
    )

    return edited_df


def processar_validacao(df_original: pd.DataFrame, df_editado: pd.DataFrame) -> bool:
    """Processa a validação dos participantes selecionados."""

    # Identificar participantes que foram marcados
    selecionados = df_editado[df_editado["Selecionado"] == True]

    if selecionados.empty:
        st.warning("⚠️ Nenhum participante selecionado para validação.")
        return False

    # Obter IDs dos participantes selecionados
    ids_selecionados = selecionados.index.tolist()

    # Mapear para IDs originais
    ids_originais = df_original.loc[ids_selecionados, "ID"].tolist()

    # Preparar listas para validação
    participante_ids = ids_originais
    novos_status = [True] * len(participante_ids)  # Todos serão validados

    # Confirmar ação
    st.warning(f"⚠️ Você está prestes a validar {len(participante_ids)} participantes.")

    if st.button("✅ Confirmar Validação", type="primary", use_container_width=True):
        with st.spinner("Processando validações..."):
            sucesso, mensagem = validar_participantes(participante_ids, novos_status)

        if sucesso:
            st.success(f"🎉 {mensagem}")
            return True
        else:
            st.error(f"❌ {mensagem}")
            return False

    return False


def mostrar_filtros(df_participantes: pd.DataFrame) -> pd.DataFrame:
    """Exibe filtros para os participantes."""

    st.subheader("🔍 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtro por status
        status_filter = st.selectbox(
            "Status",
            options=["Todos", "Pendentes", "Validados"],
            help="Filtrar por status de validação",
        )

    with col2:
        # Filtro por cidade
        cidades_disponiveis = ["Todas"] + sorted(
            df_participantes["Cidade"].unique().tolist()
        )
        cidade_filter = st.selectbox(
            "Cidade", options=cidades_disponiveis, help="Filtrar por cidade"
        )

    with col3:
        # Filtro por função
        funcoes_disponiveis = ["Todas"] + sorted(
            df_participantes["Função"].unique().tolist()
        )
        funcao_filter = st.selectbox(
            "Função", options=funcoes_disponiveis, help="Filtrar por função"
        )

    # Aplicar filtros
    df_filtrado = df_participantes.copy()

    if status_filter != "Todos":
        if status_filter == "Validados":
            df_filtrado = df_filtrado[df_filtrado["Validado"] == True]
        else:
            df_filtrado = df_filtrado[df_filtrado["Validado"] == False]

    if cidade_filter != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Cidade"] == cidade_filter]

    if funcao_filter != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Função"] == funcao_filter]

    return df_filtrado


def main():
    """Função principal da página."""

    # Cabeçalho
    st.markdown(
        """
    <div class="header-validation">
        <h1>✅ Validação de Participantes</h1>
        <p>Área exclusiva para coordenadores validarem inscrições</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Informações do usuário
    mostrar_informacoes_usuario()

    # Carregar dados
    evento_atual, cidades, funcoes, participantes = carregar_dados_validacao()

    if not evento_atual:
        st.error("❌ Nenhum evento encontrado. Contate o administrador.")
        return

    # Informações do evento
    st.info(
        f"🎯 **Evento:** Pint of Science {evento_atual.ano} ({evento_atual.datas_evento})"
    )

    # Preparar DataFrame
    df_participantes = preparar_dataframe_participantes(participantes, cidades, funcoes)

    if df_participantes.empty:
        st.warning("⚠️ Nenhum participante encontrado para este evento.")
        return

    # Estatísticas
    mostrar_estatisticas(participantes)

    st.markdown("---")

    # Filtros
    df_filtrado = mostrar_filtros(df_participantes)

    st.markdown("---")

    # Tabela de validação
    df_editado = tabela_validacao_participantes(df_filtrado)

    if df_editado is not None:
        # Processar validação
        if processar_validacao(df_filtrado, df_editado):
            st.rerun()

    # Rodapé
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><em>Use os filtros acima para refinar sua busca e marque os participantes para validação.</em></p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
