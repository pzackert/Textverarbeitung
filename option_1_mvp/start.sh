#!/bin/bash
# Startup-Script für IFB PROFI

echo "🚀 Starte IFB PROFI..."
echo ""

# Virtuelles Environment aktivieren
echo "📦 Aktiviere Virtual Environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
else
    echo "⚠️ Kein Virtual Environment gefunden!"
fi

# PYTHONPATH setzen
export PYTHONPATH=$PWD

echo "✓ Environment bereit"
echo ""

# Optionen anzeigen
echo "Verfügbare Aktionen:"
echo "  1) Streamlit UI starten"
echo "  2) Integration-Test ausführen"
echo "  3) LM Studio Test"
echo ""

read -p "Wähle eine Option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starte Streamlit UI..."
        streamlit run frontend/app.py
        ;;
    2)
        echo ""
        echo "🧪 Führe Integration-Test aus..."
        python tests/integration/test_workflow.py
        ;;
    3)
        echo ""
        echo "🔌 Teste LM Studio Verbindung..."
        python tests/test_lm_studio.py
        ;;
    *)
        echo "Ungültige Auswahl!"
        ;;
esac
