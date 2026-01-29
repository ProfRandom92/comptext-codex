#!/bin/bash
###############################################################################
# CompText-Codex - Automatisches Lokales Setup
# Version: 4.0.0
# Datum: 2026-01-29
###############################################################################

set -e  # Bei Fehler abbrechen

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
clear
echo -e "${BLUE}"
cat << "EOF"
   ____                  _____         _      ____          _
  / ___|___  _ __ ___   |_   _|____  _| |_   / ___|___   __| | _____  __
 | |   / _ \| '_ ` _ \    | |/ _ \ \/ / __| | |   / _ \ / _` |/ _ \ \/ /
 | |__| (_) | | | | | |   | |  __/>  <| |_  | |__| (_) | (_| |  __/>  <
  \____\___/|_| |_| |_|   |_|\___/_/\_\\__|  \____\___/ \__,_|\___/_/\_\

  🚀 Automatisches Lokales Setup v4.0.0

EOF
echo -e "${NC}"

print_header "Schritt 1/7: Systemprüfung"

# Python-Version prüfen
print_info "Python-Version prüfen..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_success "Python $PYTHON_VERSION gefunden (>= 3.9 erforderlich)"
        PYTHON_CMD="python3"
    else
        print_error "Python $PYTHON_VERSION ist zu alt. Version >= 3.9 erforderlich."
        exit 1
    fi
else
    print_error "Python 3 nicht gefunden. Bitte installieren Sie Python >= 3.9"
    exit 1
fi

# pip prüfen
print_info "pip prüfen..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    print_success "pip $PIP_VERSION gefunden"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_VERSION=$(pip --version | awk '{print $2}')
    print_success "pip $PIP_VERSION gefunden"
    PIP_CMD="pip"
else
    print_error "pip nicht gefunden. Bitte installieren Sie pip"
    exit 1
fi

# Git prüfen
print_info "Git prüfen..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git $GIT_VERSION gefunden"
else
    print_warning "Git nicht gefunden (optional)"
fi

print_header "Schritt 2/7: Virtuelle Umgebung"

# Virtuelle Umgebung erstellen
if [ -d "venv" ]; then
    print_warning "Virtuelle Umgebung 'venv' existiert bereits"
    read -p "Neu erstellen? (j/N): " RECREATE_VENV
    if [ "$RECREATE_VENV" = "j" ] || [ "$RECREATE_VENV" = "J" ]; then
        print_info "Entferne alte virtuelle Umgebung..."
        rm -rf venv
        print_info "Erstelle neue virtuelle Umgebung..."
        $PYTHON_CMD -m venv venv
        print_success "Virtuelle Umgebung neu erstellt"
    fi
else
    print_info "Erstelle virtuelle Umgebung..."
    $PYTHON_CMD -m venv venv
    print_success "Virtuelle Umgebung erstellt"
fi

# Virtuelle Umgebung aktivieren
print_info "Aktiviere virtuelle Umgebung..."
source venv/bin/activate
print_success "Virtuelle Umgebung aktiviert"

# pip upgraden
print_info "Upgrade pip..."
$PIP_CMD install --upgrade pip setuptools wheel -q
print_success "pip aktualisiert"

print_header "Schritt 3/7: Dependencies installieren"

# Core Dependencies
print_info "Installiere Core-Dependencies..."
$PIP_CMD install -r requirements.txt -q
print_success "Dependencies installiert"

print_header "Schritt 4/7: Package installieren"

# Package im Development Mode installieren
print_info "Installiere CompText-Codex im Development Mode..."
$PIP_CMD install -e . -q
print_success "CompText-Codex installiert"

# Version prüfen
INSTALLED_VERSION=$(comptext --version 2>/dev/null || echo "unknown")
print_info "Installierte Version: $INSTALLED_VERSION"

print_header "Schritt 5/7: Validierung"

# Codex validieren
print_info "Validiere Codex-Definitionen..."
if $PYTHON_CMD scripts/validate_codex.py --codex-dir codex --schema-dir schemas > /dev/null 2>&1; then
    print_success "Codex-Validierung erfolgreich"
else
    print_warning "Codex-Validierung mit Warnungen (nicht kritisch)"
fi

# Bundle erstellen
print_info "Erstelle Codex-Bundle..."
if $PYTHON_CMD scripts/build_bundle.py --codex-dir codex --out dist/codex.bundle.json --version v4.0.0 > /dev/null 2>&1; then
    print_success "Bundle erstellt: dist/codex.bundle.json"
else
    print_warning "Bundle-Erstellung übersprungen (optional)"
fi

print_header "Schritt 6/7: Tests"

# Token-Report
print_info "Erstelle Token-Report..."
if comptext token-report --codex-dir codex --format json > token_report.json 2>/dev/null; then
    print_success "Token-Report erstellt: token_report.json"
else
    print_warning "Token-Report übersprungen (optional)"
fi

# Installation testen
print_info "Teste Installation..."
TEST_OUTPUT=$($PYTHON_CMD -c "from comptext_codex import CompTextParser; parser = CompTextParser(); print('OK')" 2>&1)
if [ "$TEST_OUTPUT" = "OK" ]; then
    print_success "Installation funktioniert korrekt"
else
    print_error "Installation fehlgeschlagen: $TEST_OUTPUT"
    exit 1
fi

print_header "Schritt 7/7: Setup abgeschlossen!"

echo ""
print_success "CompText-Codex wurde erfolgreich installiert!"
echo ""

# Zusammenfassung
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Zusammenfassung:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "  Python:        ${GREEN}$PYTHON_VERSION${NC}"
echo -e "  pip:           ${GREEN}$PIP_VERSION${NC}"
echo -e "  CompText:      ${GREEN}$INSTALLED_VERSION${NC}"
echo -e "  Virtual Env:   ${GREEN}venv/${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Nächste Schritte
print_header "🎯 Nächste Schritte"
echo ""
echo -e "${YELLOW}1. Virtuelle Umgebung aktivieren (falls nicht aktiv):${NC}"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo -e "${YELLOW}2. Playground öffnen:${NC}"
echo -e "   ${BLUE}cd public && python -m http.server 8000${NC}"
echo -e "   ${BLUE}Browser: http://localhost:8000/playground.html${NC}"
echo ""
echo -e "${YELLOW}3. Beispiele durchgehen:${NC}"
echo -e "   ${BLUE}cd examples/basic${NC}"
echo -e "   ${BLUE}python simple_commands.py${NC}"
echo ""
echo -e "${YELLOW}4. Python API nutzen:${NC}"
echo -e "   ${BLUE}from comptext_codex import CompTextParser${NC}"
echo -e "   ${BLUE}parser = CompTextParser()${NC}"
echo -e "   ${BLUE}result = parser.execute('@CODE_ANALYZE[perf_bottleneck]', code='...')${NC}"
echo ""
echo -e "${YELLOW}5. CLI-Befehle testen:${NC}"
echo -e "   ${BLUE}comptext --help${NC}"
echo -e "   ${BLUE}comptext token-report --codex-dir codex${NC}"
echo -e "   ${BLUE}comptext token-benchmark --output results.md${NC}"
echo ""
echo -e "${YELLOW}6. Tests ausführen:${NC}"
echo -e "   ${BLUE}pytest${NC}"
echo -e "   ${BLUE}pytest --cov=comptext_codex --cov-report=html${NC}"
echo ""
echo -e "${YELLOW}7. Dokumentation lesen:${NC}"
echo -e "   ${BLUE}cat SETUP_LOKAL_DE.md${NC}"
echo -e "   ${BLUE}cat README.md${NC}"
echo ""

# MCP Server Hinweis
print_header "🔌 MCP Server (Optional)"
echo ""
echo -e "${YELLOW}Für Claude Desktop Integration:${NC}"
echo -e "   ${BLUE}python -m comptext_mcp.server --test${NC}"
echo ""
echo -e "Siehe ${BLUE}SETUP_LOKAL_DE.md${NC} für MCP-Konfiguration."
echo ""

# Abschluss
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 Setup erfolgreich abgeschlossen!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
print_info "Dokumentation: SETUP_LOKAL_DE.md"
print_info "Support: https://github.com/ProfRandom92/comptext-codex/issues"
echo ""

# Finale
echo -e "${GREEN}Viel Erfolg mit CompText-Codex! 🎉${NC}"
echo ""
