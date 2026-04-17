<div align="center">

# 📖🔊 LibreLector

### *Votre bibliothèque parle. Vraiment.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/nouhailler/LibreLector/releases)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/nouhailler/LibreLector)
[![React](https://img.shields.io/badge/UI-React%2018-61dafb.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com)

**LibreLector** est un lecteur EPUB open-source qui met l'audio au premier plan.
Voix neuronales **100 % hors-ligne** via Piper, surlignage synchronisé phrase par phrase,
bibliothèque organisée en dossiers — tout ce dont vous avez besoin pour écouter vos livres,
sans cloud, sans abonnement, sans compromis.

</div>

---

## 🖥️ Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LibreLector             + Ouvrir EPUB   ⚙ Paramètres   ? Aide             │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 📚 Bibliothèque  📁+ │  📕 La Psychologie des Foules — Gustave Le Bon      │
│                      ├──────────────────┬──────────────────────────────────┤
│ ▼ 📁 Philosophie     │ Chapitres        │                                  │
│   📗 La République   │                  │  Les individus appartenant à     │
│   📘 Méditations     │ ▶ Chapitre 1     │  ██████████████████████████████  │
│                      │   Chapitre 2     │  une foule organisée forment     │
│ ▼ 📁 Roman           │   Chapitre 3     │  un être nouveau, très différent │
│   📕 Les Misérables  │   Chapitre 4     │  de chacun des individus qui     │
│                      │                  │  la composent.                   │
│ ▼ Sans dossier       │                  │                                  │
│   📙 EPUB test       │                  │                                  │
│                      ├──────────────────┴──────────────────────────────────┤
│                      │ ⏮  ▶  ⏹  ⏭    Vitesse 1.2×  🔊 ──────●──         │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

| Fonctionnalité | Statut |
|---|:---:|
| 📂 Ouverture et lecture de fichiers EPUB | ✅ |
| 🎨 Surlignage synchronisé phrase par phrase | ✅ |
| 🧠 Voix neuronale offline via **Piper TTS** | ✅ |
| 🔁 Fallback automatique via Speech Dispatcher | ✅ |
| ⏯️ Lecture / Pause / Arrêt / Navigation chapitres | ✅ |
| 🖱️ Démarrage par double-clic sur une phrase | ✅ |
| 🎚️ Réglage de la vitesse et du volume | ✅ |
| 💾 Mémorisation automatique de la position | ✅ |
| 📁 Bibliothèque avec dossiers thématiques | ✅ |
| 🗣️ Dictionnaire de prononciation personnalisé | ✅ |
| 🔗 Lecture continue multi-chapitres | ✅ |
| 🎵 Export MP3 par chapitre via FFmpeg | ✅ |

---

## 🏗️ Architecture

LibreLector repose sur un backend **FastAPI** (Python) qui gère le parsing EPUB et la synthèse TTS, exposé via une API REST consommée par une interface **React 18** embarquée dans Tauri.

```
┌─────────────────────────────────────────────────────┐
│                   Interface React 18                │
│   Bibliothèque │ Lecteur │ Contrôles audio          │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼──────────────────────────────┐
│               Backend FastAPI (Python)              │
│  epub/parser  │  tts/piper  │  core/player          │
│  data/library │  core/exporter  │  pronunciation    │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Piper TTS      SQLite DB      EPUB files
  (offline)     (bibliothèque)  (~/.local/…)
```

---

## 🚀 Installation rapide

**1. Télécharger et installer le paquet Debian**

```bash
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_1.0.0_amd64.deb
sudo dpkg -i librelector_1.0.0_amd64.deb && sudo apt install -f
```

**2. Installer la voix française Piper**

```bash
pip3 install piper-tts pathvalidate --break-system-packages
mkdir -p ~/.local/share/LibreLector/voices && cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

**3. Lancer LibreLector**

```bash
librelector
```

> 💡 Sans Piper, LibreLector bascule automatiquement sur **Speech Dispatcher** (voix système).

---

## 🎙️ Configuration Piper

Créez `~/.local/share/LibreLector/settings.json` :

```json
{
  "tts_engine": "piper",
  "piper_model": "/home/VOTRE_USER/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr",
  "speed": 1.0,
  "volume": 1.0
}
```

D'autres voix Piper sont disponibles sur [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices).

---

## 🧑‍💻 Démarrage en mode développement

Ouvrez **deux terminaux** :

**Terminal 1 — Backend Python**
```bash
cd /chemin/vers/LibreLector
pip install -e ".[dev]"
python -m librelector.server
# API disponible sur http://localhost:8000
```

**Terminal 2 — Frontend React + Tauri**
```bash
cd ui
npm install
npm run tauri dev
# Fenêtre Tauri s'ouvre automatiquement
```

---

## 📦 Build du paquet .deb

```bash
bash build.sh
# Génère : packaging/librelector_1.0.0_amd64.deb
```

Le script compile le frontend React, emballe le backend Python et produit un `.deb` prêt à l'installation.

---

## 🗂️ Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite (livres, dossiers, progression)
├── settings.json        # Préférences (moteur TTS, modèle Piper, langue)
├── pronunciation.json   # Dictionnaire de prononciation personnalisé
└── voices/              # Modèles Piper (.onnx + .onnx.json)
```

---

## 🗺️ Feuille de route

| Version | Objectif | Statut |
|:---:|---|:---:|
| v0.1 | MVP : parsing EPUB, TTS Piper, surlignage, bibliothèque | ✅ |
| v0.2 | Export MP3, navigation par clic, dossiers thématiques | ✅ |
| v1.0 | Interface React/Tauri, packaging Debian stable | ✅ |
| v1.1 | Mode podcast (vitesse auto, chapitres en file) | 🔜 |
| v1.2 | Navigation intelligente (marque-pages, recherche texte) | 🔜 |
| v2.0 | Packaging Flatpak / AppImage | 🔜 |

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. **Forkez** le dépôt
2. Créez une branche : `git checkout -b feat/ma-fonctionnalite`
3. Committez vos changements : `git commit -m 'feat: ma fonctionnalité'`
4. Poussez : `git push origin feat/ma-fonctionnalite`
5. Ouvrez une **Pull Request**

Signalez bugs et idées via les [Issues GitHub](https://github.com/nouhailler/LibreLector/issues).

---

## 📚 Documentation

| Ressource | Description |
|---|---|
| [INSTALL.md](INSTALL.md) | Instructions d'installation complètes |
| [docs/GUIDE_UTILISATEUR.md](docs/GUIDE_UTILISATEUR.md) | Guide utilisateur détaillé |
| [docs/](docs/) | Documentation technique |

---

## 📄 Licence

Distribué sous licence **GNU General Public License v3.0** — voir [LICENSE](LICENSE).

<div align="center">

*Fait avec ❤️ pour les amoureux des livres qui préfèrent écouter.*

</div>
