"""
Página de Validação de Participação - Coordenadores

Esta página permite que coordenadores validem as inscrições dos participantes,
visualizem dados e gerenciem o status de validação.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import time
from sqlalchemy.exc import IntegrityError

# Importar módulos do sistema
from app.auth import require_login, get_current_user_info, auth_manager, SESSION_KEYS
from app.core import settings
from app.db import db_manager
from app.models import Evento, Cidade, Funcao, Participante
from app.services import (
    servico_criptografia,
    validar_participantes,
    servico_calculo_carga_horaria,
)
from app.utils import formatar_data_exibicao, validar_email

# Configure logging
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title=f"Participantes - {settings.app_name}",
    page_icon="👨‍👨‍👦‍👦",
    layout="wide",
)

# CRITICAL: Check authentication cookie BEFORE require_login
# This restores the session from cookie if it exists
try:
    if auth_manager.authenticator:
        name, authentication_status, username = auth_manager.authenticator.login(
            location="unrendered"
        )
        if authentication_status and username and not st.session_state.get("logged_in"):
            auth_manager.handle_login_result(name, authentication_status, username)
except Exception:
    pass  # Will be caught by require_login below

# Proteção de acesso - agora é simples!
require_login()

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


def normalizar_valor_editor(val: Any) -> str:
    """Normaliza valores do data_editor para comparação e validação."""
    if pd.isna(val) or val is None:
        return ""

    s = str(val).strip()
    if s in ["-", "nan", "None", "N/A"]:
        return ""
    return s


def validar_campos_obrigatorios_participante(
    participante_id: Any,
    *,
    nome: Any,
    email: Any,
    cidade: Any,
    funcao: Any,
    datas_participacao: Any,
    validar_datas_br: bool,
) -> List[str]:
    """Valida campos obrigatórios antes de qualquer alteração persistente."""
    prefixo = f"Participante ID {participante_id}"
    erros = []

    nome_normalizado = normalizar_valor_editor(nome)
    email_normalizado = normalizar_valor_editor(email)
    cidade_normalizada = normalizar_valor_editor(cidade)
    funcao_normalizada = normalizar_valor_editor(funcao)
    datas_normalizadas = normalizar_valor_editor(datas_participacao)

    campos_vazios = []
    if not nome_normalizado:
        campos_vazios.append("Nome")
    if not email_normalizado:
        campos_vazios.append("Email")
    if not cidade_normalizada:
        campos_vazios.append("Cidade")
    if not funcao_normalizada:
        campos_vazios.append("Função")
    if not datas_normalizadas:
        campos_vazios.append("Datas Participação")

    if campos_vazios:
        erros.append(f"{prefixo}: preencha {', '.join(campos_vazios)}.")

    if email_normalizado and not validar_email(email_normalizado):
        erros.append(f"{prefixo}: email inválido ({email_normalizado}).")

    if datas_normalizadas and validar_datas_br:
        try:
            Participante.parse_datas_participacao_br_to_iso(datas_normalizadas)
        except ValueError as exc:
            erros.append(f"{prefixo}: {exc}")

    return erros


def validar_dataframe_editor(df_editado: pd.DataFrame) -> List[str]:
    """Valida todas as linhas editáveis antes de salvar ou validar participantes."""
    erros = []

    for participante_id, row in df_editado.iterrows():
        # Linhas novas não devem existir neste editor, mas ignoramos linhas
        # sem ID para tolerar estados intermediários do Streamlit.
        if pd.isna(participante_id):
            continue

        erros.extend(
            validar_campos_obrigatorios_participante(
                participante_id,
                nome=row.get("Nome", ""),
                email=row.get("Email", ""),
                cidade=row.get("Cidade", ""),
                funcao=row.get("Função", ""),
                datas_participacao=row.get("Datas Participação", ""),
                validar_datas_br=True,
            )
        )

    return erros


def exibir_erros_validacao_editor(erros: List[str]) -> None:
    """Mostra erros de validação de forma compacta."""
    st.error(
        "⚠️ Corrija os campos obrigatórios antes de salvar alterações ou validar participantes."
    )
    with st.expander("Ver detalhes dos campos inválidos", expanded=True):
        for erro in erros[:20]:
            st.write(f"- {erro}")
        if len(erros) > 20:
            st.write(f"- ... e mais {len(erros) - 20} erro(s).")


def carregar_dados_validacao() -> Optional[tuple]:
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

            # Preparar informações do evento (acessar atributos dentro da sessão)
            evento_info = None
            if evento_atual:
                evento_info = {
                    "id": evento_atual.id,
                    "ano": evento_atual.ano,
                    "datas_evento": evento_atual.datas_evento,
                }

            # Buscar cidades e funções (extrair dados dentro da sessão)
            cidades_raw = cidade_repo.get_all_ordered()
            cidades = {}
            for cidade in cidades_raw:
                cidades[cidade.id] = {
                    "id": cidade.id,
                    "nome": cidade.nome,
                    "estado": cidade.estado,
                }

            funcoes_raw = funcao_repo.get_all_ordered()
            funcoes = {}
            for funcao in funcoes_raw:
                funcoes[funcao.id] = {
                    "id": funcao.id,
                    "nome_funcao": funcao.nome_funcao,
                }

            # Verificar se é coordenador com cidades restritas
            is_superadmin = st.session_state.get(SESSION_KEYS["is_superadmin"], False)
            allowed_cities = st.session_state.get(SESSION_KEYS["allowed_cities"], [])

            # Buscar participantes (extrair dados dentro da sessão)
            participantes_data = []
            if evento_info:
                if is_superadmin:
                    # Superadmin vê todos os participantes
                    participantes_raw = participante_repo.get_by_evento_cidade(
                        evento_info["id"]
                    )
                elif allowed_cities:
                    # Coordenador vê apenas participantes de suas cidades
                    participantes_raw = []
                    for cidade_id in allowed_cities:
                        participantes_cidade = participante_repo.get_by_evento_cidade(
                            evento_info["id"], cidade_id
                        )
                        participantes_raw.extend(participantes_cidade)
                else:
                    # Coordenador sem cidades associadas não vê nenhum participante
                    participantes_raw = []
                    st.warning(
                        "⚠️ Você não está associado a nenhuma cidade. "
                        "Entre em contato com o administrador para associar cidades ao seu perfil."
                    )

                print(
                    f"DEBUG: Data loading - Found {len(participantes_raw)} participants for event {evento_info['id']}"
                )
                for i, participante in enumerate(participantes_raw):
                    nome_decrypted = servico_criptografia.descriptografar(
                        participante.nome_completo_encrypted
                    )
                    email_decrypted = servico_criptografia.descriptografar(
                        participante.email_encrypted
                    )
                    if i < 3:  # Log first 3 participants with validation status
                        print(
                            f"DEBUG: Participant {i+1}: ID={participante.id}, Name='{nome_decrypted}', Validado={participante.validado}"
                        )

                    participantes_data.append(
                        {
                            "id": participante.id,
                            "nome_completo_encrypted": participante.nome_completo_encrypted,
                            "email_encrypted": participante.email_encrypted,
                            "cidade_id": participante.cidade_id,
                            "funcao_id": participante.funcao_id,
                            "titulo_apresentacao": participante.titulo_apresentacao,
                            "datas_participacao": participante.datas_participacao,
                            "validado": participante.validado,
                            "data_inscricao": participante.data_inscricao,
                        }
                    )

            return evento_info, cidades, funcoes, participantes_data

    except Exception as e:
        print(f"DEBUG: Error in data loading: {str(e)}")
        return None


def preparar_dataframe_participantes(
    participantes: List[Dict[str, Any]],
    cidades: Dict[int, Dict[str, Any]],
    funcoes: Dict[int, Dict[str, Any]],
    evento_info: Dict[str, Any],
) -> pd.DataFrame:
    """Prepara um DataFrame com os dados dos participantes para exibição."""

    dados = []

    for participante in participantes:
        try:
            # Descriptografar dados sensíveis
            nome = servico_criptografia.descriptografar(
                participante["nome_completo_encrypted"]
            )
            email = servico_criptografia.descriptografar(
                participante["email_encrypted"]
            )

            # Obter informações relacionadas
            cidade = cidades.get(participante["cidade_id"])
            funcao = funcoes.get(participante["funcao_id"])

            # Calcular carga horária on-the-fly
            carga_horaria, _ = servico_calculo_carga_horaria.calcular_carga_horaria(
                participante["datas_participacao"],
                evento_info["datas_evento"],
                evento_info["ano"],
                participante["funcao_id"],
            )

            # Preparar dados da linha
            linha = {
                "ID": participante["id"],
                "Nome": nome,
                "Email": email,
                "Cidade": f"{cidade['nome']}-{cidade['estado']}" if cidade else "N/A",
                "Função": funcao["nome_funcao"] if funcao else "N/A",
                "Título Apresentação": participante["titulo_apresentacao"] or "-",
                "Datas Participação": Participante.format_datas_participacao_iso_to_br(
                    participante["datas_participacao"]
                ),
                "Carga Horária": f"{carga_horaria}h",
                "Validado": participante["validado"],
                "Data Inscrição": formatar_data_exibicao(
                    participante["data_inscricao"]
                ),
            }

            dados.append(linha)

        except Exception as e:
            st.warning(f"Erro ao processar participante {participante['id']}: {str(e)}")
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


def mostrar_estatisticas(participantes: List[Dict[str, Any]]) -> None:
    """Exibe estatísticas sobre os participantes."""

    total = len(participantes)
    validados = sum(1 for p in participantes if p["validado"])
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
    cidades: Dict[int, Dict[str, Any]],
    funcoes: Dict[int, Dict[str, Any]],
) -> Optional[tuple[pd.DataFrame, str]]:
    """Exibe tabela editável para validação de participação."""

    if df_participantes.empty:
        st.info("📋 Nenhum participante encontrado para este evento.")
        return None

    st.subheader("📋 Validação de Participação")

    # Check if user is superadmin or regular coordinator
    is_superadmin = st.session_state.get(SESSION_KEYS["is_superadmin"], False)
    allowed_cities = st.session_state.get(SESSION_KEYS["allowed_cities"], [])

    # Coordenadores podem editar participantes de suas cidades
    can_edit = is_superadmin or bool(allowed_cities)

    st.write("Marque os participantes que deseja validar/desvalidar ou excluir.")

    if is_superadmin:
        st.info(
            "💡 **Atenção superadmin:**\n\n"
            "- Você pode editar nome, email, cidade, função, título, datas etc...\n"
            "- Clique em “💾 Salvar Alterações” para confirmar edições.\n"
            "- Para excluir cadastros inválidos, marque as linhas e clique em “🗑️ Excluir Selecionados”."
        )
    elif allowed_cities:
        st.info(
            "💡 **Coordenador:** Você pode editar os dados dos participantes das suas cidades associadas. Não esqueça de salvar as alterações!"
        )

    # Preparar DataFrame para edição
    df_editavel = df_participantes.copy()

    # Ordenar por Nome em ordem ascendente
    df_editavel = df_editavel.sort_values(by="Nome", ascending=True)

    # Adicionar coluna de seleção
    df_editavel["Selecionado"] = False

    # Formatar coluna Validado para exibição
    df_editavel["Status"] = df_editavel["Validado"].apply(
        lambda x: "✅ Validado" if x else "⏳ Pendente"
    )

    # Colunas para exibição na tabela (replace Carga Horária with Datas Participação)
    colunas_exibicao = [
        "ID",  # Include ID column for processing
        "Selecionado",
        "Nome",
        "Email",
        "Cidade",
        "Função",
        "Título Apresentação",
        "Datas Participação",
        "Status",
        "Data Inscrição",
    ]

    # Editar apenas colunas selecionadas
    df_para_editor = df_editavel[colunas_exibicao].copy()

    # Set ID as index so hide_index=True will hide it
    df_para_editor = df_para_editor.set_index("ID")

    # Preparar options para Cidade e Função dropdowns
    cidade_options = [""] + [f"{c['nome']}-{c['estado']}" for c in cidades.values()]
    funcao_options = [""] + [f["nome_funcao"] for f in funcoes.values()]

    acao = ""
    with st.form("form_validacao_participantes", clear_on_submit=False):
        # Data editor com configurações
        edited_df = st.data_editor(
            df_para_editor,
            column_config={
                "Selecionado": st.column_config.CheckboxColumn(
                    "Selecionar",
                    help="Marque para validar/desvalidar ou excluir este participante",
                ),
                "Nome": st.column_config.TextColumn(
                    "Nome",
                    width="large",
                    disabled=not can_edit,
                    max_chars=200,
                    help=(
                        "Editar nome (coordenadores e superadmin)"
                        if can_edit
                        else "Somente leitura"
                    ),
                ),
                "Email": st.column_config.TextColumn(
                    "Email",
                    width="large",
                    disabled=not can_edit,
                    max_chars=200,
                    help=(
                        "Editar email (coordenadores e superadmin)"
                        if can_edit
                        else "Somente leitura"
                    ),
                ),
                "Cidade": st.column_config.SelectboxColumn(
                    "Cidade",
                    options=cidade_options,
                    width="medium",
                    disabled=not is_superadmin,  # Apenas superadmin pode trocar cidade
                    help=(
                        "Selecionar cidade (somente superadmin)"
                        if is_superadmin
                        else "Somente leitura"
                    ),
                ),
                "Função": st.column_config.SelectboxColumn(
                    "Função",
                    options=funcao_options,
                    width="medium",
                    disabled=not can_edit,
                    help=(
                        "Selecionar função (coordenadores e superadmin)"
                        if can_edit
                        else "Somente leitura"
                    ),
                ),
                "Título Apresentação": st.column_config.TextColumn(
                    "Título Apresentação",
                    width="large",
                    disabled=not can_edit,
                    help=(
                        "Editar título (coordenadores e superadmin)"
                        if can_edit
                        else "Somente leitura"
                    ),
                ),
                "Datas Participação": st.column_config.TextColumn(
                    "Datas Participação",
                    width="medium",
                    disabled=not can_edit,
                    help=(
                        "Editar datas no formato DD/MM/YYYY, separadas por vírgula (coordenadores e superadmin)"
                        if can_edit
                        else "Somente leitura"
                    ),
                ),
                "Status": st.column_config.TextColumn(
                    "Status", width="medium", disabled=True
                ),
                "Data Inscrição": st.column_config.TextColumn(
                    "Data Inscrição", width="medium", disabled=True
                ),
            },
            hide_index=True,
            width="content",
            num_rows="fixed",
            key="participantes_editor",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            validar_submit = st.form_submit_button(
                "🔄 Validar/Desvalidar", type="primary", width="content"
            )
        with col2:
            salvar_submit = st.form_submit_button(
                "💾 Salvar Alterações",
                type="primary",
                width="content",
                disabled=not can_edit,
            )
        with col3:
            excluir_submit = st.form_submit_button(
                "🗑️ Excluir Selecionados",
                type="secondary",
                width="content",
                disabled=not can_edit,
            )

        if validar_submit:
            acao = "validar"
        elif salvar_submit:
            acao = "salvar"
        elif excluir_submit:
            acao = "excluir"

    return edited_df, acao


def processar_validacao(
    df_original: pd.DataFrame,
    df_editado: pd.DataFrame,
    cidades: Dict[int, Dict[str, Any]],
    funcoes: Dict[int, Dict[str, Any]],
    acao: str,
) -> str:
    """Processa a validação e edições dos participantes selecionados.

    Returns:
        "validacao" if validation was performed
        "edicao" if edits were saved
        "" if no action was taken
    """

    # Check if user is superadmin or regular coordinator
    is_superadmin = st.session_state.get(SESSION_KEYS["is_superadmin"], False)
    allowed_cities = st.session_state.get(SESSION_KEYS["allowed_cities"], [])

    # Coordenadores podem editar participantes de suas cidades
    can_edit = is_superadmin or bool(allowed_cities)

    if not acao:
        return ""

    # CRITICAL FIX: Ensure df_original uses ID as index to match df_editado
    # df_editado already has ID as index from tabela_validacao_participantes
    # But df_original (df_filtrado) comes with default numeric index
    if "ID" in df_original.columns:
        df_original = df_original.set_index("ID")

    # Identificar participantes selecionados antes das validações para permitir
    # excluir registros já corrompidos/incompletos.
    selecionados = df_editado[df_editado["Selecionado"] == True]

    if acao == "excluir":
        if not can_edit:
            st.error("Você não tem permissão para excluir participantes.")
        elif selecionados.empty:
            st.info("Selecione pelo menos um participante para excluir.")
        else:
            with st.spinner("Excluindo participantes selecionados..."):
                sucesso, mensagem = excluir_participantes(selecionados.index.tolist())

            if sucesso:
                st.success(f"🎉 {mensagem}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {mensagem}")
        return ""

    erros_editor = validar_dataframe_editor(df_editado)
    if erros_editor:
        exibir_erros_validacao_editor(erros_editor)
        return ""

    # Detectar mudanças em campos editáveis (para superadmins e coordenadores)
    mudancas = []
    if can_edit:
        for idx, row in df_editado.iterrows():
            # idx is now the participant ID since we set ID as index
            participante_id = idx

            # Use the index to get the corresponding row from df_original
            if idx in df_original.index:
                original_row = df_original.loc[idx]

                # Check for changes in editable fields
                changes = {}

                # Compare Nome
                if normalizar_valor_editor(row["Nome"]) != normalizar_valor_editor(
                    original_row["Nome"]
                ):
                    changes["nome"] = normalizar_valor_editor(row["Nome"])

                # Compare Email
                if normalizar_valor_editor(row["Email"]) != normalizar_valor_editor(
                    original_row["Email"]
                ):
                    changes["email"] = normalizar_valor_editor(row["Email"])

                # Compare Cidade
                if normalizar_valor_editor(row["Cidade"]) != normalizar_valor_editor(
                    original_row["Cidade"]
                ):
                    cidade_nome = normalizar_valor_editor(row["Cidade"])
                    if cidade_nome:  # Only if not empty
                        cidade_id = next(
                            (
                                cid
                                for cid, c in cidades.items()
                                if f"{c['nome']}-{c['estado']}" == cidade_nome
                            ),
                            None,
                        )
                        if cidade_id:
                            changes["cidade_id"] = cidade_id

                # Compare Função
                if normalizar_valor_editor(row["Função"]) != normalizar_valor_editor(
                    original_row["Função"]
                ):
                    funcao_nome = normalizar_valor_editor(row["Função"])
                    if funcao_nome:  # Only if not empty
                        funcao_id = next(
                            (
                                fid
                                for fid, f in funcoes.items()
                                if f["nome_funcao"] == funcao_nome
                            ),
                            None,
                        )
                        if funcao_id:
                            changes["funcao_id"] = funcao_id

                # Compare Título Apresentação
                if normalizar_valor_editor(
                    row.get("Título Apresentação", "")
                ) != normalizar_valor_editor(
                    original_row.get("Título Apresentação", "")
                ):
                    changes["titulo_apresentacao"] = normalizar_valor_editor(
                        row.get("Título Apresentação", "")
                    )

                # Compare Datas Participação
                if normalizar_valor_editor(
                    row["Datas Participação"]
                ) != normalizar_valor_editor(original_row["Datas Participação"]):
                    changes["datas_participacao"] = normalizar_valor_editor(
                        row["Datas Participação"]
                    )

                if changes:
                    mudancas.append({"id": participante_id, "changes": changes})

    if acao == "validar":
        if not selecionados.empty:
            with st.spinner("Alternando status de validação..."):
                # Para cada participante selecionado, toggle seu status atual
                validation_statuses = []
                ids_para_validar = []

                for idx in selecionados.index:
                    if idx in df_original.index:
                        original_row = df_original.loc[idx]
                        # Toggle: se está validado (True), vira False; se não está (False), vira True
                        current_status = original_row["Validado"]
                        new_status = not current_status
                        validation_statuses.append(new_status)
                        ids_para_validar.append(idx)
                        logger.info(
                            f"Toggling participant {idx}: {current_status} -> {new_status}"
                        )
                    else:
                        # Se não encontrar no original, validar por padrão
                        validation_statuses.append(True)
                        ids_para_validar.append(idx)
                        logger.info(
                            f"Participant {idx} not found in original, defaulting to True"
                        )

                logger.info(
                    f"Calling validar_participantes with {len(ids_para_validar)} participants"
                )
                sucesso, mensagem = validar_participantes(
                    ids_para_validar, validation_statuses
                )
                logger.info(
                    f"validar_participantes returned: sucesso={sucesso}, mensagem={mensagem}"
                )

            if sucesso:
                st.success(f"🎉 Status de validação alternado com sucesso!")
                if "atualizados com sucesso" in mensagem:
                    st.info(mensagem)
                time.sleep(1)  # Brief pause to show the message
                st.rerun()  # Force immediate refresh
            else:
                st.error(f"❌ Erro ao alternar validação: {mensagem}")
        else:
            st.info("Selecione pelo menos um participante para validar/desvalidar.")

    elif acao == "salvar":
        if not can_edit:
            st.error("Você não tem permissão para editar participantes.")
        elif mudancas:
            with st.spinner("Salvando alterações..."):
                sucesso, mensagem = salvar_edicoes_participantes(mudancas)

            if sucesso:
                st.success("🎉 Alterações salvas com sucesso!")
                time.sleep(1)  # Brief pause to show the message
                st.rerun()  # Force immediate refresh
            else:
                st.error(f"❌ {mensagem}")
        else:
            st.info("Nenhuma alteração detectada.")

    return ""


def excluir_participantes(participante_ids: List[Any]) -> tuple[bool, str]:
    """Exclui participantes selecionados."""
    try:
        ids_para_excluir = []
        for participante_id in participante_ids:
            if pd.isna(participante_id):
                continue
            ids_para_excluir.append(int(participante_id))

        if not ids_para_excluir:
            return False, "Nenhum participante selecionado para exclusão."

        with db_manager.get_db_session() as session:
            excluidos = 0
            for participante_id in ids_para_excluir:
                participante = session.get(Participante, participante_id)
                if not participante:
                    logger.warning(
                        f"Participante ID {participante_id} não encontrado para exclusão"
                    )
                    continue

                session.delete(participante)
                excluidos += 1
                logger.info(f"🗑️ Participante ID {participante_id} excluído")

        if excluidos == 0:
            return False, "Nenhum participante encontrado para exclusão."

        return True, f"{excluidos} participante(s) excluído(s) com sucesso."

    except Exception as e:
        logger.error(f"❌ Erro ao excluir participantes: {str(e)}")
        return False, "Erro ao excluir participantes."


def salvar_edicoes_participantes(mudancas: List[Dict[str, Any]]) -> tuple[bool, str]:
    """Salva alterações nos participantes e regenera hash de validação se necessário."""
    try:
        logger.info(f"📝 Iniciando salvamento de {len(mudancas)} alterações")

        with db_manager.get_db_session() as session:
            from app.models import Participante
            from app.db import get_participante_repository

            participante_repo = get_participante_repository(session)
            participantes_por_id = {}
            identidades_propostas = []
            erros_validacao = []

            for mudanca in mudancas:
                participante = session.get(Participante, mudanca["id"])

                if not participante:
                    logger.error(f"❌ Participante {mudanca['id']} não encontrado!")
                    continue

                participantes_por_id[mudanca["id"]] = participante
                changes = mudanca["changes"]

                nome_atual = servico_criptografia.descriptografar(
                    participante.nome_completo_encrypted
                )
                email_atual = servico_criptografia.descriptografar(
                    participante.email_encrypted
                )

                nome_proposto = changes.get("nome", nome_atual)
                email_proposto = changes.get("email", email_atual)
                cidade_id = changes.get("cidade_id", participante.cidade_id)
                funcao_id = changes.get("funcao_id", participante.funcao_id)
                datas_participacao = changes.get(
                    "datas_participacao", participante.datas_participacao
                )

                erros_validacao.extend(
                    validar_campos_obrigatorios_participante(
                        participante.id,
                        nome=nome_proposto,
                        email=email_proposto,
                        cidade=cidade_id,
                        funcao=funcao_id,
                        datas_participacao=datas_participacao,
                        validar_datas_br="datas_participacao" in changes,
                    )
                )

                email_hash = servico_criptografia.gerar_hash_email(email_proposto)

                identidades_propostas.append(
                    (participante.id, email_hash, participante.evento_id, funcao_id)
                )

            if erros_validacao:
                mensagem = " ".join(erros_validacao[:5])
                if len(erros_validacao) > 5:
                    mensagem += f" ... e mais {len(erros_validacao) - 5} erro(s)."
                return False, mensagem

            identidades_vistas = {}
            for (
                participante_id,
                email_hash,
                evento_id,
                funcao_id,
            ) in identidades_propostas:
                identidade = (email_hash, evento_id, funcao_id)
                if identidade in identidades_vistas:
                    return (
                        False,
                        "As alterações criariam inscrições duplicadas para o mesmo email, evento e função.",
                    )
                identidades_vistas[identidade] = participante_id

                existing = participante_repo.get_by_email_evento_funcao(
                    email_hash,
                    evento_id,
                    funcao_id,
                    exclude_participante_id=participante_id,
                )
                if existing:
                    return (
                        False,
                        "Este email já está inscrito neste evento com esta função.",
                    )

            for mudanca in mudancas:
                logger.info(
                    f"Processando participante ID {mudanca['id']}: {mudanca['changes']}"
                )

                participante = participantes_por_id.get(mudanca["id"])

                if not participante:
                    logger.error(f"❌ Participante {mudanca['id']} não encontrado!")
                    continue

                # Track if we need to regenerate hash (nome ou email changed)
                needs_hash_regeneration = False

                for campo, valor in mudanca["changes"].items():
                    if campo == "nome":
                        old_name = servico_criptografia.descriptografar(
                            participante.nome_completo_encrypted
                        )
                        participante.nome_completo_encrypted = (
                            servico_criptografia.criptografar_nome(valor)
                        )
                        needs_hash_regeneration = True
                        logger.info(f"✏️ Nome atualizado: '{old_name}' -> '{valor}'")
                    elif campo == "email":
                        old_email = servico_criptografia.descriptografar(
                            participante.email_encrypted
                        )
                        # Update both encrypted email and hash
                        participante.email_encrypted = (
                            servico_criptografia.criptografar_email(valor)
                        )
                        participante.email_hash = servico_criptografia.gerar_hash_email(
                            valor
                        )
                        needs_hash_regeneration = True
                        logger.info(f"✉️ Email atualizado: '{old_email}' -> '{valor}'")
                    elif campo == "cidade_id":
                        logger.info(
                            f"🏙️ Cidade atualizada: {participante.cidade_id} -> {valor}"
                        )
                        participante.cidade_id = valor
                    elif campo == "funcao_id":
                        logger.info(
                            f"👔 Função atualizada: {participante.funcao_id} -> {valor}"
                        )
                        participante.funcao_id = valor
                    elif campo == "titulo_apresentacao":
                        logger.info(
                            f"📄 Título atualizado: '{participante.titulo_apresentacao}' -> '{valor}'"
                        )
                        participante.titulo_apresentacao = valor if valor else None
                    elif campo == "datas_participacao":
                        # Convert from Brazilian format (DD/MM/YYYY) to ISO (YYYY-MM-DD)
                        try:
                            valor_iso = Participante.parse_datas_participacao_br_to_iso(
                                valor
                            )
                            logger.info(
                                f"📅 Datas atualizadas: '{participante.datas_participacao}' -> '{valor_iso}' (convertido de '{valor}')"
                            )
                            participante.datas_participacao = valor_iso
                        except ValueError as e:
                            logger.error(f"❌ Erro ao converter datas: {str(e)}")
                            raise ValueError(
                                f"Datas inválidas para participante ID {participante.id}: {e}"
                            )

                # Regenerate validation hash if nome or email changed
                if needs_hash_regeneration and participante.hash_validacao:
                    nome_atual = servico_criptografia.descriptografar(
                        participante.nome_completo_encrypted
                    )
                    email_atual = servico_criptografia.descriptografar(
                        participante.email_encrypted
                    )

                    novo_hash = servico_criptografia.gerar_hash_validacao_certificado(
                        participante.id, participante.evento_id, email_atual, nome_atual
                    )
                    participante.hash_validacao = novo_hash
                    logger.info(f"🔐 Hash de validação regenerado")

                # Merge changes
                session.merge(participante)
                logger.info(
                    f"✅ Participante {mudanca['id']} atualizado (merge realizado)"
                )

            # Flush changes to ensure they're written before commit
            session.flush()
            logger.info(
                f"💾 Flush realizado - {len(mudancas)} alterações preparadas para commit"
            )

            # Context manager will auto-commit
        logger.info(f"✅ Commit automático concluído - alterações salvas no banco")
        return True, "Alterações salvas com sucesso!"
    except IntegrityError:
        logger.warning("⚠️ Alteração duplicada bloqueada por email/evento/função")
        return False, "Este email já está inscrito neste evento com esta função."
    except ValueError as e:
        logger.warning(f"⚠️ Alteração inválida bloqueada: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"❌ Erro ao salvar alterações: {str(e)}")
        import traceback

        traceback.print_exc()
        return False, "Erro ao salvar alterações."


def mostrar_filtros(df_participantes: pd.DataFrame) -> pd.DataFrame:
    """Exibe filtros para os participantes."""

    st.subheader("🔍 Filtros")

    # Check if user is superadmin
    is_superadmin = st.session_state.get(SESSION_KEYS["is_superadmin"], False)
    allowed_cities = st.session_state.get(SESSION_KEYS["allowed_cities"], [])

    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtro por status
        status_filter = st.selectbox(
            "Status",
            options=["Todos", "Pendentes", "Validados"],
            help="Filtrar por status de validação",
        )

    with col2:
        # Filtro por cidade (desabilitado para coordenadores, pois já filtrado automaticamente)
        if is_superadmin:
            cidades_disponiveis = ["Todas"] + sorted(
                df_participantes["Cidade"].unique().tolist()
            )
            cidade_filter = st.selectbox(
                "Cidade", options=cidades_disponiveis, help="Filtrar por cidade"
            )
        else:
            # Para coordenadores, mostrar info das cidades associadas
            if allowed_cities:
                cidades_coord = sorted(df_participantes["Cidade"].unique().tolist())
                st.info(f"🏙️ **Suas cidades:** {', '.join(cidades_coord)}")
            cidade_filter = "Todas"  # Não aplicar filtro adicional

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
        <h1>👨‍👨‍👦‍👦 Participantes</h1>
        <p>Área exclusiva para coordenadores</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Informações do usuário
    mostrar_informacoes_usuario()

    # Carregar dados
    dados = carregar_dados_validacao()
    if dados is None:
        st.error(
            "❌ Erro ao carregar dados do sistema. Por favor, recarregue a página."
        )
        return

    evento_info, cidades, funcoes, participantes = dados

    if not evento_info:
        st.error("❌ Nenhum evento encontrado. Contate o administrador.")
        return

    # Informações do evento
    # Formatar datas do evento para exibição amigável
    datas_evento_str = ", ".join(evento_info["datas_evento"])
    st.info(
        f"🎯 **Evento:** Pint of Science {evento_info['ano']}, dias: {datas_evento_str}"
    )

    # Preparar DataFrame
    df_participantes = preparar_dataframe_participantes(
        participantes, cidades, funcoes, evento_info
    )

    if df_participantes.empty:
        st.warning("⚠️ Nenhum participante encontrado para este evento.")
        return

    # Estatísticas
    mostrar_estatisticas(participantes)

    # Filtros
    df_filtrado = mostrar_filtros(df_participantes)

    # Tabela de validação
    resultado_editor = tabela_validacao_participantes(df_filtrado, cidades, funcoes)

    if resultado_editor is not None:
        df_editado, acao = resultado_editor
        # Processar validação e edições (rerun happens inside this function if needed)
        processar_validacao(df_filtrado, df_editado, cidades, funcoes, acao)

    # Rodapé
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
