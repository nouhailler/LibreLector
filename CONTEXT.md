# LibreLector — Contexte du projet

## Description

LibreLector est un lecteur EPUB open-source orienté **audio-first** pour Linux.
Il combine la lecture neuronale hors-ligne (Piper TTS) avec un surlignage synchronisé
phrase par phrase, une bibliothèque persistante et l'export MP3.

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
| NLP | NLTK (tokenisation des phrases) |
| Base de données | SQLite (WAL) via sqlite3 |
| Export audio | pydub + FFmpeg (subprocess) |
| Packaging | Debian .deb (build_deb.sh) |

---

## Architecture

Le backend FastAPI démarre un serveur local sur le port **7531** et sert le frontend
React compilé (`ui/dist/`). Le frontend s'ouvre dans le navigateur par défaut.

```
┌──────────────────────────────────────────┐
│  Frontend React (Vite + TypeScript)       │
│  Servi statiquement par FastAPI           │
└───────────────────┬──────────────────────┘
                    │ HTTP REST + WebSocket (localhost:7531)
┌───────────────────▼──────────────────────┐
│  Backend FastAPI (Python)                 │
│  api/routers/ : library, player,          │
│                 reader, settings, export  │
│  api/ws_manager.py : surlignage WS        │
│  Réutilise epub/, tts/, core/, data/      │
└──────────────────────────────────────────┘
```

---

## Structure des sources

```
src/librelector/
├── api/
│   ├── app.py               # Application FastAPI, sert ui/dist en catch-all SPA
│   ├── server.py            # Démarrage uvicorn
│   ├── session.py           # État global partagé (player, livre courant)
│   ├── ws_manager.py        # Broadcast WebSocket (surlignage phrase)
│   └── routers/
│       ├── library.py       # CRUD bibliothèque + upload EPUB
│       ├── player.py        # Contrôles lecture (play/pause/stop/navigation)
│       ├── reader.py        # Segments EPUB, position
│       ├── settings.py      # Préférences TTS, liste des voix
│       └── export.py        # Export MP3 SSE
├── epub/
│   ├── models.py            # EpubBook, EpubChapter, TextSegment
│   └── parser.py            # ZIP → OPF → HTML → texte brut → segments
├── tts/
│   ├── base.py              # TTSEngine abstraite + callbacks
│   ├── piper.py             # Moteur Piper (subprocess, neural)
│   ├── speech_dispatcher.py # Fallback système
│   └── factory.py           # Sélection automatique du moteur
├── core/
│   ├── player.py            # Orchestrateur principal (play/pause/stop/navigation)
│   ├── exporter.py          # Export MP3 via FFmpeg
│   └── pronunciation.py     # Dictionnaire JSON de prononciation
├── data/
│   ├── library.py           # CRUD SQLite (livres, dossiers, progression, marque-pages)
│   └── models.py            # BookRecord, Folder, ReadingProgress, Bookmark
└── ui/                      # Ancien code GTK4 — conservé mais non utilisé

ui/                          # Frontend React
├── src/
│   ├── App.tsx
│   ├── api/                 # Clients HTTP (fetch vers localhost:7531)
│   ├── components/
│   │   ├── Library/         # Bibliothèque, dossiers, upload
│   │   ├── Reader/          # Affichage EPUB, surlignage
│   │   ├── Player/          # Contrôles lecture
│   │   ├── Settings/        # Modal paramètres TTS
│   │   ├── Export/          # Modal export MP3
│   │   └── Help/
│   ├── hooks/
│   │   └── useWebSocket.ts  # Connexion WS, handlers dans un ref (pas de reconnexion)
│   ├── store/
│   │   └── useStore.ts      # État global Zustand
│   └── types.ts
└── dist/                    # Frontend compilé — embarqué dans le .deb
```

---

## Données utilisateur

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite
├── settings.json        # Préférences TTS
├── pronunciation.json   # Prononciations personnalisées
└── voices/              # Modèles Piper (.onnx + .onnx.json)
```

---

## Fonctionnalités

- Ouverture EPUB et parsing en segments (phrases)
- Lecture TTS avec surlignage synchronisé phrase par phrase (WebSocket)
- Démarrage de lecture au clic sur une phrase
- Navigation par chapitres (TOC)
- Bibliothèque avec dossiers thématiques (SQLite)
- Mémorisation automatique de la position de lecture
- Contrôles : play/pause/stop, vitesse, volume, chapitre suivant/précédent
- Export MP3 par chapitre via FFmpeg (SSE)
- Dictionnaire de prononciation personnalisable
- Paramètres TTS depuis l'interface

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
