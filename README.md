# 📖 LibreLector

> **Lecteur EPUB open-source avec synthèse vocale neuronale offline pour Linux**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![GTK4](https://img.shields.io/badge/GTK-4.0-orange.svg)](https://gtk.org)
[![Piper TTS](https://img.shields.io/badge/TTS-Piper-purple.svg)](https://github.com/rhasspy/piper)

LibreLector est un lecteur de livres numériques conçu **prioritairement pour l'écoute**.
Contrairement aux lecteurs visuels classiques (Foliate, Calibre…), l'audio est au cœur de l'expérience :
voix naturelles hors-ligne via **Piper**, surlignage synchronisé phrase par phrase,
navigation intuitive et export MP3.

---

## ✨ Fonctionnalités

| | Fonctionnalité | État |
|---|---|---|
| 📚 | Ouverture / parsing EPUB | ✅ |
| 📄 | Affichage texte (GTK4 TextView) | ✅ |
| 🎙️ | TTS Piper (offline neuronal) | ✅ |
| 🔊 | TTS Speech Dispatcher (fallback) | ✅ |
| ▶️ | Play / Pause / Stop | ✅ |
| 📑 | Navigation chapitres | ✅ |
| 🖱️ | Clic pour démarrer la lecture à une phrase | ✅ |
| 🔡 | Vitesse et volume réglables | ✅ |
| 💾 | Mémorisation de la position | ✅ |
| 🟡 | Surlignage phrase synchronisé | ✅ |
| 🗂️ | Bibliothèque SQLite | ✅ |
| 🗣️ | Dictionnaire de prononciation | ✅ |
| 🔁 | Lecture continue multi-chapitres | ✅ |
| 🎨 | Interface GTK4 / Libadwaita | ✅ |
| 🎵 | Export audio MP3 via FFmpeg | ✅ |
| 🌙 | Mode podcast / écran éteint | 🔜 |
| 📦 | Packaging Flatpak / AppImage | 🔜 |

---

## 🖼️ Interface

```
┌─────────────────┬──────────────────────────────────────────┐
│  📚 Bibliothèque │  📖 Titre du livre — Auteur              │
│                 │                                          │
│  ┌───────────┐  │  Chapitre 1    En étudiant               │
│  │ 📕 Livre1 │  │  Chapitre 2    l'imagination des         │
│  │ 📗 Livre2 │  │  Chapitre 3 ◀  foules, nous avons vu     │
│  └───────────┘  │  Chapitre 4    ██████████████████        │
│                 │  Chapitre 5    (phrase surlignée 🟡)      │
│  [+] Ajouter    │                                          │
│                 │  ⏮  ▶  ⏹  ⏭   Vitesse: 1.00  🔊 ────●  │
└─────────────────┴──────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
src/librelector/
├── 📂 epub/
│   ├── models.py             # EpubBook, EpubChapter, TextSegment
│   └── parser.py             # ZIP → OPF → HTML → plain text → segments
├── 📂 tts/
│   ├── base.py               # TTSEngine (classe abstraite)
│   ├── piper.py              # 🎙️ Piper (voix neuronales offline)
│   ├── speech_dispatcher.py  # 🔊 Speech Dispatcher (fallback)
│   └── factory.py            # Sélection automatique du moteur
├── 📂 core/
│   ├── player.py             # Orchestrateur principal
│   ├── exporter.py           # 🎵 Export MP3 via FFmpeg
│   └── pronunciation.py      # Dictionnaire de prononciation JSON
├── 📂 data/
│   ├── library.py            # Gestionnaire SQLite
│   └── models.py             # BookRecord, ReadingProgress, Bookmark
├── 📂 ui/
│   ├── application.py        # Adw.Application
│   ├── window.py             # Fenêtre principale
│   ├── library_view.py       # Sidebar bibliothèque
│   ├── reader_view.py        # Zone de lecture + contrôles
│   ├── export_dialog.py      # 🎵 Dialogue export MP3
│   └── settings_dialog.py    # ⚙️ Paramètres
└── main.py                   # Point d'entrée CLI
```

---

## 🚀 Installation

### 1. Dépendances système

```bash
# GTK4 + Libadwaita
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# WebKitGTK (optionnel, rendu HTML riche)
sudo apt install gir1.2-webkit-6.0

# Speech Dispatcher (TTS fallback)
sudo apt install speech-dispatcher

# aplay (lecture audio raw pour Piper)
sudo apt install alsa-utils

# FFmpeg (export MP3)
sudo apt install ffmpeg
```

### 2. 🎙️ Piper — voix neuronales offline (recommandé)

```bash
# Télécharger le binaire Piper
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
mv piper/piper ~/.local/bin/

# Télécharger la voix française (siwis — qualité naturelle)
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

> 💡 D'autres voix disponibles sur [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)

### 3. LibreLector

```bash
git clone https://github.com/nouhailler/LibreLector.git
cd LibreLector
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -e .
```

---

## 🎮 Utilisation

```bash
# Lancer l'interface graphique
librelector

# Ouvrir directement un fichier EPUB
librelector mon_livre.epub
```

### ⚙️ Configuration Piper (première utilisation)

Créer le fichier de configuration :

```bash
mkdir -p ~/.local/share/LibreLector
cat > ~/.local/share/LibreLector/settings.json << 'EOF'
{
  "tts_engine": "piper",
  "piper_model": "/home/UTILISATEUR/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr"
}
EOF
```

Ou via l'interface : **☰ → Paramètres**

### 🖱️ Démarrer la lecture à une phrase précise

**Double-clic** sur n'importe quelle phrase dans le texte pour démarrer la lecture à partir de cet endroit.

### 🎵 Exporter un livre en MP3

**☰ → Exporter en MP3** — génère un fichier MP3 par chapitre dans `~/Music/LibreLector/`.

### 🗣️ Dictionnaire de prononciation

```json
// ~/.local/share/LibreLector/pronunciation.json
{
  "LLM": "L L M",
  "Kubernetes": "koubernetesse",
  "GPU": "gépéu"
}
```

---

## 🧪 Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 📁 Données utilisateur

```
~/.local/share/LibreLector/
├── 🗄️  metadata.db          # Bibliothèque SQLite
├── ⚙️  settings.json         # Préférences
├── 🗣️  pronunciation.json    # Dictionnaire de prononciation
└── 📂 voices/               # Modèles Piper (.onnx)
```

---

## 🗺️ Feuille de route

- **v0.1** — MVP : parsing EPUB, TTS Piper, surlignage, bibliothèque ✅
- **v0.2** — Export MP3 via FFmpeg, navigation par clic ✅
- **v0.3** — Mode podcast, navigation intelligente (dialogues, titres)
- **v0.4** — Mode apprentissage langue (répétition de phrases)
- **v0.5** — Packaging Flatpak / AppImage
- **v1.0** — Release stable

---

## 🤝 Contribuer

Les contributions sont les bienvenues !
Ouvrez une [issue](https://github.com/nouhailler/LibreLector/issues) ou soumettez une [pull request](https://github.com/nouhailler/LibreLector/pulls).

---

## 📄 Licence

GNU General Public License v3.0 — voir [LICENSE](LICENSE).
