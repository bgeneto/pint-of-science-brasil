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


class ServicoCalculoCargaHoraria:
    """Serviço para cálculo de carga horária de participação."""

    def __init__(self):
        self._duracao_padrao_evento = 4  # 4 horas por dia de evento

    def calcular_carga_horaria(
        self, datas_participacao: str, evento_datas
    ) -> Tuple[int, str]:
        """
        Calcula a carga horária com base nas datas de participação.

        Args:
            datas_participacao: String com datas ISO separadas por vírgula
            evento_datas: Lista de strings ISO ou string (formato antigo)

        Returns:
            Tupla com (carga_horaria_total, detalhes_calculo)
        """
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

            # Calcular dias únicos de participação
            dias_unicos = set()
            for data in dias_participacao:
                if data in dias_evento:
                    dias_unicos.add(data)

            # Calcular carga horária
            carga_horaria = len(dias_unicos) * self._duracao_padrao_evento

            detalhes = (
                f"Dias de participação: {len(dias_unicos)} ({', '.join(sorted(dias_unicos))})\n"
                f"Carga horária por dia: {self._duracao_padrao_evento}h\n"
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
                            <li>Aguarde a validação da sua participação pelos organizadores</li>
                            <li>Após sua apresentação, você receberá um e-mail com instruções para download de seu certificado</li>
                            <li>Qualquer dúvida, entre em contato com os organizadores da sua cidade</li>
                        </ol>
                    </div>

                    <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #e8f4f8; border-radius: 8px;">
                        <p style="margin: 0;">
                            <em>"Levando a ciência para o bar"</em>
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">
                            Pint of Science Brasil
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
                            <em>"Levando a ciência para o bar"</em>
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #666;">
                            Pint of Science Brasil
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

    def gerar_certificado_pdf(
        self, participante: Participante, evento: Evento, cidade: Cidade, funcao: Funcao
    ) -> bytes:
        """
        Gera um certificado PDF para um participante.

        Args:
            participante: Objeto Participante com dados validados
            evento: Objeto Evento
            cidade: Objeto Cidade
            funcao: Objeto Funcao

        Returns:
            Bytes do PDF gerado
        """
        try:
            # Descriptografar dados sensíveis
            nome_completo = self._servico_criptografia.descriptografar(
                participante.nome_completo_encrypted
            )
            email = self._servico_criptografia.descriptografar(
                participante.email_encrypted
            )

            # Criar buffer para o PDF
            buffer = BytesIO()

            # Criar documento
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#e74c3c"),
            )

            subtitle_style = ParagraphStyle(
                "CustomSubtitle",
                parent=styles["Heading2"],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2c3e50"),
            )

            normal_style = ParagraphStyle(
                "CustomNormal",
                parent=styles["Normal"],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_CENTER,
            )

            # Construir conteúdo
            content = []

            # Título
            content.append(Paragraph("CERTIFICADO DE PARTICIPAÇÃO", title_style))
            content.append(Spacer(1, 20))

            # Subtítulo
            content.append(
                Paragraph(f"Pint of Science Brasil - {evento.ano}", subtitle_style)
            )
            content.append(Spacer(1, 30))

            # Texto principal
            texto_certificado = f"""
            Certificamos que <b>{nome_completo}</b> participou do evento
            <b>Pint of Science Brasil {evento.ano}</b> na cidade de <b>{cidade.nome}-{cidade.estado}</b>,
            com a função de <b>{funcao.nome_funcao}</b>.
            """
            content.append(Paragraph(texto_certificado, normal_style))
            content.append(Spacer(1, 20))

            # Detalhes da participação
            detalhes_data = [
                ["Período do Evento:", evento.datas_evento],
                ["Datas de Participação:", participante.datas_participacao],
                [
                    "Carga Horária Total:",
                    f"{participante.carga_horaria_calculada} horas",
                ],
                ["Função Exercida:", funcao.nome_funcao],
            ]

            if participante.titulo_apresentacao:
                detalhes_data.append(
                    ["Título da Apresentação:", participante.titulo_apresentacao]
                )

            tabela_detalhes = Table(detalhes_data, colWidths=[3 * inch, 3 * inch])
            tabela_detalhes.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                        ("BACKGROUND", (0, 0), (0, -1), colors.grey),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.whitesmoke),
                    ]
                )
            )

            content.append(tabela_detalhes)
            content.append(Spacer(1, 30))

            # Data de emissão
            data_emissao = datetime.now().strftime("%d de %B de %Y")
            content.append(Paragraph(f"Emitido em {data_emissao}", normal_style))
            content.append(Spacer(1, 40))

            # Rodapé
            rodape_style = ParagraphStyle(
                "Rodape",
                parent=styles["Normal"],
                fontSize=10,
                spaceAfter=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#7f8c8d"),
            )

            content.append(
                Paragraph("Organização: Pint of Science Brasil", rodape_style)
            )
            content.append(
                Paragraph(
                    "Este certificado tem validade digital e pode ser verificado online.",
                    rodape_style,
                )
            )
            content.append(Paragraph('"Levando a ciência para o bar"', rodape_style))

            # Gerar PDF
            doc.build(content)

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

                email_criptografado = self._servico_criptografia.criptografar_email(
                    dados.email
                )
                existing = participante_repo.get_by_encrypted_email(
                    email_criptografado, evento.id
                )

                if existing:
                    return False, "Este email já está inscrito neste evento"

            # Validar datas de participação
            if not self._servico_calculo.validar_datas_participacao(
                dados.datas_participacao, evento.datas_evento
            ):
                return False, "Datas de participação inválidas para este evento"

            # Validar carga horária mínima
            carga_horaria, _ = self._servico_calculo.calcular_carga_horaria(
                dados.datas_participacao, evento.datas_evento
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
                email_criptografado = self._servico_criptografia.criptografar_email(
                    email
                )
                participante = participante_repo.get_by_encrypted_email(
                    email_criptografado, evento_id
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
                        "Sua participação ainda não foi validada pelos organizadores",
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
                    carga_horaria_calculada=participante.carga_horaria_calculada,
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

            # Calcular carga horária
            carga_horaria, _ = servico_calculo_carga_horaria.calcular_carga_horaria(
                dados_inscricao.datas_participacao, evento.datas_evento
            )

            print(f"DEBUG: Criando participante...")
            # Criar participante
            participante_repo = get_participante_repository(session)
            participante = participante_repo.create_participante(
                nome_completo_encrypted=nome_criptografado,
                email_encrypted=email_criptografado,
                titulo_apresentacao=dados_inscricao.titulo_apresentacao,
                evento_id=dados_inscricao.evento_id,
                cidade_id=dados_inscricao.cidade_id,
                funcao_id=dados_inscricao.funcao_id,
                datas_participacao=dados_inscricao.datas_participacao,
                carga_horaria_calculada=carga_horaria,
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

                                # Aqui você implementaria a geração do link de download
                                link_download = (
                                    f"https://seusite.com/download/{participante_id}"
                                )

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
