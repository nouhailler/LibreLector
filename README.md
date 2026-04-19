<div align="center">

# 📖🔊 LibreLector

### Lecteur de livres numériques audio-first pour Linux

*Écoutez vos livres avec une voix neuronale naturelle, surlignez, annotez, marquez — le tout hors-ligne.*

[![License: GPL v3](https://img.shields.io/badge/Licence-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/UI-React%2018-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Piper TTS](https://img.shields.io/badge/TTS-Piper%20Neural-8B5CF6)](https://github.com/rhasspy/piper)
[![Last commit](https://img.shields.io/github/last-commit/nouhailler/LibreLector)](https://github.com/nouhailler/LibreLector/commits/main)
[![Release](https://img.shields.io/github/v/release/nouhailler/LibreLector?label=derni%C3%A8re%20release)](https://github.com/nouhailler/LibreLector/releases/latest)

---

**[📦 Télécharger le .deb](https://github.com/nouhailler/LibreLector/releases/latest)** · **[📋 Fonctionnalités](#-fonctionnalités)** · **[⚡ Installation rapide](#-installation)** · **[🏗️ Architecture](#️-architecture)**

</div>

---

## ✨ Qu'est-ce que LibreLector ?

LibreLector transforme vos livres numériques en expérience d'écoute immersive. Contrairement aux lecteurs visuels classiques (Foliate, Calibre…), **l'audio est au cœur de l'expérience** :

- 🧠 **Voix neuronale offline** via [Piper TTS](https://github.com/rhasspy/piper) — qualité naturelle, aucune connexion requise
- 📍 **Surlignage synchronisé** phrase par phrase en temps réel (WebSocket)
- 📚 **Multi-formats** : EPUB, PDF, TXT, FB2
- 🔒 **100 % local** — aucune donnée ne quitte votre machine

L'interface React s'ouvre dans votre navigateur ; un backend FastAPI tourne silencieusement en local.

---

## 🚀 Fonctionnalités

<details open>
<summary><strong>🎵 Lecture audio</strong></summary>

| Fonctionnalité | État |
|---|:---:|
| Voix neuronale offline via **Piper TTS** | ✅ |
| Fallback automatique vers Speech Dispatcher | ✅ |
| Surlignage synchronisé phrase par phrase (WebSocket) | ✅ |
| Clic sur une phrase pour démarrer la lecture à cet endroit | ✅ |
| Lecture / Pause / Arrêt | ✅ |
| Vitesse réglable (0.25× → 4×) | ✅ |
| Volume réglable | ✅ |
| Navigation par chapitres (table des matières) | ✅ |
| Lecture continue multi-chapitres | ✅ |
| Mémorisation automatique de la position | ✅ |
| Export MP3 par chapitre (FFmpeg) | ✅ |

</details>

<details open>
<summary><strong>📝 Annotations</strong></summary>

| Fonctionnalité | État |
|---|:---:|
| **🖊 Surligner** un passage (sauvegardé, bordure orange) | ✅ |
| **📝 Annoter** un passage (texte surligné + commentaire libre) | ✅ |
| **🔖 Marque-page** à la position de lecture courante | ✅ |
| Panneau Annotations unifié (3 types distincts) | ✅ |
| Navigation vers le passage depuis le panneau (↗) | ✅ |
| Édition inline des notes | ✅ |
| **↓ Export** de toutes les annotations en fichier `.txt` | ✅ |
| Persistance SQLite (survit aux redémarrages) | ✅ |

</details>

<details>
<summary><strong>📚 Bibliothèque & formats</strong></summary>

| Fonctionnalité | État |
|---|:---:|
| Format **EPUB** | ✅ |
| Format **PDF** (PyMuPDF) | ✅ |
| Format **TXT** | ✅ |
| Format **FB2** (FictionBook) | ✅ |
| Détection automatique du format | ✅ |
| Dossiers thématiques | ✅ |
| Upload depuis l'interface | ✅ |
| Dictionnaire de prononciation personnalisable | ✅ |

</details>

---

## ⚡ Installation

### 📦 Via le paquet .deb (recommandé)

```bash
# Télécharger la dernière release
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_2.1.0_amd64.deb

# Installer
sudo dpkg -i librelector_2.1.0_amd64.deb
sudo apt install -f          # résout les dépendances manquantes si besoin

# Lancer
librelector
```

> L'interface s'ouvre dans votre navigateur à `http://localhost:7531`.
> LibreLector apparaît aussi dans le menu des applications.

---

### 🔧 Depuis les sources (développement)

```bash
git clone https://github.com/nouhailler/LibreLector.git
cd LibreLector

# Créer l'environnement Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1 — backend (port 7531)
python -m librelector.api.server

# Terminal 2 — frontend avec hot-reload (port 5173)
cd ui && npm install && npm run dev
```

Vite proxie automatiquement `/api` et `/ws` vers le backend.

---

## 🧠 Configurer la voix Piper (recommandé)

> Sans Piper, Speech Dispatcher (voix robot système) prend le relais automatiquement.

### 1. Installer Piper

```bash
pip install piper-tts
```

### 2. Télécharger un modèle de voix

```bash
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices

# Voix française féminine naturelle (siwis-medium)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

> D'autres voix sur [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)

### 3. Configurer dans l'interface

**⚙ Paramètres** → sélectionner `piper` → renseigner le chemin vers le `.onnx` → **Enregistrer**

---

## 🖥️ Interface

```
┌─────────────────────┬────────────────────────────────────────────────────────┐
│  📚 Bibliothèque  + │  Le Petit Prince — Antoine de Saint-Exupéry     🔖 📝 │
│                     │                                                        │
│  ▼ Romans           │  ▸ Chapitre 1  Il était une fois un petit prince       │
│    📕 Livre A       │  ▸ Chapitre 2  qui habitait une planète à peine        │
│    📗 Livre B  ···  │  ▸ Chapitre 3  plus grande que lui, et qui avait       │
│  ▼ Essais           │             ██ besoin d'un ami. ██                     │
│    📘 Livre C  ···  │                                                        │
│                     │  📝 Annotations (3)                    ↓ Exporter     │
│  ─────────────────  │  ─────────────────────────────────────────────────     │
│                     │  🖊  « besoin d'un ami »    Ch.3 · Phrase 7           │
│                     │  📝  « petit prince »       — Personnage central       │
│                     │  🔖  Marque-page            Ch.2 · Phrase 1           │
│                     │                                                        │
│                     │  ⏮   ▶   ⏹   ⏭    1.0×   🔊──────●                  │
└─────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│  🌐 Frontend React 18 + TypeScript            │
│     Vite · Tailwind CSS · Zustand             │
│     Servi statiquement par FastAPI             │
└─────────────────────┬────────────────────────┘
                      │  HTTP REST + WebSocket
                      │  localhost:7531
┌─────────────────────▼────────────────────────┐
│  ⚡ Backend FastAPI (Python 3.11+)            │
│                                               │
│  /api/library   — bibliothèque & upload       │
│  /api/reader    — ouverture, chapitres        │
│  /api/player    — contrôles TTS               │
│  /api/notes     — annotations & surlignages   │
│  /api/bookmarks — marque-pages                │
│  /api/export    — MP3 (SSE)                   │
│  /ws            — surlignage temps réel       │
│                                               │
│  document/  → parseurs EPUB·PDF·TXT·FB2       │
│  tts/       → Piper (neural) + fallback       │
│  core/      → Player + export MP3             │
│  data/      → SQLite WAL                      │
└───────────────────────────────────────────────┘
```

> Tous les parseurs retournent une structure `EpubBook` commune — le moteur TTS et l'export fonctionnent indépendamment du format source.

---

## 🗄️ Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # 📊 Bibliothèque SQLite
├── settings.json        # ⚙️  Préférences TTS
├── pronunciation.json   # 🗣️  Prononciations personnalisées
└── voices/              # 🧠 Modèles Piper (.onnx)
```

### Dictionnaire de prononciation

```json
// ~/.local/share/LibreLector/pronunciation.json
{
  "LLM":        "L L M",
  "Kubernetes": "koubernetesse",
  "GPU":        "gépéu"
}
```

---

## 📦 Dépendances

| Dépendance | Version | Rôle |
|---|---|---|
| Python | ≥ 3.11 | Runtime backend |
| FastAPI + uvicorn | ≥ 0.110 | Serveur API |
| ebooklib + bs4 + lxml | ≥ latest | Parsing EPUB |
| PyMuPDF | ≥ 1.23 | Parsing PDF |
| NLTK | ≥ 3.8 | Tokenisation phrases |
| pydub | ≥ 0.25 | Export audio |
| ffmpeg | système | Encodage MP3 |
| piper-tts | ≥ latest | Voix neuronale (optionnel) |
| Node.js + npm | ≥ 18 | Build frontend (dev) |

---

## 🗺️ Feuille de route

- [x] **v1.0** — Interface React + API FastAPI, bibliothèque, TTS Piper
- [x] **v2.0** — Panneau paramètres, correction chargement EPUB
- [x] **v2.1** — Annotations complètes : surlignage, marque-pages, export `.txt`
- [ ] **v2.2** — Mode podcast, navigation intelligente, raccourcis clavier
- [ ] **v3.0** — Packaging Flatpak / AppImage

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. **🐛 Signaler un bug** → [ouvrir une issue](https://github.com/nouhailler/LibreLector/issues)
2. **✨ Proposer une fonctionnalité** → [discussion](https://github.com/nouhailler/LibreLector/discussions)
3. **🔧 Soumettre un patch** → forker → branche → [pull request](https://github.com/nouhailler/LibreLector/pulls)
4. **📄 Ajouter un format** → implémenter `DocumentParser` dans `src/librelector/document/`

> Commits en français, convention : `feat:`, `fix:`, `perf:`, `docs:`, `chore:`

---

## 🙏 Remerciements

LibreLector s'appuie sur des projets open-source remarquables :

| Projet | Rôle |
|---|---|
| [Piper TTS](https://github.com/rhasspy/piper) | Voix neuronale offline |
| [FastAPI](https://fastapi.tiangolo.com) | Framework API Python |
| [React](https://react.dev) | Interface utilisateur |
| [ebooklib](https://github.com/aerkalov/ebooklib) | Parsing EPUB |
| [PyMuPDF](https://pymupdf.readthedocs.io) | Parsing PDF |
| [NLTK](https://www.nltk.org) | Tokenisation |
| [pydub](https://github.com/jiaaro/pydub) + [FFmpeg](https://ffmpeg.org) | Export MP3 |
| [Speech Dispatcher](https://freebsoft.org/speechd) | TTS système (fallback) |

---

<div align="center">

**Licence GNU GPL v3.0** — [LICENSE](LICENSE)

Maintenu par [nouhailler](https://github.com/nouhailler)

</div>
