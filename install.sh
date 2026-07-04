#!/bin/bash

# TF Tracker - Installation script for macOS / Linux

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${RED}  ████████╗███████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗${NC}"
echo -e "${RED}     ██║   ██╔════╝       ██║   ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗${NC}"
echo -e "${RED}     ██║   █████╗         ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝${NC}"
echo -e "${RED}     ██║   ██╔══╝         ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗${NC}"
echo -e "${RED}     ██║   ██║            ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║${NC}"
echo ""
echo "  Installation startar..."
echo "  ================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
echo "  [1/4] Kontrollerar Python..."
if command -v python3 &>/dev/null; then
    PYVER=$(python3 --version)
    echo -e "  ${GREEN}OK${NC} - $PYVER"
else
    echo -e "  ${RED}FEL: Python 3 hittades inte.${NC}"
    echo "  Installera Python från: https://www.python.org/downloads/"
    exit 1
fi

# Install dependencies
echo ""
echo "  [2/4] Installerar Flask och ReportLab..."
python3 -m pip install flask reportlab --quiet --disable-pip-version-check
if [ $? -ne 0 ]; then
    echo -e "  ${RED}FEL: Kunde inte installera paket.${NC}"
    exit 1
fi
echo -e "  ${GREEN}OK${NC} - Flask och ReportLab installerade"

# Seed database
echo ""
echo "  [3/4] Skapar databas med alla Transformers-figurer..."
echo "yes" | python3 seed.py > /dev/null 2>&1
echo -e "  ${GREEN}OK${NC} - Databas klar"

# Make start.sh executable
chmod +x start.sh

# Create desktop shortcut (macOS)
echo ""
echo "  [4/4] Skapar genväg..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    DESKTOP="$HOME/Desktop"
    APP_SCRIPT="$DESKTOP/TF Tracker.command"
    echo "#!/bin/bash" > "$APP_SCRIPT"
    echo "cd \"$SCRIPT_DIR\"" >> "$APP_SCRIPT"
    echo "python3 app.py" >> "$APP_SCRIPT"
    chmod +x "$APP_SCRIPT"
    echo -e "  ${GREEN}OK${NC} - Genväg skapad på skrivbordet (TF Tracker.command)"
else
    echo -e "  ${YELLOW}INFO${NC} - Kör 'bash start.sh' för att starta appen"
fi

# Done
echo ""
echo "  ================================================"
echo -e "  ${GREEN}INSTALLATION KLAR!${NC}"
echo "  ================================================"
echo ""
echo "  Starta appen med:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  → Dubbelklicka på 'TF Tracker' på skrivbordet"
    echo "  → Eller kör: bash start.sh"
else
    echo "  → bash start.sh"
fi
echo ""
echo "  Appen öppnas på: http://localhost:5000"
echo ""

read -p "  Starta TF Tracker nu? (j/n): " START
if [[ "$START" == "j" || "$START" == "J" ]]; then
    python3 app.py
fi
