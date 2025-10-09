"""
Utilitários Gerais

Este módulo contém funções utilitárias usadas em todo o sistema,
incluindo validação de email, geração de UUID, formatação de datas,
e outras funções auxiliares.
"""

import re
import uuid
from datetime import datetime
from typing import Optional


def validar_email(email: str) -> bool:
    """
    Valida se um endereço de email está em formato válido.

    Args:
        email: Email a ser validado

    Returns:
        True se válido, False caso contrário
    """
    if not email or not isinstance(email, str):
        return False

    # Padrão de validação de email
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(padrao, email.strip()) is not None


def gerar_uuid_curto() -> str:
    """
    Gera um UUID curto para uso em nomes de arquivos e identificadores.

    Returns:
        String com UUID de 8 caracteres
    """
    return str(uuid.uuid4())[:8]


def formatar_data_iso(data: datetime) -> str:
    """
    Formata uma data para o padrão ISO 8601.

    Args:
        data: Objeto datetime

    Returns:
        String no formato ISO 8601
    """
    return data.isoformat()


def formatar_data_exibicao(data_iso: str) -> str:
    """
    Formata uma data ISO para exibição amigável.

    Args:
        data_iso: Data em formato ISO

    Returns:
        String formatada para exibição
    """
    try:
        data = datetime.fromisoformat(data_iso)
        return data.strftime("%d/%m/%Y %H:%M")
    except (ValueError, AttributeError):
        return data_iso


def limpar_texto(texto: str) -> str:
    """
    Remove espaços extras e normaliza texto.

    Args:
        texto: Texto a ser limpo

    Returns:
        Texto limpo e normalizado
    """
    if not texto:
        return ""

    return texto.strip()


def extrair_iniciais(nome: str) -> str:
    """
    Extrai as iniciais de um nome.

    Args:
        nome: Nome completo

    Returns:
        String com as iniciais em maiúsculas
    """
    if not nome:
        return ""

    palavras = nome.strip().split()
    iniciais = [palavra[0].upper() for palavra in palavras if palavra]
    return "".join(iniciais)


def mascarar_email(email: str) -> str:
    """
    Mascara um email para exibição parcial.

    Args:
        email: Email completo

    Returns:
        Email mascarado (ex: jo***@email.com)
    """
    if not email or "@" not in email:
        return email

    local, dominio = email.split("@", 1)

    if len(local) <= 2:
        mascarado = local[0] + "***" if len(local) > 1 else "***"
    else:
        mascarado = local[0] + "*" * (len(local) - 2) + local[-1]

    return f"{mascarado}@{dominio}"


def validar_cpf_cnpj(documento: str) -> bool:
    """
    Valida se um CPF ou CNPJ está em formato válido.

    Args:
        documento: CPF ou CNPJ a ser validado

    Returns:
        True se válido, False caso contrário
    """
    if not documento:
        return False

    # Remover caracteres não numéricos
    numeros = re.sub(r"\D", "", documento)

    # Validar CPF (11 dígitos)
    if len(numeros) == 11:
        return _validar_cpf(numeros)

    # Validar CNPJ (14 dígitos)
    elif len(numeros) == 14:
        return _validar_cnpj(numeros)

    return False


def _validar_cpf(cpf: str) -> bool:
    """Validação interna de CPF."""
    # CPFs inválidos conhecidos
    if cpf == cpf[0] * 11:
        return False

    # Cálculo dos dígitos verificadores
    def calcular_digito(cpf_parcial: str, peso: int) -> int:
        soma = sum(int(d) * peso for d, peso in zip(cpf_parcial, range(peso, 1, -1)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Verificar primeiro dígito
    primeiro_digito = calcular_digito(cpf[:9], 10)
    if int(cpf[9]) != primeiro_digito:
        return False

    # Verificar segundo dígito
    segundo_digito = calcular_digito(cpf[:10], 11)
    if int(cpf[10]) != segundo_digito:
        return False

    return True


def _validar_cnpj(cnpj: str) -> bool:
    """Validação interna de CNPJ."""
    # CNPJs inválidos conhecidos
    if cnpj == cnpj[0] * 14:
        return False

    # Cálculo dos dígitos verificadores
    def calcular_digito(cnpj_parcial: str, pesos: list) -> int:
        soma = sum(int(d) * peso for d, peso in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos primeiro dígito
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    primeiro_digito = calcular_digito(cnpj[:12], pesos1)

    # Pesos segundo dígito
    pesos2 = [6] + pesos1
    segundo_digito = calcular_digito(cnpj[:13], pesos2)

    # Verificar dígitos
    return int(cnpj[12]) == primeiro_digito and int(cnpj[13]) == segundo_digito


def formatar_telefone(telefone: str) -> str:
    """
    Formata um número de telefone para exibição.

    Args:
        telefone: Número de telefone

    Returns:
        Telefone formatado
    """
    if not telefone:
        return ""

    # Remover caracteres não numéricos
    numeros = re.sub(r"\D", "", telefone)

    # Formatar celular com DDD
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"

    # Formatar telefone fixo com DDD
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

    # Formatar sem DDD
    elif len(numeros) == 8 or len(numeros) == 9:
        if len(numeros) == 9:
            return f"{numeros[:5]}-{numeros[5:]}"
        else:
            return f"{numeros[:4]}-{numeros[4:]}"

    # Retornar original se não conseguir formatar
    return telefone


def gerar_codigo_verificacao(tamanho: int = 6) -> str:
    """
    Gera um código de verificação numérico.

    Args:
        tamanho: Quantidade de dígitos do código

    Returns:
        String com código numérico
    """
    import random

    return "".join(str(random.randint(0, 9)) for _ in range(tamanho))


def calcular_porcentagem(parcial: int, total: int) -> float:
    """
    Calcula porcentagem de forma segura.

    Args:
        parcial: Valor parcial
        total: Valor total

    Returns:
        Porcentagem calculada
    """
    if total == 0:
        return 0.0

    return round((parcial / total) * 100, 2)


def truncar_texto(texto: str, limite: int = 100, sufixo: str = "...") -> str:
    """
    Trunca um texto se exceder o limite especificado.

    Args:
        texto: Texto a ser truncado
        limite: Limite de caracteres
        sufixo: Sufixo a ser adicionado se truncado

    Returns:
        Texto truncado ou original
    """
    if not texto or len(texto) <= limite:
        return texto

    return texto[: limite - len(sufixo)] + sufixo


def normalizar_string(texto: str) -> str:
    """
    Normaliza uma string removendo acentos e caracteres especiais.

    Args:
        texto: Texto a ser normalizado

    Returns:
        String normalizada
    """
    if not texto:
        return ""

    import unicodedata

    # Remover acentos
    texto_normalizado = unicodedata.normalize("NFD", texto)
    texto_sem_acentos = "".join(
        char for char in texto_normalizado if unicodedata.category(char) != "Mn"
    )

    # Converter para minúsculas e manter apenas alfanuméricos
    return re.sub(r"[^a-zA-Z0-9\s]", "", texto_sem_acentos.lower())


def validar_cep(cep: str) -> bool:
    """
    Valida se um CEP está em formato válido.

    Args:
        cep: CEP a ser validado

    Returns:
        True se válido, False caso contrário
    """
    if not cep:
        return False

    # Remover caracteres não numéricos
    numeros = re.sub(r"\D", "", cep)

    # CEP válido tem 8 dígitos
    return len(numeros) == 8


def formatar_cep(cep: str) -> str:
    """
    Formata um CEP para exibição.

    Args:
        cep: CEP a ser formatado

    Returns:
        CEP formatado (XXXXX-XXX)
    """
    if not cep:
        return ""

    numeros = re.sub(r"\D", "", cep)

    if len(numeros) == 8:
        return f"{numeros[:5]}-{numeros[5:]}"

    return cep


def gerar_hash_simples(texto: str) -> str:
    """
    Gera um hash simples para identificação.

    Args:
        texto: Texto para gerar hash

    Returns:
        String com hash
    """
    import hashlib

    if not texto:
        return ""

    return hashlib.md5(texto.encode()).hexdigest()[:16]


def validar_url(url: str) -> bool:
    """
    Valida se uma URL está em formato válido.

    Args:
        url: URL a ser validada

    Returns:
        True se válida, False caso contrário
    """
    if not url:
        return False

    padrao = r"^https?:\/\/(?:[-\w.])+(?:[:\d]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$"
    return re.match(padrao, url.strip()) is not None


def converter_bytes_para_humanos(bytes_val: int) -> str:
    """
    Converte bytes para formato legível por humanos.

    Args:
        bytes_val: Valor em bytes

    Returns:
        String formatada (ex: "1.5 MB")
    """
    if bytes_val == 0:
        return "0 B"

    unidades = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while bytes_val >= 1024 and i < len(unidades) - 1:
        bytes_val /= 1024.0
        i += 1

    return f"{bytes_val:.1f} {unidades[i]}"


def gerar_cor_aleatoria() -> str:
    """
    Gera uma cor hexadecimal aleatória.

    Returns:
        String com cor hexadecimal
    """
    import random

    return f"#{random.randint(0, 0xFFFFFF):06x}"
