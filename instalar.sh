#!/bin/bash
# ============================================================
# CRM Castanheira e Reis - Script de Instalação
# ============================================================
echo "🏛️  CRM Castanheira e Reis Advogados Associados"
echo "================================================"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale em: https://python.org"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Cria ambiente virtual
python3 -m venv venv 2>/dev/null || python -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate

# Instala dependências
echo "📦 Instalando dependências..."
pip install flask flask-sqlalchemy anthropic --quiet

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "▶️  Para iniciar: python app.py"
echo "🌐 Acesse:       http://localhost:5000"
echo ""
