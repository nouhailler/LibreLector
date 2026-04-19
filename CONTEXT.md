# LibreLector — Contexte du projet

## Description

LibreLector est un lecteur de livres électroniques open-source orienté **audio-first** pour Linux.
Il combine la lecture neuronale hors-ligne (Piper TTS) avec un surlignage synchronisé
phrase par phrase, une bibliothèque persistante, l'export MP3, des annotations utilisateur
et la prise en charge de multiples formats de documents.

Licence : GPL v3 · Version courante : **2.1.0** · Langue principale : Python 3.11+

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18 + TypeScript (Vite 8) |
| Style | Tailwind CSS v3 |
| État global | Zustand (`ui/src/store/useStore.ts`) |
| Backend | FastAPI + uvicorn (Python 3.11+) |
| Communication temps réel | WebSocket (surlignage synchronisé) |
| TTS principal | Piper (subprocess, modèles ONNX) |
| TTS fallback | Speech Dispatcher |
| EPUB | ebooklib + BeautifulSoup4 + lxml |
| PDF | PyMuPDF (fitz) |
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
│                 export, notes, bookmarks  │
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
│       ├── notes.py         # CRUD annotations (notes + surlignages, champ type)
│       ├── bookmarks.py     # CRUD marque-pages (/api/bookmarks)
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
│   ├── types.ts             # Interfaces TypeScript (Book, Note, Bookmark, Sentence…)
│   ├── components/
│   │   ├── Library/         # Bibliothèque, dossiers, upload
│   │   ├── Reader/
│   │   │   ├── ReaderPanel.tsx    # Conteneur lecteur + boutons Notes / Marque-page / MP3
│   │   │   ├── ChapterText.tsx    # Affichage phrases, sélection → menu flottant (Surligner/Note)
│   │   │   └── TableOfContents.tsx
│   │   ├── Notes/
│   │   │   ├── NotesPanel.tsx     # Panneau unifié : notes (📝), surlignages (🖊), marque-pages (🔖)
│   │   │   └── NoteDialog.tsx     # Dialog création de note annotée
│   │   ├── Player/          # Contrôles lecture
│   │   ├── Settings/        # Modal paramètres TTS
│   │   ├── Export/          # Modal export MP3
│   │   └── Help/
│   ├── hooks/
│   │   └── useWebSocket.ts  # Connexion WS, handlers dans un ref
│   └── store/
│       └── useStore.ts      # État global Zustand
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
| `bookmarks` | Marque-pages (chapter_order, sentence_index, label) |
| `notes` | Annotations (highlighted_text, content, **type**: 'note'|'highlight', position) |

> **Migration automatique** : les colonnes `folder_id` (books) et `type` (notes) sont ajoutées
> au démarrage si elles n'existent pas — aucune action manuelle requise.

---

## Fonctionnalités implémentées

### Lecture
- Ouverture de livres **EPUB, PDF, TXT, FB2** (MOBI/AZW3 non supporté)
- Détection automatique du format (extension + magic bytes)
- Lecture TTS avec surlignage synchronisé phrase par phrase (WebSocket)
- Démarrage de lecture au clic sur une phrase
- Navigation par chapitres (TOC)
- Mémorisation automatique de la position de lecture
- Contrôles : play/pause/stop, vitesse (0.25×→4×), volume, chapitre suivant/précédent
- Export MP3 par chapitre via FFmpeg (SSE)

### Bibliothèque
- Dossiers thématiques (SQLite, glisser-déposer)
- Upload via l'interface (EPUB · TXT · PDF · FB2)

### Annotations (v2.1.0)
- **Surlignage** : sélectionner du texte → `🖊 Surligner` → sauvegardé sans commentaire
- **Note annotée** : sélectionner du texte → `📝 Note` → dialog avec saisie libre
- **Marque-page** : bouton `🔖 Marque-page` en en-tête → posé à la position courante
- Panneau Annotations unifié avec 3 types visuellement distincts :
  - 📝 Note : bordure jaune, texte surligné + commentaire éditable
  - 🖊 Surlignage : bordure orange, texte uniquement
  - 🔖 Marque-page : bordure bleue, libellé + navigation
- **Export annotations** : bouton `↓ Exporter` → fichier `.txt` (titre, chapitres, phrases)
- Navigation vers le passage depuis le panneau (↗)
- Persistance SQLite, cascade suppression avec le livre
- API REST : `/api/notes`, `/api/bookmarks`

### Autres
- Dictionnaire de prononciation personnalisable (JSON)
- Paramètres TTS depuis l'interface

---

## API REST

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/library` | Liste livres + dossiers |
| POST | `/api/library/books/upload` | Upload EPUB/PDF/TXT/FB2 |
| DELETE | `/api/library/books/{id}` | Supprimer un livre |
| POST/GET/DELETE | `/api/library/folders` | CRUD dossiers |
| POST | `/api/reader/open/{id}` | Ouvrir un livre |
| GET | `/api/reader/chapter/{order}` | Contenu d'un chapitre (phrases) |
| POST | `/api/player/play` | Lecture |
| POST | `/api/player/pause` | Pause |
| POST | `/api/player/sentence/{idx}` | Aller à une phrase |
| GET/PUT | `/api/settings` | Paramètres TTS |
| GET/POST/PUT/DELETE | `/api/notes/{book_id}` | CRUD notes/surlignages |
| GET/POST/DELETE | `/api/bookmarks/{book_id}` | CRUD marque-pages |
| POST | `/api/export/chapter/{order}` | Export MP3 (SSE) |
| WS | `/ws` | Surlignage temps réel |

---

## Démarrage en développement

```bash
# Prérequis : créer le virtualenv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install python-multipart PyMuPDF

# Terminal 1 — backend
python -m librelector.api.server

# Terminal 2 — frontend (proxy Vite → port 7531)
cd ui && npm install && npm run dev
# → http://localhost:5173
```

---

## Formats de documents supportés

| Format | Parser | Chapitres | Dépendance |
|--------|--------|-----------|------------|
| EPUB | `epub_doc.py` | Spine OPF | ebooklib |
| PDF | `pdf_doc.py` | TOC ou groupes de 10 pages | PyMuPDF |
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
- Installe les dépendances Python via pip3 (dont python-multipart, PyMuPDF)
- Affiche une bannière d'installation avec la version dynamique

Entrée menu : `packaging/debian/usr/share/applications/librelector.desktop`
Icône : `packaging/debian/usr/share/icons/hicolor/256x256/apps/librelector.png`

---

## Bugs connus / limitations

- Les fichiers MOBI/AZW3 (Kindle) ne sont pas supportés
- Speech Dispatcher produit une voix robot — Piper est fortement recommandé
- La migration DB est automatique mais nécessite un redémarrage si la DB était ouverte
- L'export MP3 nécessite FFmpeg installé sur le système

---

## Conventions

- Python : black (formatter), ruff (linter), pytest (tests)
- Commits en français, conventionnel : `feat:`, `fix:`, `perf:`, `docs:`, `chore:`
- Pas de commentaires triviaux — uniquement les invariants non-évidents
- Le catch-all SPA dans `app.py` ne doit **pas** intercepter les routes `/api/*`
- Tous les parsers de documents retournent un `EpubBook` (structure commune)

---

## Derniers travaux (session 2026-04-19)

**Fonctionnalités ajoutées — v2.1.0** :
- Surlignage persistant de phrases (type `highlight` dans la table `notes`)
- Marque-pages avec API `/api/bookmarks` complète
- Panneau Annotations unifié (3 types visuellement distincts)
- Export des annotations en fichier `.txt`
- Migration automatique de la colonne `type` dans `notes`
- Icône SVG de l'application + entrée `.desktop`
- Packaging Debian mis à jour (v2.1.0, nouvelles dépendances)
