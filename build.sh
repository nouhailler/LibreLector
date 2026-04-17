#!/usr/bin/env bash
# build.sh — construit le paquet .deb LibreLector (React + Tauri)
#
# Prérequis :
#   - Node.js >= 20 et npm
#   - Rust stable (https://rustup.rs)
#   - cargo-tauri : cargo install tauri-cli --version "^2"
#   - libwebkit2gtk-4.1-dev, libgtk-3-dev, libssl-dev, build-essential
#
# Usage :
#   ./build.sh                  # build complet → src-tauri/target/release/bundle/deb/
#   ./build.sh --dev            # mode développement (Vite + Tauri dev)
#   ./build.sh --frontend-only  # build React uniquement

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
UI_DIR="$ROOT/ui"
TAURI_DIR="$ROOT/src-tauri"

# ── helpers ────────────────────────────────────────────────────────────────────

log() { echo "[build.sh] $*"; }
die() { echo "[build.sh] ERREUR : $*" >&2; exit 1; }

check_cmd() {
  command -v "$1" &>/dev/null || die "Commande '$1' introuvable. $2"
}

# ── parse args ─────────────────────────────────────────────────────────────────

DEV=false
FRONTEND_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=true ;;
    --frontend-only) FRONTEND_ONLY=true ;;
  esac
done

# ── checks ─────────────────────────────────────────────────────────────────────

check_cmd node  "Installez Node.js >= 20 : https://nodejs.org"
check_cmd npm   "npm est fourni avec Node.js"
check_cmd cargo "Installez Rust : curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"

if ! cargo tauri --version &>/dev/null; then
  log "Installation de tauri-cli..."
  cargo install tauri-cli --version "^2" --locked
fi

# ── frontend ───────────────────────────────────────────────────────────────────

log "Installation des dépendances npm..."
cd "$UI_DIR"
npm install

if $DEV; then
  log "Mode développement — Vite + Tauri dev"
  cd "$ROOT"
  cargo tauri dev
  exit 0
fi

log "Build du frontend React..."
npm run build

if $FRONTEND_ONLY; then
  log "Frontend React construit dans ui/dist/"
  exit 0
fi

# ── tauri .deb ─────────────────────────────────────────────────────────────────

log "Build Tauri → .deb..."
cd "$ROOT"
cargo tauri build --bundles deb

DEB_PATH=$(find "$TAURI_DIR/target/release/bundle/deb" -name "*.deb" | head -1)
if [ -z "$DEB_PATH" ]; then
  die "Aucun fichier .deb trouvé dans $TAURI_DIR/target/release/bundle/deb/"
fi

log "Paquet .deb généré : $DEB_PATH"
log ""
log "Installation :"
log "  sudo dpkg -i '$DEB_PATH'"
log "  sudo apt install -f"
log ""
log "Puis installer les dépendances Python :"
log "  pip3 install -r requirements.txt --break-system-packages"
log "  # ou via venv :"
log "  python3 -m venv ~/.venv/librelector && ~/.venv/librelector/bin/pip install -r requirements.txt"
