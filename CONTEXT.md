# LibreLector — Contexte du projet

## Description

LibreLector est un lecteur de livres électroniques open-source orienté **audio-first** pour Linux.
Il combine la lecture neuronale hors-ligne (Piper TTS) avec un surlignage synchronisé
phrase par phrase, une bibliothèque persistante, l'export MP3, des annotations utilisateur
et la prise en charge de multiples formats de documents.

Licence : GPL v3 · Version courante : **2.0.1** · Langue principale : Python 3.11+

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18 + TypeScript (Vite 8) |
| Style | Tailwind CSS v4 |
| État global | Zustand (`ui/src/store/useStore.ts`) |
| Backend | FastAPI + uvicorn (Python 3.11) |
| Communication temps réel | WebSocket (surlignage synchronisé) |
| TTS principal | Piper (subprocess, modèles ONNX) |
| TTS fallback | Speech Dispatcher |
| EPUB | ebooklib + BeautifulSoup4 + lxml |
| PDF | PyMuPDF (fitz) — `pip install PyMuPDF` |
| FB2 / TXT | stdlib Python (xml.etree, pathlib) |
| NLP | NLTK (tokenisation des phrases) |
| Base de données | SQLite (WAL) via sqlite3 |
| Export audio | pydub + FFmpeg (subprocess) |
| Packaging | Debian .deb (build_deb.sh) |

---

## Architecture

Le backend FastAPI démarre un serveur local sur le port **7531** et sert le frontend
React compilé (`ui/dist/`). Le frontend s'ouvre dans le navigateur par défaut.

En mode développement, Vite tourne sur le port **5173** et proxie `/api` et `/ws`
vers le port 7531 (voir `ui/vite.config.ts`).

```
┌──────────────────────────────────────────┐
│  Frontend React (Vite + TypeScript)       │
│  Servi statiquement par FastAPI           │
└───────────────────┬──────────────────────┘
                    │ HTTP REST + WebSocket (localhost:7531)
┌───────────────────▼──────────────────────┐
│  Backend FastAPI (Python)                 │
│  api/routers/ : library, player,          │
│                 reader, settings,         │
│                 export, notes             │
│  api/ws_manager.py : surlignage WS        │
│  Réutilise document/, epub/, tts/,        │
│             core/, data/                  │
└──────────────────────────────────────────┘
```

---

## Structure des sources

```
src/librelector/
├── api/
│   ├── app.py               # Application FastAPI, sert ui/dist en catch-all SPA
│   ├── server.py            # Démarrage uvicorn (port 7531)
│   ├── session.py           # État global partagé (player, livre courant)
│   ├── ws_manager.py        # Broadcast WebSocket (surlignage phrase)
│   └── routers/
│       ├── library.py       # CRUD bibliothèque + upload (EPUB/PDF/TXT/FB2)
│       ├── notes.py         # CRUD annotations utilisateur
│       ├── player.py        # Contrôles lecture (play/pause/stop/navigation)
│       ├── reader.py        # Segments, position
│       ├── settings.py      # Préférences TTS, liste des voix
│       └── export.py        # Export MP3 SSE
├── document/                # Abstraction multi-formats
│   ├── base.py              # Classe abstraite DocumentParser → EpubBook
│   ├── epub_doc.py          # Wrapper EpubParser existant
│   ├── pdf_doc.py           # PyMuPDF : chapitres depuis TOC ou par groupes de pages
│   ├── txt_doc.py           # Texte brut : split double-newline, fusion/découpage auto
│   ├── fb2_doc.py           # XML FictionBook 2 : sections → chapitres
│   └── factory.py           # load_document(path) : détection auto (ext + magic bytes)
├── epub/
│   ├── models.py            # EpubBook, EpubChapter, TextSegment (structure commune)
│   └── parser.py            # ZIP → OPF → HTML → texte brut → segments
├── tts/
│   ├── base.py              # TTSEngine abstraite + callbacks
│   ├── piper.py             # Moteur Piper (subprocess, neural)
│   ├── speech_dispatcher.py # Fallback système
│   └── factory.py           # Sélection automatique du moteur
├── core/
│   ├── player.py            # Orchestrateur (utilise load_document() pour tous formats)
│   ├── exporter.py          # Export MP3 via FFmpeg
│   └── pronunciation.py     # Dictionnaire JSON de prononciation
├── data/
│   ├── library.py           # CRUD SQLite (livres, dossiers, progression, marque-pages, notes)
│   └── models.py            # BookRecord, Folder, ReadingProgress, Bookmark, Note
└── ui/                      # Ancien code GTK4 — conservé mais non utilisé

ui/                          # Frontend React
├── src/
│   ├── App.tsx              # Layout principal, bouton upload (EPUB·TXT·PDF·FB2)
│   ├── api/client.ts        # Clients HTTP (fetch vers /api/*)
│   ├── types.ts             # Interfaces TypeScript (Book, Note, Sentence…)
│   ├── components/
│   │   ├── Library/         # Bibliothèque, dossiers, upload
│   │   ├── Reader/
│   │   │   ├── ReaderPanel.tsx    # Conteneur lecteur + bouton Notes
│   │   │   ├── ChapterText.tsx    # Affichage phrases, sélection → bouton note flottant
│   │   │   └── TableOfContents.tsx
│   │   ├── Notes/
│   │   │   ├── NotesPanel.tsx     # Panneau latéral : liste des notes, navigation, édition
│   │   │   └── NoteDialog.tsx     # Dialog création de note (texte surligné + saisie)
│   │   ├── Player/          # Contrôles lecture
│   │   ├── Settings/        # Modal paramètres TTS
│   │   ├── Export/          # Modal export MP3
│   │   └── Help/
│   ├── hooks/
│   │   └── useWebSocket.ts  # Connexion WS, handlers dans un ref (pas de reconnexion)
│   ├── store/
│   │   └── useStore.ts      # État global Zustand (notes, notesOpen inclus)
│   └── types.ts
└── dist/                    # Frontend compilé — embarqué dans le .deb
```

---

## Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite (livres, progression, marque-pages, notes)
├── settings.json        # Préférences TTS
├── pronunciation.json   # Prononciations personnalisées
└── voices/              # Modèles Piper (.onnx + .onnx.json)
```

### Schéma SQLite (tables)

| Table | Rôle |
|-------|------|
| `books` | Métadonnées livres (titre, auteur, langue, cover, chemin) |
| `folders` | Dossiers thématiques |
| `reading_progress` | Position de lecture par livre (chapitre, phrase, offset) |
| `bookmarks` | Marque-pages nommés |
| `notes` | Annotations utilisateur (passage surligné, contenu, position, horodatage) |

---

## Fonctionnalités

### Lecture
- Ouverture de livres **EPUB, PDF, TXT, FB2** (MOBI/AZW3 non supporté)
- Détection automatique du format (extension + magic bytes)
- Lecture TTS avec surlignage synchronisé phrase par phrase (WebSocket)
- Démarrage de lecture au clic sur une phrase
- Navigation par chapitres (TOC)
- Mémorisation automatique de la position de lecture
- Contrôles : play/pause/stop, vitesse, volume, chapitre suivant/précédent
- Export MP3 par chapitre via FFmpeg (SSE)

### Bibliothèque
- Dossiers thématiques (SQLite)
- Upload via l'interface (bouton "+ Ouvrir EPUB · TXT · PDF")

### Annotations
- Sélection de texte → bouton flottant "📝 Ajouter une note"
- Dialog avec passage surligné + champ de saisie libre (Ctrl+Entrée pour sauver)
- Panneau latéral Notes : liste, navigation vers le passage, édition inline, suppression
- Persistance en base SQLite (table `notes`), cascade suppression avec le livre
- API REST : `GET/POST /api/notes/{book_id}`, `PUT/DELETE /api/notes/{id}`

### Autres
- Dictionnaire de prononciation personnalisable
- Paramètres TTS depuis l'interface

---

## Démarrage en développement

```bash
# Terminal 1 — backend (depuis la racine du dépôt)
PYTHONPATH=src python3 -m librelector.api.server

# Terminal 2 — frontend (proxy Vite → port 7531)
cd ui && npm run dev
# → http://localhost:5173
```

---

## Formats de documents supportés

| Format | Parser | Chapitres | Dépendance |
|--------|--------|-----------|------------|
| EPUB | `epub_doc.py` | Spine OPF | ebooklib |
| PDF | `pdf_doc.py` | TOC ou groupes de 10 pages | PyMuPDF (`pip install PyMuPDF`) |
| TXT | `txt_doc.py` | Double-newline, fusion auto | stdlib |
| FB2 | `fb2_doc.py` | `<section>` XML | stdlib |
| MOBI/AZW3 | — | non supporté | — |

---

## Packaging Debian

`packaging/build_deb.sh` :
1. Lit la version depuis `packaging/debian/DEBIAN/control`
2. Compile le frontend React (`npm run build`)
3. Copie `ui/dist/` dans le `.deb`
4. Construit `librelector_<VERSION>_amd64.deb`

`packaging/debian/DEBIAN/postinst` :
- Installe les dépendances Python via pip3
- Lit la version via `dpkg-query` et l'affiche dynamiquement dans la bannière

---

## Conventions

- Python : black (formatter), ruff (linter), pytest (tests)
- Commits en français, conventionnel : `feat:`, `fix:`, `perf:`, `docs:`, `chore:`
- Pas de commentaires triviaux — uniquement les invariants non-évidents
- Le catch-all SPA dans `app.py` ne doit **pas** intercepter les routes `/api/*`
- Tous les parsers de documents retournent un `EpubBook` (structure commune) pour que
  le Player, le TTS et l'export fonctionnent sans modification
