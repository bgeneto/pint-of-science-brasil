"""
Módulo de Serviços de Negócio

Este módulo contém a lógica de negócio central do sistema, incluindo:
- Criptografia de dados sensíveis
- Cálculo de carga horária
- Geração de certificados PDF
- Envio de e-mails
- Validação de regras de negócio
"""

import logging
import re
import uuid
import json
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from cryptography.fernet import Fernet

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

import requests
import json
from typing import Dict, Any

# Check if requests is available
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print(
        "⚠️ AVISO: Biblioteca requests não disponível. Funcionalidades de e-mail estarão desabilitadas."
    )

from .core import settings
from .models import (
    Evento,
    Cidade,
    Funcao,
    Participante,
    Coordenador,
    ParticipanteCreate,
    ParticipanteRead,
)
from .db import (
    db_manager,
    get_evento_repository,
    get_cidade_repository,
    get_funcao_repository,
    get_participante_repository,
    get_auditoria_repository,
)
from .auth import get_current_user_info

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServicoCriptografia:
    """Serviço para criptografia de dados sensíveis."""

    def __init__(self):
        if not settings.encryption_key:
            raise ValueError("Chave de criptografia não configurada")

        try:
            self._fernet = Fernet(settings.encryption_key.encode())
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Fernet: {e}")
            raise ValueError("Chave de criptografia inválida")

    def criptografar(self, dados: str) -> bytes:
        """Criptografa dados sensíveis."""
        try:
            return self._fernet.encrypt(dados.encode("utf-8"))
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar dados: {e}")
            raise ValueError("Erro ao criptografar dados")

    def descriptografar(self, dados_criptografados: bytes) -> str:
        """Descriptografa dados sensíveis."""
        try:
            return self._fernet.decrypt(dados_criptografados).decode("utf-8")
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar dados: {e}")
            raise ValueError("Erro ao descriptografar dados")

    def criptografar_email(self, email: str) -> bytes:
        """Criptografa um endereço de email."""
        return self.criptografar(email.lower().strip())

    def criptografar_nome(self, nome: str) -> bytes:
        """Criptografa um nome completo."""
        return self.criptografar(nome.strip())

    def gerar_hash_email(self, email: str) -> str:
        """Gera um hash SHA-256 do email para buscas eficientes."""
        import hashlib

        return hashlib.sha256(email.lower().strip().encode("utf-8")).hexdigest()

    def gerar_hash_validacao_certificado(
        self, participante_id: int, evento_id: int, email: str, nome: str
    ) -> str:
        """
        Gera um hash HMAC-SHA256 para validação de certificado.

        Este hash é único e verificável, permitindo validar a autenticidade
        de um certificado sem armazenar o PDF.

        Args:
            participante_id: ID do participante
            evento_id: ID do evento
            email: Email do participante
            nome: Nome completo do participante

        Returns:
            String hexadecimal com 64 caracteres (HMAC-SHA256)
        """
        import hmac
        import hashlib

        # Construir mensagem a ser assinada
        message = (
            f"{participante_id}|{evento_id}|{email.lower().strip()}|{nome.strip()}"
        )

        # Gerar HMAC usando chave secreta
        secret_key = settings.certificate_secret_key.encode("utf-8")
        signature = hmac.new(
            secret_key, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return signature

    def verificar_hash_validacao_certificado(
        self,
        hash_fornecido: str,
        participante_id: int,
        evento_id: int,
        email: str,
        nome: str,
    ) -> bool:
        """
        Verifica se um hash de validação é autêntico.

        Args:
            hash_fornecido: Hash a ser verificado
            participante_id: ID do participante
            evento_id: ID do evento
            email: Email do participante
            nome: Nome completo do participante

        Returns:
            True se o hash é válido, False caso contrário
        """
        import hmac

        hash_esperado = self.gerar_hash_validacao_certificado(
            participante_id, evento_id, email, nome
        )

        # Comparação segura contra timing attacks
        return hmac.compare_digest(hash_fornecido, hash_esperado)


class ServicoCalculoCargaHoraria:
    """Serviço para cálculo de carga horária de participação."""

    def __init__(self):
        self._duracao_padrao_evento = 4  # 4 horas por dia de evento (padrão)

    def _carregar_configuracao_carga_horaria(self, evento_ano: int) -> Dict[str, Any]:
        """
        Carrega configuração de carga horária para um ano específico.

        Args:
            evento_ano: Ano do evento

        Returns:
            Dicionário com configuração de carga horária
        """
        # Use absolute path based on the location of this file
        services_dir = Path(__file__).parent
        project_root = services_dir.parent
        config_path = project_root / "static" / "certificate_config.json"

        default_config = {
            "horas_por_dia": 4,
            "horas_por_evento": 40,
            "funcoes_evento_completo": [],  # IDs das funções que recebem carga horária total
        }

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                ano_key = str(evento_ano)
                if ano_key in config and "carga_horaria" in config[ano_key]:
                    return config[ano_key]["carga_horaria"]

            return default_config

        except Exception as e:
            logger.error(f"Erro ao carregar configuração de carga horária: {e}")
            return default_config

    def calcular_carga_horaria(
        self,
        datas_participacao: str,
        evento_datas,
        evento_ano: int = None,
        funcao_id: int = None,
    ) -> Tuple[int, str]:
        """
        Calcula a carga horária com base nas datas de participação.

        Args:
            datas_participacao: String com datas ISO separadas por vírgula
            evento_datas: Lista de strings ISO ou string (formato antigo)
            evento_ano: Ano do evento (opcional, para buscar configuração)
            funcao_id: ID da função do participante (opcional)

        Returns:
            Tupla com (carga_horaria_total, detalhes_calculo)
        """
        try:
            # Carregar configuração se ano foi fornecido
            if evento_ano:
                config = self._carregar_configuracao_carga_horaria(evento_ano)
                horas_por_dia = config.get("horas_por_dia", self._duracao_padrao_evento)
                horas_por_evento = config.get("horas_por_evento", 40)
                funcoes_evento_completo = config.get("funcoes_evento_completo", [])
            else:
                horas_por_dia = self._duracao_padrao_evento
                horas_por_evento = 40
                funcoes_evento_completo = []

            # Verificar se a função tem direito a carga horária total do evento
            if funcao_id and funcao_id in funcoes_evento_completo:
                detalhes = (
                    f"Função com carga horária de evento completo\n"
                    f"Total: {horas_por_evento}h (configurado para esta função)"
                )
                logger.info(
                    f"📊 Carga horária (evento completo): {horas_por_evento}h para função ID {funcao_id}"
                )
                return horas_por_evento, detalhes

            # Extrair dias do evento
            if isinstance(evento_datas, list):
                # Lista de strings ISO
                dias_evento = evento_datas
            else:
                # Formato antigo: string (não deveria acontecer)
                dias_evento = [evento_datas]

            # Datas de participação vêm como string separada por vírgulas em formato ISO
            dias_participacao = [
                d.strip() for d in datas_participacao.split(",") if d.strip()
            ]

            # Calcular dias únicos de participação
            dias_unicos = set()
            for data in dias_participacao:
                if data in dias_evento:
                    dias_unicos.add(data)

            # Calcular carga horária
            carga_horaria = len(dias_unicos) * horas_por_dia

            detalhes = (
                f"Dias de participação: {len(dias_unicos)} ({', '.join(sorted(dias_unicos))})\n"
                f"Carga horária por dia: {horas_por_dia}h\n"
                f"Total: {carga_horaria}h"
            )

            logger.info(
                f"📊 Carga horária calculada: {carga_horaria}h para {len(dias_unicos)} dias"
            )
            return carga_horaria, detalhes

        except Exception as e:
            logger.error(f"❌ Erro ao calcular carga horária: {e}")
            return 0, "Erro no cálculo"

    def validar_datas_participacao(self, datas_participacao: str, evento_datas) -> bool:
        """Valida se as datas de participação são válidas para o evento."""
        try:
            # Extrair dias do evento
            if isinstance(evento_datas, list):
                # Lista de strings ISO
                dias_evento = evento_datas
            else:
                # Formato antigo: string (não deveria acontecer)
                dias_evento = [evento_datas]

            # Datas de participação vêm como string separada por vírgulas em formato ISO
            dias_participacao = [
                d.strip() for d in datas_participacao.split(",") if d.strip()
            ]

            if not dias_evento:
                return False

            # Verificar se pelo menos um dia de participação está no evento
            valid = any(data in dias_evento for data in dias_participacao)
            return valid

        except Exception as e:
            return False

    def _extrair_datas_texto(self, texto: str) -> List[str]:
        """Extrai datas de uma string de texto."""
        datas = []

        # Padrões comuns de data
        padroes = [
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # DD/MM/YYYY
            r"\b\d{1,2}\s+de\s+[a-zA-ZçÇãõÃÕáéíóúÁÉÍÓÚêÊôÔâÂàÀ]+",  # DD de Mês
            r"\b\d{1,2}\b",  # Apenas números (dias)
        ]

        for padrao in padroes:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            datas.extend(matches)

        # Remover duplicatas e normalizar
        return list(set([d.strip() for d in datas if d.strip()]))

    def validar_datas_participacao_old(
        self, datas_participacao: str, evento_datas: str
    ) -> bool:
        """Valida se as datas de participação são válidas para o evento."""
        try:
            dias_evento = self._extrair_datas_texto(evento_datas)
            dias_participacao = self._extrair_datas_texto(datas_participacao)

            if not dias_evento:
                return False

            # Verificar se pelo menos um dia de participação está no evento
            return any(data in dias_evento for data in dias_participacao)

        except Exception:
            return False


class ServicoEmail:
    """Serviço para envio de e-mails usando Brevo API com requests."""

    def __init__(self):
        self._configured = REQUESTS_AVAILABLE and settings.is_email_configured

        if not self._configured:
            logger.warning("⚠️ Serviço de e-mail não configurado")
            return

        try:
            self.api_url = "https://api.brevo.com/v3/smtp/email"
            self.api_key = settings.brevo_api_key
            self.sender_email = settings.brevo_sender_email
            self.sender_name = settings.brevo_sender_name
        except Exception as e:
            logger.error(f"❌ Erro ao configurar API Brevo: {e}")
            self._configured = False

    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return self._configured

    def enviar_email_confirmacao_inscricao(
        self, nome: str, email: str, dados_inscricao: Dict[str, Any]
    ) -> bool:
        """Envia e-mail de confirmação de inscrição."""
        if not self._configured:
            logger.warning("⚠️ E-mail não enviado: serviço não configurado")
            return False

        try:
            assunto = "Confirmação de Inscrição - Pint of Science Brasil"

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #e74c3c; text-align: center;">
                        🍺 Pint of Science Brasil
                    </h2>

                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>Olá, {nome}!</h3>
                        <p>Recebemos sua inscrição para o Pint of Science Brasil com sucesso!</p>

                        <h4>Detalhes da sua inscrição:</h4>
                        <ul>
                            <li><strong>Evento:</strong> {dados_inscricao.get('evento_ano', 'N/A')}</li>
                            <li><strong>Cidade:</strong> {dados_inscricao.get('cidade_nome', 'N/A')}</li>
                            <li><strong>Função:</strong> {dados_inscricao.get('funcao_nome', 'N/A')}</li>
                            <li><strong>Datas de participação:</strong> {dados_inscricao.get('datas_participacao', 'N/A')}</li>
                            <li><strong>Carga horária:</strong> {dados_inscricao.get('carga_horaria', 0)} horas</li>
                        </ul>

                        <p><strong>Próximos passos:</strong></p>
                        <ol>
                            <li>Prepare-se para que sua participação se torne memorável</li>
                            <li>Após sua apresentação, você receberá um e-mail com instruções para download de seu certificado</li>
                            <li>Seu certificado estará disponível para download em {settings.base_url}</li>
                            <li>Qualquer dúvida, entre em contato com os organizadores da sua cidade</li>
                        </ol>
                    </div>

                    <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #e8f4f8; border-radius: 8px;">
                        <p style="margin: 0;">
                            <em>“Levando a ciência para o bar”</em>
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">
                            © Pint of Science Brasil
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            return self._enviar_email(email, assunto, html_content)

        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail de confirmação: {e}")
            return False

    def enviar_email_certificado_liberado(
        self, nome: str, email: str, link_download: str
    ) -> bool:
        """Envia e-mail informando que o certificado está liberado."""
        if not self._configured:
            logger.warning("⚠️ E-mail não enviado: serviço não configurado")
            return False

        try:
            assunto = "Seu Certificado Pint of Science Brasil Está Disponível! 🎉"

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #27ae60; text-align: center;">
                        🎉 Certificado Disponível!
                    </h2>

                    <div style="background-color: #f8fff8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60;">
                        <h3>Parabéns, {nome}!</h3>
                        <p>Sua participação no Pint of Science Brasil foi validada e seu certificado já está disponível para download!</p>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{link_download}" style="
                                background-color: #e74c3c;
                                color: white;
                                padding: 12px 24px;
                                text-decoration: none;
                                border-radius: 6px;
                                font-weight: bold;
                                display: inline-block;
                            ">
                                BAIXAR CERTIFICADO
                            </a>
                        </div>

                        <p><strong>O certificado inclui:</strong></p>
                        <ul>
                            <li>Seu nome completo e função no evento</li>
                            <li>Carga horária validada pelos organizadores</li>
                            <li>Assinatura digital dos organizadores</li>
                            <li>Validade e autenticidade garantidas</li>
                        </ul>
                    </div>

                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;">
                            <strong>⏰ Importante:</strong> O link de download é pessoal e intransferível.
                            Mantenha seu certificado em local seguro.
                        </p>
                    </div>

                    <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #e8f4f8; border-radius: 8px;">
                        <p style="margin: 0;">
                            <em>“Levando a ciência para o bar”</em>
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">
                            © Pint of Science Brasil
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            return self._enviar_email(email, assunto, html_content)

        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail de certificado: {e}")
            return False

    def _enviar_email(self, destino: str, assunto: str, html_content: str) -> bool:
        """Método interno para envio de e-mails usando requests."""
        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json",
            }

            data = {
                "sender": {"name": self.sender_name, "email": self.sender_email},
                "to": [{"email": destino}],
                "subject": assunto,
                "htmlContent": html_content,
            }

            response = requests.post(self.api_url, headers=headers, json=data)

            if response.status_code == 201:
                logger.info(f"✅ E-mail enviado com sucesso para {destino}")
                return True
            else:
                logger.error(
                    f"❌ Falha ao enviar e-mail para {destino}: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Erro na API Brevo: {e}")
            return False


class GeradorCertificado:
    """Serviço para geração de certificados em PDF."""

    def __init__(self):
        self._servico_criptografia = ServicoCriptografia()

    def _carregar_configuracao_cores(self, evento_ano: int) -> Dict[str, str]:
        """
        Carrega configuração de cores do certificado para um ano específico.

        Args:
            evento_ano: Ano do evento para buscar configuração

        Returns:
            Dicionário com cores configuradas para o ano
        """
        # Use absolute path based on the location of this file
        services_dir = Path(__file__).parent
        project_root = services_dir.parent
        config_path = project_root / "static" / "certificate_config.json"

        default_config = {
            "cor_primaria": "#e74c3c",
            "cor_secundaria": "#c0392b",
            "cor_texto": "#2c3e50",
            "cor_destaque": "#f39c12",
        }

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    all_configs = json.load(f)

                    # Tentar buscar configuração do ano específico
                    ano_key = str(evento_ano)
                    if ano_key in all_configs and "cores" in all_configs[ano_key]:
                        config = all_configs[ano_key]["cores"]
                        # Garantir que todas as chaves existem
                        for key in default_config:
                            if key not in config:
                                config[key] = default_config[key]
                        return config

                    # Fallback para configuração padrão
                    if "_default" in all_configs and "cores" in all_configs["_default"]:
                        config = all_configs["_default"]["cores"]
                        for key in default_config:
                            if key not in config:
                                config[key] = default_config[key]
                        return config
        except Exception as e:
            logger.warning(
                f"Erro ao carregar config de cores para ano {evento_ano}: {e}"
            )

        return default_config

    def _carregar_caminhos_imagens(self, evento_ano: int) -> Dict[str, Path]:
        """
        Carrega caminhos das imagens do certificado para um ano específico.

        Args:
            evento_ano: Ano do evento para buscar configuração

        Returns:
            Dicionário com Path objects para cada imagem
        """
        # Use absolute path based on the location of this file
        services_dir = Path(__file__).parent
        project_root = services_dir.parent
        config_path = project_root / "static" / "certificate_config.json"

        default_images = {
            "pint_logo": project_root / "static" / "pint_logo.png",
            "pint_signature": project_root / "static" / "pint_signature.png",
            "sponsor_logo": project_root / "static" / "sponsor_logo.png",
        }

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    all_configs = json.load(f)

                    # Tentar buscar configuração do ano específico
                    ano_key = str(evento_ano)
                    if ano_key in all_configs and "imagens" in all_configs[ano_key]:
                        images_config = all_configs[ano_key]["imagens"]
                        return {
                            key: project_root
                            / "static"
                            / images_config.get(key, default_images[key].name)
                            for key in default_images.keys()
                        }

                    # Fallback para configuração padrão
                    if (
                        "_default" in all_configs
                        and "imagens" in all_configs["_default"]
                    ):
                        images_config = all_configs["_default"]["imagens"]
                        return {
                            key: project_root
                            / "static"
                            / images_config.get(key, default_images[key].name)
                            for key in default_images.keys()
                        }
        except Exception as e:
            logger.warning(
                f"Erro ao carregar paths de imagens para ano {evento_ano}: {e}"
            )

        return default_images

    def _obter_nome_coordenador_geral(self) -> str:
        """Obtém o nome do primeiro superadmin cadastrado."""
        try:
            with db_manager.get_db_session() as session:
                from app.db import get_coordenador_repository

                coord_repo = get_coordenador_repository(session)

                # Buscar o primeiro superadmin
                superadmin = coord_repo.get_first_superadmin()

                if superadmin:
                    return superadmin.nome.upper()
                else:
                    # Fallback caso não haja superadmin
                    logger.warning("Nenhum superadmin encontrado, usando nome padrão")
                    return "COORDENADOR GERAL"
        except Exception as e:
            logger.error(f"Erro ao buscar coordenador geral: {e}")
            return "COORDENADOR GERAL"

    def gerar_certificado_pdf(
        self, participante: Participante, evento: Evento, cidade: Cidade, funcao: Funcao
    ) -> bytes:
        """
        Gera um certificado PDF para um participante em formato A4 landscape.

        Args:
            participante: Objeto Participante com dados validados
            evento: Objeto Evento
            cidade: Objeto Cidade
            funcao: Objeto Funcao

        Returns:
            Bytes do PDF gerado
        """
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader

            # Descriptografar dados sensíveis
            nome_completo = self._servico_criptografia.descriptografar(
                participante.nome_completo_encrypted
            )
            email = self._servico_criptografia.descriptografar(
                participante.email_encrypted
            )

            # Gerar hash de validação se ainda não existe
            if not participante.hash_validacao:
                hash_validacao = (
                    self._servico_criptografia.gerar_hash_validacao_certificado(
                        participante.id, evento.id, email, nome_completo
                    )
                )
                # Atualizar no banco
                with db_manager.get_db_session() as session:
                    participante_db = session.merge(participante)
                    participante_db.hash_validacao = hash_validacao
                    session.commit()
                    # Atualizar objeto local
                    participante.hash_validacao = hash_validacao
            else:
                hash_validacao = participante.hash_validacao

            # Carregar configuração de cores e imagens para o ano do evento
            cores = self._carregar_configuracao_cores(evento.ano)
            caminhos_imagens = self._carregar_caminhos_imagens(evento.ano)

            # Criar buffer para o PDF
            buffer = BytesIO()

            # Configurar página A4 landscape (297mm x 210mm = 841.89 x 595.27 points)
            page_width, page_height = landscape(A4)

            # Criar canvas
            c = canvas.Canvas(buffer, pagesize=landscape(A4))

            # Definir dimensões da coluna lateral (30% da largura)
            sidebar_width = page_width * 0.30
            content_x_start = sidebar_width + 30  # 30 points de margem

            # ========== COLUNA LATERAL ESQUERDA (LARANJA) ==========
            c.setFillColor(colors.HexColor(cores["cor_primaria"]))
            c.rect(0, 0, sidebar_width, page_height, fill=1, stroke=0)

            # Logo do patrocinador (se existir)
            sponsor_logo_path = caminhos_imagens["sponsor_logo"]
            if sponsor_logo_path.exists():
                try:
                    # Ajustar imagem para ocupar toda a altura da coluna lateral
                    img_reader = ImageReader(str(sponsor_logo_path))
                    img_width, img_height = img_reader.getSize()

                    # Calcular dimensões - ALTURA FIXA = altura da página
                    new_height = page_height  # Altura total da página
                    max_width = sidebar_width  # - 20 - 20 # margem de 20 em cada lado

                    # Calcular largura mantendo aspect ratio
                    ratio = new_height / img_height
                    new_width = img_width * ratio

                    # Se a largura calculada exceder o máximo, ajustar pela largura
                    if new_width > max_width:
                        new_width = max_width
                        new_height = (img_height * new_width) / img_width

                    # Centralizar horizontalmente, alinhar verticalmente
                    x = (sidebar_width - new_width) / 2
                    y = (page_height - new_height) / 2

                    c.drawImage(
                        str(sponsor_logo_path),
                        x,
                        y,
                        width=new_width,
                        height=new_height,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                except Exception as e:
                    logger.warning(f"Erro ao carregar logo do patrocinador: {e}")

            # ========== ÁREA DE CONTEÚDO ==========

            # Logo Pint of Science (canto superior direito)
            pint_logo_path = caminhos_imagens["pint_logo"]
            if pint_logo_path.exists():
                try:
                    logo_size = 80  # tamanho do logo
                    c.drawImage(
                        str(pint_logo_path),
                        page_width - logo_size - 30,  # 30 points da margem direita
                        page_height - logo_size - 30,  # 30 points da margem superior
                        width=logo_size,
                        height=logo_size,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                except Exception as e:
                    logger.warning(f"Erro ao carregar logo Pint: {e}")

            # Título principal
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.HexColor(cores["cor_secundaria"]))
            title_y = page_height - 100
            # Calcular centro da área de conteúdo (excluindo sidebar e área do logo)
            content_center_x = content_x_start + (
                (page_width - content_x_start - 120) / 2
            )  # 120 = espaço do logo + margem
            c.drawCentredString(
                content_center_x,
                title_y,
                "CERTIFICADO DE PARTICIPAÇÃO",
            )

            # Subtítulo
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(colors.HexColor(cores["cor_texto"]))
            c.drawCentredString(
                content_center_x,
                title_y - 45,
                f"Pint of Science Brasil - {evento.ano}",
            )

            # ========== TEXTO PRINCIPAL (SEM QUEBRAS DE LINHA) ==========
            y_position = title_y - 110
            c.setFont("Helvetica", 14)
            c.setFillColor(colors.HexColor(cores["cor_texto"]))

            # Formatar datas de participação
            datas_participacao_str = participante.datas_participacao
            if "," in datas_participacao_str:
                # Multiple dates
                datas_list = [d.strip() for d in datas_participacao_str.split(",")]
                # Format ISO dates to DD/MM/YYYY
                datas_formatadas = []
                for data in datas_list:
                    try:
                        dt = datetime.fromisoformat(data)
                        datas_formatadas.append(dt.strftime("%d/%m/%Y"))
                    except:
                        datas_formatadas.append(data)

                if len(datas_formatadas) > 1:
                    datas_texto = " e ".join(
                        [", ".join(datas_formatadas[:-1]), datas_formatadas[-1]]
                    )
                else:
                    datas_texto = datas_formatadas[0]
            else:
                try:
                    dt = datetime.fromisoformat(datas_participacao_str.strip())
                    datas_texto = dt.strftime("%d/%m/%Y")
                except:
                    datas_texto = datas_participacao_str

            # Calcular carga horária on-the-fly usando configuração
            carga_horaria, _ = servico_calculo_carga_horaria.calcular_carga_horaria(
                participante.datas_participacao,
                evento.datas_evento,
                evento.ano,
                participante.funcao_id,
            )

            # Construir o texto completo do certificado em uma linha fluida
            # Calcular a largura disponível
            max_width = page_width - content_x_start - 60
            x_current = content_x_start + 20

            # Função auxiliar para desenhar texto com alternância de estilos
            def desenhar_texto_fluido(canvas, x, y, texto, bold=False, cor=None):
                """Desenha texto e retorna a nova posição X."""
                if bold:
                    canvas.setFont("Helvetica-Bold", 14)
                else:
                    canvas.setFont("Helvetica", 14)

                if cor:
                    canvas.setFillColor(colors.HexColor(cor))

                canvas.drawString(x, y, texto)
                return x + canvas.stringWidth(texto, canvas._fontname, 14)

            # Construir o parágrafo completo
            partes = [
                ("Certificamos que ", False, cores["cor_texto"]),
                (nome_completo, True, cores["cor_destaque"]),
                (" participou como ", False, cores["cor_texto"]),
                (funcao.nome_funcao, True, cores["cor_destaque"]),
                (
                    " do Pint of Science Brasil, realizado na cidade de ",
                    False,
                    cores["cor_texto"],
                ),
                (f" {cidade.nome} - {cidade.estado}", True, cores["cor_destaque"]),
                (", no(s) dia(s) ", False, cores["cor_texto"]),
                (datas_texto, True, cores["cor_destaque"]),
                (", com carga horária de ", False, cores["cor_texto"]),
                (
                    f"{carga_horaria} horas",
                    True,
                    cores["cor_destaque"],
                ),
                (".", False, cores["cor_texto"]),
            ]

            # Quebrar em linhas com suporte a wordwrap inteligente
            linha_atual = []
            linhas = []
            largura_linha = 0

            for texto, bold, cor in partes:
                # Calcular largura do texto
                fonte = "Helvetica-Bold" if bold else "Helvetica"
                largura_texto = c.stringWidth(texto, fonte, 14)

                # Se o texto atual cabe na linha, adiciona
                if largura_linha + largura_texto <= max_width or not linha_atual:
                    linha_atual.append((texto, bold, cor))
                    largura_linha += largura_texto
                else:
                    # Texto não cabe. Verificar se precisa quebrar por palavras
                    if " " in texto.strip() and largura_texto > max_width * 0.6:
                        # Texto muito longo, quebrar por palavras
                        palavras = texto.split()
                        texto_parcial = ""

                        for palavra in palavras:
                            teste = (
                                texto_parcial + " " + palavra
                                if texto_parcial
                                else palavra
                            )
                            largura_teste = c.stringWidth(teste, fonte, 14)

                            # Se cabe na linha atual com o que já tem
                            if largura_linha + largura_teste <= max_width:
                                texto_parcial = teste
                            else:
                                # Não cabe. Salvar linha atual se tiver conteúdo
                                if linha_atual:
                                    linhas.append(linha_atual)
                                    linha_atual = []
                                    largura_linha = 0

                                # Adicionar o que já foi construído (se houver)
                                if texto_parcial:
                                    linha_atual.append((texto_parcial, bold, cor))
                                    largura_linha = c.stringWidth(
                                        texto_parcial, fonte, 14
                                    )
                                    # Nova linha
                                    linhas.append(linha_atual)
                                    linha_atual = []
                                    largura_linha = 0
                                    texto_parcial = ""

                                # Começar com a palavra atual
                                texto_parcial = palavra

                        # Adicionar resto do texto parcial
                        if texto_parcial:
                            largura_parcial = c.stringWidth(texto_parcial, fonte, 14)
                            if largura_linha + largura_parcial <= max_width:
                                linha_atual.append((texto_parcial, bold, cor))
                                largura_linha += largura_parcial
                            else:
                                if linha_atual:
                                    linhas.append(linha_atual)
                                linha_atual = [(texto_parcial, bold, cor)]
                                largura_linha = largura_parcial
                    else:
                        # Salvar linha atual e começar nova
                        linhas.append(linha_atual)
                        linha_atual = [(texto, bold, cor)]
                        largura_linha = largura_texto

            # Adicionar última linha
            if linha_atual:
                linhas.append(linha_atual)

            # Desenhar todas as linhas
            for linha in linhas:
                x_current = content_x_start + 20
                for texto, bold, cor in linha:
                    x_current = desenhar_texto_fluido(
                        c, x_current, y_position, texto, bold, cor
                    )
                y_position -= 25  # Próxima linha

            # ========== TÍTULO DA APRESENTAÇÃO (SE HOUVER) ==========
            if participante.titulo_apresentacao:
                y_position -= 15  # Espaço extra antes do título
                c.setFont("Helvetica-Bold", 12)
                c.setFillColor(colors.HexColor(cores["cor_texto"]))
                c.drawString(
                    content_x_start + 20, y_position, "Título da apresentação:"
                )

                y_position -= 20
                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(colors.HexColor(cores["cor_destaque"]))
                # Quebrar título se for muito longo
                max_width = page_width - content_x_start - 120
                if (
                    c.stringWidth(participante.titulo_apresentacao, "Helvetica", 14)
                    > max_width
                ):
                    # Quebrar em palavras
                    palavras = participante.titulo_apresentacao.split()
                    linha = ""
                    for palavra in palavras:
                        teste = linha + " " + palavra if linha else palavra
                        if c.stringWidth(teste, "Helvetica-Oblique", 12) <= max_width:
                            linha = teste
                        else:
                            c.drawString(content_x_start + 20, y_position, linha)
                            y_position -= 15
                            linha = palavra
                    if linha:
                        c.drawString(content_x_start + 20, y_position, linha)
                else:
                    c.drawString(
                        content_x_start + 20,
                        y_position,
                        participante.titulo_apresentacao,
                    )

            # Data de emissão
            y_position -= 50
            c.setFont("Helvetica", 11)
            c.setFillColor(colors.HexColor(cores["cor_texto"]))
            data_emissao = datetime.now().strftime("%d de %B de %Y")
            # Traduzir mês para português
            meses_pt = {
                "January": "Janeiro",
                "February": "Fevereiro",
                "March": "Março",
                "April": "Abril",
                "May": "Maio",
                "June": "Junho",
                "July": "Julho",
                "August": "Agosto",
                "September": "Setembro",
                "October": "Outubro",
                "November": "Novembro",
                "December": "Dezembro",
            }
            for en, pt in meses_pt.items():
                data_emissao = data_emissao.replace(en, pt)

            c.drawCentredString(
                content_center_x,
                y_position,
                f"Emitido em {data_emissao}.",
            )

            # Assinatura (se existir)
            signature_path = caminhos_imagens["pint_signature"]
            if signature_path.exists():
                try:
                    sig_width = 200
                    sig_height = 60
                    sig_x = content_center_x - sig_width / 2
                    sig_y = 95  # Aumentado de 80 para 95 para dar mais espaço ao rodapé

                    c.drawImage(
                        str(signature_path),
                        sig_x,
                        sig_y,
                        width=sig_width,
                        height=sig_height,
                        preserveAspectRatio=True,
                        mask="auto",
                    )

                    # Nome do coordenador geral IMEDIATAMENTE abaixo da assinatura
                    nome_coordenador = self._obter_nome_coordenador_geral()
                    c.setFont("Helvetica", 9)
                    c.setFillColor(colors.HexColor(cores["cor_texto"]))
                    # Reduzido espaço de -10 para -5 (mais próximo)
                    c.drawCentredString(content_center_x, sig_y - 5, nome_coordenador)
                    # Reduzido espaço de -22 para -17 (mais próximo)
                    c.drawCentredString(
                        content_center_x,
                        sig_y - 17,
                        "Coordenador Geral - Pint of Science Brasil",
                    )
                except Exception as e:
                    logger.warning(f"Erro ao carregar assinatura: {e}")

            # Rodapé
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(colors.HexColor("#7f8c8d"))
            footer_text = "“Levando a ciência para o bar”"
            c.drawCentredString(content_center_x, 50, footer_text)

            # Link de validação
            validation_url = (
                f"{settings.base_url}/Validar_Certificado?hash={hash_validacao}"
            )
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor("#2980b9"))
            c.drawCentredString(
                content_center_x,
                35,
                "Valide a autenticidade deste certificado em:",
            )

            # Tornar o link clicável
            c.setFillColor(colors.HexColor("#3498db"))
            c.setFont("Helvetica", 6)
            # Calcular largura aproximada do link para centralização do hitbox
            link_width = c.stringWidth(validation_url, "Helvetica", 6)
            link_x_start = content_center_x - (link_width / 2)
            link_x_end = content_center_x + (link_width / 2)

            c.linkURL(
                validation_url,
                (
                    link_x_start,
                    18,
                    link_x_end,
                    28,
                ),
                relative=0,
            )
            c.drawCentredString(content_center_x, 22, validation_url)

            # Finalizar PDF
            c.save()

            # Retornar bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"✅ Certificado PDF gerado para {nome_completo}")
            return pdf_bytes

        except Exception as e:
            logger.error(f"❌ Erro ao gerar certificado PDF: {e}")
            raise ValueError("Erro ao gerar certificado")

    def gerar_nome_arquivo_certificado(self, evento_ano: int) -> str:
        """Gera um nome único para o arquivo do certificado."""
        uuid_curto = str(uuid.uuid4())[:8]
        return f"Certificado-PintOfScience-{evento_ano}-{uuid_curto}.pdf"


class ServicoValidacao:
    """Serviço para validação de regras de negócio."""

    def __init__(self):
        self._servico_criptografia = ServicoCriptografia()
        self._servico_calculo = ServicoCalculoCargaHoraria()

    def validar_inscricao(
        self, dados: ParticipanteCreate, evento: Evento
    ) -> Tuple[bool, str]:
        """
        Valida uma inscrição de participante.

        Args:
            dados: Dados da inscrição
            evento: Evento correspondente

        Returns:
            Tupla com (valido, mensagem_erro)
        """
        try:
            # Validar email duplicado no mesmo evento
            with db_manager.get_db_session() as session:
                participante_repo = get_participante_repository(session)

                email_hash = self._servico_criptografia.gerar_hash_email(dados.email)
                existing = participante_repo.get_by_email_hash(email_hash, evento.id)

                if existing:
                    return False, "Este email já está inscrito neste evento"

            # Validar datas de participação
            if not self._servico_calculo.validar_datas_participacao(
                dados.datas_participacao, evento.datas_evento
            ):
                return False, "Datas de participação inválidas para este evento"

            # Validar carga horária mínima
            carga_horaria, _ = self._servico_calculo.calcular_carga_horaria(
                dados.datas_participacao,
                evento.datas_evento,
                evento.ano,
                dados.funcao_id,
            )

            if carga_horaria == 0:
                return False, "Carga horária inválida para as datas informadas"

            return True, "Inscrição válida"

        except Exception as e:
            logger.error(f"❌ Erro ao validar inscrição: {e}")
            return False, "Erro na validação da inscrição"

    def validar_download_certificado(
        self, email: str, evento_id: int
    ) -> Tuple[bool, Optional[ParticipanteRead], str]:
        """
        Valida se um usuário pode baixar certificado.

        Args:
            email: Email do participante
            evento_id: ID do evento

        Returns:
            Tupla com (pode_baixar, participante, mensagem)
        """
        try:
            with db_manager.get_db_session() as session:
                participante_repo = get_participante_repository(session)
                evento_repo = get_evento_repository(session)

                # Buscar participante
                email_hash = self._servico_criptografia.gerar_hash_email(email)
                participante = participante_repo.get_by_email_hash(
                    email_hash, evento_id
                )

                if not participante:
                    return (
                        False,
                        None,
                        "Email não encontrado ou não inscrito neste evento",
                    )

                # Verificar se está validado
                if not participante.validado:
                    return (
                        False,
                        None,
                        "Sua participação ainda não foi validada pelos coordenadores",
                    )

                # Buscar dados relacionados
                evento = evento_repo.get_by_id(Evento, evento_id)
                if not evento:
                    return False, None, "Evento não encontrado"

                # Criar objeto de leitura
                participante_read = ParticipanteRead(
                    id=participante.id,
                    nome_completo=self._servico_criptografia.descriptografar(
                        participante.nome_completo_encrypted
                    ),
                    email=self._servico_criptografia.descriptografar(
                        participante.email_encrypted
                    ),
                    titulo_apresentacao=participante.titulo_apresentacao,
                    evento_id=participante.evento_id,
                    cidade_id=participante.cidade_id,
                    funcao_id=participante.funcao_id,
                    datas_participacao=participante.datas_participacao,
                    carga_horaria_calculada=servico_calculo_carga_horaria.calcular_carga_horaria(
                        participante.datas_participacao,
                        evento.datas_evento,
                        evento.ano,
                        participante.funcao_id,
                    ),
                    validado=participante.validado,
                    data_inscricao=participante.data_inscricao,
                )

                return True, participante_read, "Certificado disponível para download"

        except Exception as e:
            logger.error(f"❌ Erro ao validar download: {e}")
            return False, None, "Erro ao validar download do certificado"


# ============= INSTÂNCIAS GLOBAIS =============

servico_criptografia = ServicoCriptografia()
servico_calculo_carga_horaria = ServicoCalculoCargaHoraria()
servico_email = ServicoEmail()
gerador_certificado = GeradorCertificado()
servico_validacao = ServicoValidacao()


# ============= FUNÇÕES DE CONVENIÊNCIA =============


def inscrever_participante(
    dados_inscricao: ParticipanteCreate,
) -> Tuple[bool, str, Optional[int]]:
    """
    Função de conveniência para inscrever um participante.

    Args:
        dados_inscricao: Dados completos da inscrição

    Returns:
        Tupla com (sucesso, mensagem, participante_id)
    """
    try:
        # Validar dados
        with db_manager.get_db_session() as session:
            evento_repo = get_evento_repository(session)
            evento = evento_repo.get_by_id(Evento, dados_inscricao.evento_id)

            if not evento:
                return False, "Evento não encontrado", None

            valido, mensagem = servico_validacao.validar_inscricao(
                dados_inscricao, evento
            )
            if not valido:
                return False, mensagem, None

            # Criptografar dados sensíveis
            nome_criptografado = servico_criptografia.criptografar_nome(
                dados_inscricao.nome_completo
            )
            email_criptografado = servico_criptografia.criptografar_email(
                dados_inscricao.email
            )
            email_hash = servico_criptografia.gerar_hash_email(dados_inscricao.email)

            # Calcular carga horária
            carga_horaria, _ = servico_calculo_carga_horaria.calcular_carga_horaria(
                dados_inscricao.datas_participacao,
                evento.datas_evento,
                evento.ano,
                dados_inscricao.funcao_id,
            )

            print(f"DEBUG: Criando participante...")
            # Criar participante
            participante_repo = get_participante_repository(session)
            participante = participante_repo.create_participante(
                nome_completo_encrypted=nome_criptografado,
                email_encrypted=email_criptografado,
                email_hash=email_hash,
                titulo_apresentacao=dados_inscricao.titulo_apresentacao,
                evento_id=dados_inscricao.evento_id,
                cidade_id=dados_inscricao.cidade_id,
                funcao_id=dados_inscricao.funcao_id,
                datas_participacao=dados_inscricao.datas_participacao,
                validado=False,  # Inicia como não validado
            )

            # Enviar e-mail de confirmação
            if servico_email.is_configured():
                cidade_repo = get_cidade_repository(session)
                funcao_repo = get_funcao_repository(session)

                cidade = cidade_repo.get_by_id(Cidade, dados_inscricao.cidade_id)
                funcao = funcao_repo.get_by_id(Funcao, dados_inscricao.funcao_id)

                dados_email = {
                    "evento_ano": evento.ano,
                    "cidade_nome": (
                        f"{cidade.nome}-{cidade.estado}" if cidade else "N/A"
                    ),
                    "funcao_nome": funcao.nome_funcao if funcao else "N/A",
                    "datas_participacao": dados_inscricao.datas_participacao,
                    "carga_horaria": carga_horaria,
                }

                servico_email.enviar_email_confirmacao_inscricao(
                    dados_inscricao.nome_completo, dados_inscricao.email, dados_email
                )

            logger.info(f"✅ Participante inscrito: {dados_inscricao.email}")
            return True, "Inscrição realizada com sucesso!", participante.id

    except Exception as e:
        logger.error(f"❌ Erro ao inscrever participante: {e}")
        return False, f"Erro ao realizar inscrição: {str(e)}", None


def baixar_certificado(email: str, evento_id: int) -> Tuple[bool, Optional[bytes], str]:
    """
    Função de conveniência para baixar certificado.

    Args:
        email: Email do participante
        evento_id: ID do evento

    Returns:
        Tupla com (sucesso, pdf_bytes, mensagem)
    """
    try:
        # Validar download
        pode_baixar, participante, mensagem = (
            servico_validacao.validar_download_certificado(email, evento_id)
        )

        if not pode_baixar:
            return False, None, mensagem

        # Buscar dados relacionados
        with db_manager.get_db_session() as session:
            evento_repo = get_evento_repository(session)
            cidade_repo = get_cidade_repository(session)
            funcao_repo = get_funcao_repository(session)
            participante_repo = get_participante_repository(session)

            evento = evento_repo.get_by_id(Evento, evento_id)
            cidade = cidade_repo.get_by_id(Cidade, participante.cidade_id)
            funcao = funcao_repo.get_by_id(Funcao, participante.funcao_id)
            participante_db = participante_repo.get_by_id(Participante, participante.id)

            if not all([evento, cidade, funcao, participante_db]):
                return False, None, "Dados incompletos para gerar certificado"

            # Gerar PDF
            pdf_bytes = gerador_certificado.gerar_certificado_pdf(
                participante_db, evento, cidade, funcao
            )

            logger.info(f"✅ Certificado baixado por: {email}")
            return True, pdf_bytes, "Certificado gerado com sucesso!"

    except Exception as e:
        logger.error(f"❌ Erro ao baixar certificado: {e}")
        return False, None, f"Erro ao gerar certificado: {str(e)}"


def validar_participantes(
    participante_ids: List[int], validados: List[bool]
) -> Tuple[bool, str]:
    """
    Função para validar múltiplos participantes.

    Args:
        participante_ids: Lista de IDs dos participantes
        validados: Lista de status de validação correspondentes

    Returns:
        Tupla com (sucesso, mensagem)
    """
    try:
        if len(participante_ids) != len(validados):
            return False, "Listas de IDs e status devem ter o mesmo tamanho"

        current_user = get_current_user_info()
        if not current_user:
            return False, "Usuário não autenticado"

        with db_manager.get_db_session() as session:
            participante_repo = get_participante_repository(session)
            auditoria_repo = get_auditoria_repository(session)

            success_count = 0
            error_count = 0

            for i, participante_id in enumerate(participante_ids):
                try:
                    participante = participante_repo.get_by_id(
                        Participante, participante_id
                    )
                    if not participante:
                        error_count += 1
                        continue

                    # Atualizar validação
                    novo_status = validados[i]
                    status_anterior = participante.validado

                    if status_anterior != novo_status:
                        participante.validado = novo_status
                        session.merge(participante)

                        # Registrar auditoria
                        acao = (
                            "VALIDATE_PARTICIPANTE"
                            if novo_status
                            else "INVALIDATE_PARTICIPANTE"
                        )
                        detalhes = f"Participante {participante_id} {'validado' if novo_status else 'invalidado'}"

                        auditoria_repo.create_audit_log(
                            coordenador_id=current_user["id"],
                            acao=acao,
                            detalhes=detalhes,
                        )

                        # Enviar e-mail se validado
                        if novo_status and servico_email.is_configured():
                            try:
                                nome = servico_criptografia.descriptografar(
                                    participante.nome_completo_encrypted
                                )
                                email = servico_criptografia.descriptografar(
                                    participante.email_encrypted
                                )

                                # Vamos usar o BASE_URL para construir o link
                                link_download = f"{settings.base_url}/"

                                servico_email.enviar_email_certificado_liberado(
                                    nome, email, link_download
                                )
                            except Exception as e:
                                logger.warning(
                                    f"⚠️ Não foi possível enviar e-mail de certificado: {e}"
                                )

                        success_count += 1
                    else:
                        # Status não mudou
                        success_count += 1

                except Exception as e:
                    logger.error(
                        f"❌ Erro ao validar participante {participante_id}: {e}"
                    )
                    error_count += 1

            mensagem = f"Processados {success_count + error_count} participantes. "
            if success_count > 0:
                mensagem += f"{success_count} atualizados com sucesso. "
            if error_count > 0:
                mensagem += f"{error_count} erros."

            logger.info(f"✅ Validação em lote concluída: {mensagem}")
            return True, mensagem

    except Exception as e:
        logger.error(f"❌ Erro ao validar participantes: {e}")
        return False, f"Erro ao processar validação: {str(e)}"
