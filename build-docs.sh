#!/bin/bash
# Script para construir a documentação do Sistema Pint of Science Brasil

echo "🚀 Construindo documentação MkDocs..."
echo ""

# Verificar se mkdocs está instalado
if ! command -v mkdocs &> /dev/null; then
    echo "❌ MkDocs não encontrado!"
    echo "📦 Instalando dependências..."
    pip install mkdocs-material mkdocs-with-pdf
fi

# Menu de opções
echo "Escolha uma opção:"
echo "1) Servir localmente (http://localhost:8000)"
echo "2) Construir site estático"
echo "3) Construir site + PDF"
echo "4) Limpar build anterior"
echo ""
read -p "Opção (1-4): " option

case $option in
    1)
        echo "🌐 Iniciando servidor local..."
        mkdocs serve
        ;;
    2)
        echo "🔨 Construindo site estático..."
        mkdocs build
        echo "✅ Site gerado em: site/"
        ;;
    3)
        echo "🔨 Construindo site com PDF..."
        ENABLE_PDF_EXPORT=1 mkdocs build
        echo "✅ Site gerado em: site/"
        echo "📄 PDF gerado em: site/pdf/manual-usuario-pint-of-science.pdf"
        ;;
    4)
        echo "🧹 Limpando build anterior..."
        rm -rf site/
        echo "✅ Build limpo!"
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "✨ Concluído!"
