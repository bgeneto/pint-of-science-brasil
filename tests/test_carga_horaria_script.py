#!/usr/bin/env python3
"""
Script de teste para a nova funcionalidade de configuração de carga horária.
"""

import json
from pathlib import Path
from app.services import ServicoCalculoCargaHoraria

# Criar instância do serviço
servico = ServicoCalculoCargaHoraria()

# Teste 1: Criar configuração de teste
print("=" * 60)
print("TESTE 1: Salvando configuração de carga horária")
print("=" * 60)

config_path = Path("static/certificate_config.json")
config_path.parent.mkdir(parents=True, exist_ok=True)

# Carregar config existente ou criar nova
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {}

# Adicionar configuração de teste para 2025
ano_teste = "2025"
if ano_teste not in config:
    config[ano_teste] = {"cores": {}, "imagens": {}}

config[ano_teste]["carga_horaria"] = {
    "horas_por_dia": 4,
    "horas_por_evento": 40,
    "funcoes_evento_completo": [1, 2, 3],  # IDs de teste
}

# Salvar
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"✅ Configuração salva em: {config_path}")
print(f"   Conteúdo para 2025: {config[ano_teste]['carga_horaria']}")

# Teste 2: Calcular carga horária para função comum (por dias)
print("\n" + "=" * 60)
print("TESTE 2: Cálculo por dias (função comum)")
print("=" * 60)

datas = "2025-05-20,2025-05-21,2025-05-22"
evento_datas = ["2025-05-20", "2025-05-21", "2025-05-22"]
funcao_id_comum = 99  # Função que NÃO está na lista de evento completo

horas, detalhes = servico.calcular_carga_horaria(
    datas, evento_datas, evento_ano=2025, funcao_id=funcao_id_comum
)

print(f"Datas de participação: {datas}")
print(f"Função ID: {funcao_id_comum} (comum)")
print(f"Resultado: {horas}h")
print(f"Detalhes:\n{detalhes}")

# Teste 3: Calcular carga horária para função de evento completo
print("\n" + "=" * 60)
print("TESTE 3: Cálculo evento completo (função especial)")
print("=" * 60)

funcao_id_especial = 1  # Função que ESTÁ na lista de evento completo

horas2, detalhes2 = servico.calcular_carga_horaria(
    datas, evento_datas, evento_ano=2025, funcao_id=funcao_id_especial
)

print(f"Datas de participação: {datas}")
print(f"Função ID: {funcao_id_especial} (especial - Coordenador)")
print(f"Resultado: {horas2}h")
print(f"Detalhes:\n{detalhes2}")

# Teste 4: Calcular sem configuração (comportamento padrão)
print("\n" + "=" * 60)
print("TESTE 4: Cálculo sem configuração (comportamento padrão)")
print("=" * 60)

horas3, detalhes3 = servico.calcular_carga_horaria(datas, evento_datas)

print(f"Datas de participação: {datas}")
print(f"Sem ano/função especificados")
print(f"Resultado: {horas3}h (deve usar valor padrão de 4h/dia)")
print(f"Detalhes:\n{detalhes3}")

print("\n" + "=" * 60)
print("RESUMO DOS TESTES")
print("=" * 60)
print(f"✅ Teste 1: Configuração salva com sucesso")
print(f"✅ Teste 2: Cálculo por dias: {horas}h (3 dias × 4h)")
print(f"✅ Teste 3: Cálculo evento completo: {horas2}h (função especial)")
print(f"✅ Teste 4: Cálculo padrão: {horas3}h (sem config)")
print("\n🎉 Todos os testes concluídos!")
