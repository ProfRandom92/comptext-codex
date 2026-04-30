# ============================================================
# Hermes + CompText Codex — Setup (PowerShell)
# ============================================================
# Voraussetzungen: Git, Python 3.10+, Node 18+, pip

# --- 0. Sicherheitscheck ---
if ((Get-ExecutionPolicy) -eq "Restricted") {
    Write-Host "FEHLER: ExecutionPolicy ist Restricted." -ForegroundColor Red
    Write-Host "Fix: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    exit 1
}

# --- 1. Verzeichnisse anlegen ---
$AI_LAB = "$env:USERPROFILE\ai-lab"
New-Item -ItemType Directory -Force -Path "$AI_LAB\hermes-home" | Out-Null
New-Item -ItemType Directory -Force -Path "$AI_LAB\repos"       | Out-Null
New-Item -ItemType Directory -Force -Path "$AI_LAB\mcp"         | Out-Null
New-Item -ItemType Directory -Force -Path "$AI_LAB\reports"     | Out-Null

# --- 2. Repo klonen ---
Set-Location "$AI_LAB\repos"
if (-Not (Test-Path "comptext-codex")) {
    git clone https://github.com/ProfRandom92/comptext-codex.git
} else {
    Write-Host "Repo existiert bereits — überspringe clone." -ForegroundColor Yellow
}

# --- 3. Python venv erstellen + aktivieren ---
Set-Location "$AI_LAB\repos\comptext-codex"
python -m venv "$AI_LAB\venv-comptext"
& "$AI_LAB\venv-comptext\Scripts\Activate.ps1"

# --- 4. Paket installieren ---
pip install --upgrade pip
pip install -e ".[mcp]"

# --- 5. Installation verifizieren (PYTHONPATH-Diagnose) ---
Write-Host ""
Write-Host "=== Installationspfad-Check ===" -ForegroundColor Cyan
$modPath = python -c "import comptext_codex; print(comptext_codex.__file__)" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Modulpfad: $modPath" -ForegroundColor Green
    if ($modPath -like "*site-packages*") {
        Write-Host "-> Saubere Installation. PYTHONPATH nicht nötig." -ForegroundColor Green
    } elseif ($modPath -like "*src*") {
        Write-Host "-> Editable install. PYTHONPATH redundant." -ForegroundColor Green
    }
} else {
    Write-Host "-> FEHLER: Modul nicht gefunden. venv korrekt aktiviert?" -ForegroundColor Red
    exit 1
}

python -c "from comptext_codex.mcp_server_v5 import create_server; print('MCP import OK')"
if ($LASTEXITCODE -ne 0) { exit 1 }

# CLI-Script testen
comptext-mcp --help | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNUNG: comptext-mcp CLI nicht gefunden. pyproject.toml scripts prüfen." -ForegroundColor Yellow
}

# --- 6. Tests laufen lassen ---
pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "FEHLER: Tests fehlgeschlagen. Nicht mergen!" -ForegroundColor Red
    exit 1
}

# --- 7. Hermes installieren (Node 18+ vorausgesetzt) ---
$nodeVer = node --version 2>$null
if ($nodeVer) {
    Write-Host "Node-Version: $nodeVer" -ForegroundColor Green
    npm install -g @nousresearch/hermes-agent
    hermes --version
} else {
    Write-Host "Node.js nicht gefunden. Bitte installieren: https://nodejs.org" -ForegroundColor Red
    exit 1
}

# --- 8. Constitution-Files in hermes-home kopieren ---
Copy-Item "$AI_LAB\repos\comptext-codex\SOUL.md"     "$AI_LAB\hermes-home\SOUL.md"     -Force
Copy-Item "$AI_LAB\repos\comptext-codex\.hermes.md"  "$AI_LAB\hermes-home\.hermes.md"  -Force

# --- 9. MCP-Config aus Template erstellen ---
Copy-Item "$AI_LAB\repos\comptext-codex\integrations\hermes\mcp-config.example.json" `
          "$AI_LAB\mcp\hermes-mcp.json" -Force

# Platzhalter automatisch ersetzen
(Get-Content "$AI_LAB\mcp\hermes-mcp.json") `
    -replace "YOUR_USER", $env:USERNAME `
    | Set-Content "$AI_LAB\mcp\hermes-mcp.json"

# --- 10. Abschluss ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP ABGESCHLOSSEN" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "JETZT BEARBEITEN: $AI_LAB\mcp\hermes-mcp.json"
Write-Host "  -> YOUR_PAT_HERE ersetzen durch deinen GitHub PAT"
Write-Host "  (YOUR_USER wurde bereits automatisch auf '$env:USERNAME' gesetzt)"
Write-Host ""
Write-Host "Dann starten:"
Write-Host "  cd $AI_LAB\hermes-home"
Write-Host "  hermes --mcp-config $AI_LAB\mcp\hermes-mcp.json"
Write-Host ""
Write-Host "Erster Prompt:"
Write-Host "  > Read SOUL.md and .hermes.md, then summarize your operating parameters."
Write-Host ""
Write-Host "venv bei jedem neuen Terminal reaktivieren:"
Write-Host "  & $AI_LAB\venv-comptext\Scripts\Activate.ps1"
