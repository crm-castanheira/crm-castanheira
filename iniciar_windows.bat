@echo off
echo CRM Castanheira e Reis Advogados Associados
echo ============================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    echo Baixe em: https://python.org
    pause
    exit /b
)

REM Instala dependências se necessário
echo Verificando dependencias...
pip install flask flask-sqlalchemy anthropic --quiet

echo.
echo Iniciando o CRM...
echo Acesse: http://localhost:5000
echo Para encerrar: pressione Ctrl+C
echo.
python app.py

pause
