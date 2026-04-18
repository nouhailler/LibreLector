# LibreLector

> Lecteur de livres numériques open-source, audio-first, pour Linux

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/UI-React%2018-61dafb.svg)](https://react.dev)
[![Piper TTS](https://img.shields.io/badge/TTS-Piper-purple.svg)](https://github.com/rhasspy/piper)
[![Last commit](https://img.shields.io/github/last-commit/nouhailler/LibreLector)](https://github.com/nouhailler/LibreLector/commits/main)
[![GitHub release](https://img.shields.io/github/v/release/nouhailler/LibreLector)](https://github.com/nouhailler/LibreLector/releases/latest)

LibreLector est un lecteur de livres numériques conçu **prioritairement pour l'écoute**.
Contrairement aux lecteurs visuels classiques (Foliate, Calibre…), l'audio est au cœur de l'expérience :
voix naturelles hors-ligne via **Piper TTS**, surlignage synchronisé phrase par phrase,
prise en charge de multiples formats et export MP3.

L'interface React s'ouvre dans votre navigateur ; un backend FastAPI tourne en local — aucune donnée ne quitte votre machine.

---

## Fonctionnalités

| Fonctionnalité | État |
|---|---|
| Lecture de fichiers **EPUB, PDF, TXT, FB2** | ✅ |
| Détection automatique du format (extension + magic bytes) | ✅ |
| Voix neuronale offline via **Piper TTS** | ✅ |
| Voix système via Speech Dispatcher (fallback automatique) | ✅ |
| Surlignage synchronisé phrase par phrase (WebSocket) | ✅ |
| Démarrage de la lecture au clic sur n'importe quelle phrase | ✅ |
| Lecture / Pause / Arrêt | ✅ |
| Navigation par chapitres (table des matières) | ✅ |
| Mémorisation automatique de la position de lecture | ✅ |
| Bibliothèque avec dossiers thématiques | ✅ |
| Annotations (notes sur passage surligné + navigation) | ✅ |
| Dictionnaire de prononciation personnalisé | ✅ |
| Réglage de la vitesse (0.25× à 4×) et du volume | ✅ |
| Lecture continue multi-chapitres | ✅ |
| Export MP3 par chapitre via FFmpeg | ✅ |

---

## Prérequis système

| Dépendance | Version | Rôle |
|---|---|---|
| Python | 3.11+ | Backend FastAPI |
| pip3 | — | Installation des dépendances Python |
| alsa-utils | — | Sortie audio |
| xdg-utils | — | Ouverture du navigateur |
| ffmpeg | — | **Optionnel** — export MP3 |
| piper-tts + pathvalidate | — | **Optionnel** — voix neuronale naturelle |
| PyMuPDF | ≥ 1.23 | **Optionnel** — lecture de fichiers PDF |

> Le paquet `.deb` installe automatiquement `python3`, `python3-pip`, `alsa-utils`, `ffmpeg` et `xdg-utils` via `apt`.

---

## Installation

### Via le paquet .deb (recommandé)

```bash
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_2.0.1_amd64.deb
sudo dpkg -i librelector_2.0.1_amd64.deb
sudo apt install -f   # résout les éventuelles dépendances manquantes
librelector
```

L'interface s'ouvre dans votre navigateur à `http://localhost:7531`.

### Depuis les sources

```bash
git clone https://github.com/nouhailler/LibreLector.git
cd LibreLector
pip3 install -r requirements.txt

# Lancer le backend
PYTHONPATH=src python3 -m librelector.api.server

# Dans un second terminal — frontend (développement, avec hot-reload)
cd ui
npm install
npm run dev   # → http://localhost:5173
```

En développement, Vite (port 5173) proxie automatiquement `/api` et `/ws` vers le backend (port 7531).

---

## Configuration de la voix Piper

Piper produit une voix naturelle, entièrement hors-ligne. Il nécessite un modèle `.onnx` par langue.

### 1. Installer Piper

```bash
pip3 install piper-tts pathvalidate --break-system-packages
```

### 2. Télécharger un modèle de voix

```bash
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices

# Exemple : voix française féminine (siwis-medium)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

D'autres voix sont disponibles sur [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices) — choisir le dossier `fr/fr_FR/` pour le français.

### 3. Configurer dans l'interface

**☰ → Paramètres** → sélectionner `piper` et renseigner le chemin complet vers le fichier `.onnx`.

Ou directement dans `~/.local/share/LibreLector/settings.json` :

```json
{
  "tts_engine": "piper",
  "piper_model": "/home/VOTRE_USER/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr"
}
```

> Si Piper n'est pas configuré, Speech Dispatcher (voix robot système) prend le relais automatiquement.

---

## Utilisation

### Interface

```
┌──────────────────────┬──────────────────────────────────────────────────────┐
│  Bibliothèque    📁+ +│  Titre du livre — Auteur                        ☰   │
│                      │                                                      │
│  ▼ Histoire          │  Chapitre 1 ──── Le texte du chapitre s'affiche     │
│    📕 Livre A        │  Chapitre 2      ici. La phrase en cours de          │
│    📗 Livre B   ···  │  Chapitre 3 ◀── lecture est ████████████████        │
│  ▶ Roman             │  Chapitre 4      surlignée en jaune.                │
│  ▼ Sans dossier      │                                                      │
│    📘 Livre C   ···  │  📝 Notes                                            │
│                      │                                                      │
│                      │  ⏮   ▶   ⏹   ⏭    Vitesse 1.00  🔊───●            │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

### Fonctions principales

| Action | Comment |
|---|---|
| Ajouter un livre | Bouton **+** (sidebar) — EPUB, PDF, TXT ou FB2 |
| Ouvrir un livre | Clic sur le titre dans la sidebar |
| Démarrer la lecture à une phrase précise | Clic sur la phrase dans le texte |
| Naviguer entre chapitres | Table des matières à gauche, ou boutons ⏮ / ⏭ |
| Créer une annotation | Sélectionner du texte → bouton **📝 Ajouter une note** |
| Afficher les notes | Bouton **📝 Notes** (coin supérieur droit de la zone de lecture) |
| Exporter en MP3 | **☰ → Exporter en MP3…** (nécessite FFmpeg + Piper) |
| Personnaliser la prononciation | Éditer `~/.local/share/LibreLector/pronunciation.json` |

### Dictionnaire de prononciation

Les sigles et noms propres mal prononcés peuvent être corrigés dans :

```
~/.local/share/LibreLector/pronunciation.json
```

```json
{
  "LLM": "L L M",
  "Kubernetes": "koubernetesse",
  "GPU": "gépéu"
}
```

### Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite (livres, dossiers, progression, notes)
├── settings.json        # Préférences TTS
├── pronunciation.json   # Prononciations personnalisées
└── voices/              # Modèles Piper (.onnx + .onnx.json)
```

---

## Architecture

LibreLector est une application web locale. Le backend FastAPI (port **7531**) sert le frontend React compilé et expose une API REST + WebSocket.

```
┌──────────────────────────────────────────┐
│  Frontend React 18 + TypeScript          │
│  (Vite, Tailwind CSS, Zustand)           │
│  Servi statiquement par FastAPI           │
└───────────────────┬──────────────────────┘
                    │ HTTP REST + WebSocket
┌───────────────────▼──────────────────────┐
│  Backend FastAPI (Python 3.11)           │
│                                          │
│  api/routers/                            │
│    library  · notes  · player            │
│    reader   · settings · export          │
│                                          │
│  document/  → parseurs EPUB/PDF/TXT/FB2  │
│  tts/       → Piper (neural) + fallback  │
│  core/      → Player + exporter MP3      │
│  data/      → SQLite WAL                 │
└──────────────────────────────────────────┘
```

Tous les parseurs de documents retournent une structure `EpubBook` commune, ce qui permet au moteur TTS et à l'export d'être indépendants du format source.

---

## Feuille de route

- **v1.0** — Interface React + API FastAPI, bibliothèque, TTS Piper ✅
- **v2.0** — Correction chargement EPUB et panneau paramètres ✅
- **v2.1** — Parseurs multi-format (PDF/TXT/FB2) + annotations ✅
- **v2.2** — Mode podcast, navigation intelligente
- **v3.0** — Packaging Flatpak / AppImage

---

## Contribuer

Les contributions sont les bienvenues, qu'il s'agisse de corrections de bugs, d'ajout de fonctionnalités ou d'améliorations de la documentation.

1. **Signaler un bug** : ouvrir une [issue](https://github.com/nouhailler/LibreLector/issues) en décrivant le comportement observé et les étapes pour le reproduire
2. **Proposer une modification** : forker le dépôt, créer une branche, soumettre une [pull request](https://github.com/nouhailler/LibreLector/pulls)
3. **Ajouter un format de document** : implémenter un `DocumentParser` dans `src/librelector/document/` et l'enregistrer dans `factory.py`

Les commits suivent la convention : `feat:`, `fix:`, `perf:`, `docs:`, `chore:` (en français).

---

## Remerciements

LibreLector s'appuie sur des projets open-source remarquables :

- [Piper TTS](https://github.com/rhasspy/piper) — synthèse vocale neuronale offline (Rhasspy)
- [FastAPI](https://fastapi.tiangolo.com) — framework API Python
- [React](https://react.dev) — interface utilisateur
- [ebooklib](https://github.com/aerkalov/ebooklib) — parsing EPUB
- [PyMuPDF](https://pymupdf.readthedocs.io) — parsing PDF
- [NLTK](https://www.nltk.org) — tokenisation des phrases
- [pydub](https://github.com/jiaaro/pydub) + [FFmpeg](https://ffmpeg.org) — export audio MP3
- [Speech Dispatcher](https://freebsoft.org/speechd) — TTS système Linux (fallback)

---

## Licence

GNU General Public License v3.0 — voir [LICENSE](LICENSE).

Projet maintenu par [nouhailler](https://github.com/nouhailler).
