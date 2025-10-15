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
echo "2) Construir site estático (HTML)"
echo "3) Construir PDF profissional com WeasyPrint"
echo "4) Construir site + PDF (completo)"
echo "5) Limpar build anterior"
echo ""
read -p "Opção (1-5): " option

case $option in
    1)
        echo "🌐 Iniciando servidor local..."
        mkdocs serve
        ;;
    2)
        echo "🔨 Construindo site estático..."
        mkdocs build --clean
        echo "✅ Site gerado em: site/"
        ;;
    2)
        echo "🔨 Construindo site estático..."
        mkdocs build --clean
        echo "✅ Site gerado em: docs-site/"
        echo "📊 Acessível via Streamlit em: /docs-site/index.html"
        ;;
    3)
        echo "📄 Construindo PDF profissional..."
        # Verificar se o site HTML existe
        if [ ! -d "docs-site" ]; then
            echo "⚠️  Site HTML não encontrado, construindo primeiro..."
            mkdocs build --clean
        fi
        python3 generate_pdf.py
        if [ $? -eq 0 ]; then
            echo "✅ PDF gerado em: docs-site/pdf/manual-completo-pint-brasil.pdf"
            ls -lh docs-site/pdf/manual-completo-pint-brasil.pdf
        else
            echo "❌ Erro ao gerar PDF"
            exit 1
        fi
        ;;
    4)
        echo "🔨 Construindo site + PDF completo..."
        echo "📝 Passo 1: Construindo HTML..."
        mkdocs build --clean
        echo "📄 Passo 2: Gerando PDF..."
        python3 generate_pdf.py
        if [ $? -eq 0 ]; then
            echo "✅ Site gerado em: docs-site/"
            echo "✅ PDF gerado em: docs-site/pdf/manual-completo-pint-brasil.pdf"
            echo "📊 Acessível via Streamlit em: /docs-site/index.html"
            ls -lh docs-site/pdf/manual-completo-pint-brasil.pdf
        else
            echo "❌ Erro ao gerar PDF"
            exit 1
        fi
        ;;
    5)
        echo "🧹 Limpando build anterior..."
        rm -rf docs-site/
        echo "✅ Build limpo!"
        ;;
    4)
        echo "🔨 Construindo site + PDF completo..."
        echo "📝 Passo 1: Construindo HTML..."
        mkdocs build --clean
        echo "📄 Passo 2: Gerando PDF..."
        python3 generate_pdf.py
        if [ $? -eq 0 ]; then
            echo "✅ Site gerado em: site/"
            echo "✅ PDF gerado em: site/pdf/manual-completo.pdf"
            ls -lh site/pdf/manual-completo.pdf
        else
            echo "❌ Erro ao gerar PDF"
            exit 1
        fi
        ;;
    5)
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
