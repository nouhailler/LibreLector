# LibreLector

> Lecteur EPUB open-source avec synthèse vocale neuronale offline pour Linux

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![GTK4](https://img.shields.io/badge/GTK-4.0-orange.svg)](https://gtk.org)
[![Piper TTS](https://img.shields.io/badge/TTS-Piper-purple.svg)](https://github.com/rhasspy/piper)

LibreLector est un lecteur de livres numériques conçu **prioritairement pour l'écoute**.
Contrairement aux lecteurs visuels classiques (Foliate, Calibre…), l'audio est au cœur de l'expérience :
voix naturelles hors-ligne via **Piper**, surlignage synchronisé phrase par phrase,
navigation intuitive et export MP3.

---

## Fonctionnalités

| Fonctionnalité | État |
|---|---|
| Ouverture et lecture de fichiers EPUB | ✅ |
| Affichage du texte avec surlignage synchronisé | ✅ |
| Voix neuronale offline via Piper TTS | ✅ |
| Voix système via Speech Dispatcher (fallback) | ✅ |
| Lecture / Pause / Arrêt | ✅ |
| Navigation par chapitres | ✅ |
| Démarrage de la lecture par double-clic sur une phrase | ✅ |
| Réglage de la vitesse et du volume | ✅ |
| Mémorisation automatique de la position | ✅ |
| Bibliothèque avec dossiers thématiques | ✅ |
| Dictionnaire de prononciation personnalisé | ✅ |
| Lecture continue multi-chapitres | ✅ |
| Export MP3 par chapitre via FFmpeg | ✅ |
| Interface GTK4 / Libadwaita | ✅ |

---

## Installation rapide (paquet .deb)

```bash
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_2.0.0_amd64.deb
sudo dpkg -i librelector_2.0.0_amd64.deb
sudo apt install -f
```

Puis ouvrir un terminal et lancer :

```bash
librelector
```

L'interface s'ouvre dans votre navigateur à l'adresse `http://localhost:7531`.

Pour la voix française naturelle (Piper) :

```bash
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

Puis configurer la voix depuis l'interface via le bouton **⚙ Paramètres**.

Voir [INSTALL.md](INSTALL.md) pour les instructions complètes et [docs/GUIDE_UTILISATEUR.md](docs/GUIDE_UTILISATEUR.md) pour la documentation complète.

---

## Interface

```
┌──────────────────────┬────────────────────────────────────────────┐
│  Bibliothèque    📁+ +│  Titre du livre — Auteur              ☰   │
│                      │                                            │
│  ▼ Histoire          │  Chapitre 1 ──── En étudiant              │
│    📕 Livre A        │  Chapitre 2      l'imagination des         │
│    📗 Livre B   ···  │  Chapitre 3 ◀── foules, nous avons vu     │
│  ▶ Roman             │  Chapitre 4      ████████████████          │
│  ▼ Sans dossier      │                 (phrase surlignée)         │
│    📘 Livre C   ···  │                                            │
│                      │  ⏮   ▶   ⏹   ⏭    Vitesse 1.00  🔊───●  │
└──────────────────────┴────────────────────────────────────────────┘
```

---

## Architecture

```
src/librelector/
├── epub/
│   ├── models.py             # EpubBook, EpubChapter, TextSegment
│   └── parser.py             # ZIP → OPF → HTML → texte → segments
├── tts/
│   ├── base.py               # TTSEngine (classe abstraite)
│   ├── piper.py              # Piper (voix neuronales offline)
│   ├── speech_dispatcher.py  # Speech Dispatcher (fallback)
│   └── factory.py            # Sélection automatique du moteur
├── core/
│   ├── player.py             # Orchestrateur principal
│   ├── exporter.py           # Export MP3 via FFmpeg
│   └── pronunciation.py      # Dictionnaire de prononciation JSON
├── data/
│   ├── library.py            # Gestionnaire SQLite
│   └── models.py             # BookRecord, Folder, ReadingProgress
├── ui/
│   ├── application.py        # Adw.Application
│   ├── window.py             # Fenêtre principale
│   ├── library_view.py       # Sidebar bibliothèque + dossiers
│   ├── reader_view.py        # Zone de lecture + contrôles
│   ├── export_dialog.py      # Dialogue export MP3
│   └── settings_dialog.py    # Paramètres TTS
└── main.py                   # Point d'entrée
```

---

## Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite (livres, dossiers, progression)
├── settings.json        # Préférences (moteur TTS, modèle Piper, langue)
├── pronunciation.json   # Dictionnaire de prononciation personnalisé
└── voices/              # Modèles Piper (.onnx + .onnx.json)
```

---

## Feuille de route

- **v1.0** — Interface React + API FastAPI, bibliothèque, TTS Piper ✅
- **v2.0** — Correction chargement EPUB et panneau paramètres ✅
- **v2.1** — Mode podcast, navigation intelligente
- **v3.0** — Packaging Flatpak / AppImage

---

## Contribuer

Les contributions sont les bienvenues.
Ouvrez une [issue](https://github.com/nouhailler/LibreLector/issues) ou soumettez une [pull request](https://github.com/nouhailler/LibreLector/pulls).

---

## Licence

GNU General Public License v3.0 — voir [LICENSE](LICENSE).
