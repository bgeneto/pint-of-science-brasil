#!/usr/bin/env python3
"""
Script para gerar chave secreta para validação de certificados

Este script gera uma chave HMAC segura de 64 caracteres (256 bits)
que deve ser adicionada ao arquivo .env como CERTIFICATE_SECRET_KEY
"""

import secrets


def gerar_chave_certificado():
    """Gera uma chave secreta segura para HMAC."""
    return secrets.token_hex(32)  # 32 bytes = 64 caracteres hex


if __name__ == "__main__":
    print("=" * 70)
    print("Gerador de Chave Secreta para Validação de Certificados")
    print("=" * 70)
    print()
    print("Adicione a linha abaixo ao seu arquivo .env:")
    print()
    chave = gerar_chave_certificado()
    print(f"CERTIFICATE_SECRET_KEY={chave}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Esta chave é ÚNICA e deve ser mantida em SEGREDO")
    print("   - NÃO compartilhe esta chave publicamente")
    print("   - NÃO versione esta chave no Git")
    print("   - Se perder esta chave, todos os certificados perderão validade")
    print("   - Use a MESMA chave em todos os ambientes (dev, prod)")
    print()
    print("=" * 70)
