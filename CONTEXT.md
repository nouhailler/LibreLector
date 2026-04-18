# LibreLector — Contexte du projet

## Description

LibreLector est un lecteur EPUB open-source orienté **audio-first** pour Linux.
Il combine la lecture neuronale hors-ligne (Piper TTS) avec un surlignage synchronisé
phrase par phrase, une bibliothèque persistante et l'export MP3.

Licence : GPL v3 · Langue principale : Python 3.11+ · UI actuelle : GTK4 / Libadwaita

---

## Stack technique actuelle

| Couche | Technologie |
|--------|-------------|
| UI | GTK4 + Libadwaita (PyGObject) |
| Logique métier | Python 3.11 |
| TTS principal | Piper (subprocess, modèles ONNX) |
| TTS fallback | Speech Dispatcher |
| EPUB | ebooklib + BeautifulSoup4 + lxml |
| NLP | NLTK (tokenisation des phrases) |
| Base de données | SQLite (WAL) via sqlite3 |
| Export audio | pydub + FFmpeg (subprocess) |
| Packaging | Debian .deb + setuptools |

---

## Architecture des sources

```
src/librelector/
├── epub/
│   ├── models.py             # EpubBook, EpubChapter, TextSegment
│   └── parser.py             # ZIP → OPF → HTML → texte brut → segments
├── tts/
│   ├── base.py               # TTSEngine abstraite + callbacks
│   ├── piper.py              # Moteur Piper (subprocess, neural)
│   ├── speech_dispatcher.py  # Fallback système
│   └── factory.py            # Sélection automatique du moteur
├── core/
│   ├── player.py             # Orchestrateur principal (play/pause/stop/navigation)
│   ├── exporter.py           # Export MP3 via FFmpeg
│   └── pronunciation.py      # Dictionnaire JSON de prononciation
├── data/
│   ├── library.py            # CRUD SQLite (livres, dossiers, progression, marque-pages)
│   └── models.py             # BookRecord, Folder, ReadingProgress, Bookmark
└── ui/                       # ← À remplacer par React
    ├── application.py
    ├── window.py
    ├── library_view.py
    ├── reader_view.py
    ├── export_dialog.py
    └── settings_dialog.py
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

## Fonctionnalités clés

- Ouverture EPUB et parsing en segments (phrases)
- Lecture TTS avec surlignage synchronisé phrase par phrase
- Démarrage de lecture au clic sur une phrase
- Navigation par chapitres (TOC)
- Bibliothèque avec dossiers thématiques (SQLite)
- Mémorisation automatique de la position de lecture
- Contrôles : play/pause/stop, vitesse, volume, chapitre suivant/précédent
- Export MP3 par chapitre via FFmpeg
- Dictionnaire de prononciation personnalisable

---

## Migration React en cours

### Objectif
Remplacer l'interface GTK4 par une interface **React** tout en conservant
la totalité du backend Python (epub/, tts/, core/, data/).

### Architecture cible

```
┌─────────────────────────────────────────────────┐
│  Frontend React (Vite + TypeScript)              │
│  Tauri shell → accès système natif               │
└────────────────────┬────────────────────────────┘
                     │ HTTP/WebSocket (localhost)
┌────────────────────▼────────────────────────────┐
│  Backend FastAPI (Python)                        │
│  Réutilise epub/, tts/, core/, data/ intacts     │
│  Processus sidecar géré par Tauri                │
└─────────────────────────────────────────────────┘
```

### Pile cible

| Rôle | Choix |
|------|-------|
| Shell desktop | **Tauri v2** (Rust, ~5 Mo vs 200 Mo Electron) |
| Frontend | **React 18 + TypeScript** |
| Build frontend | **Vite** |
| Style | **Tailwind CSS v4** |
| État global | **Zustand** |
| API backend | **FastAPI + uvicorn** (Python, sidecar Tauri) |
| Communication temps réel | **WebSocket** (surlignage synchronisé, progression TTS) |
| Upload fichiers | API REST multipart |

### Phases — TOUTES COMPLÉTÉES ✅

1. **Backend FastAPI** (`src/librelector/api/`) — wrapper REST/WS autour de core/, epub/, data/, tts/
2. **Shell Tauri v2** (`src-tauri/`) — démarre Python, attend port 7531, affiche la fenêtre
3. **Frontend React** (`ui/`) — LibraryPanel, ReaderPanel, PlayerControls, SettingsModal, ExportModal
4. **Intégration** — surlignage WebSocket, upload EPUB, export MP3 SSE, retry initial
5. **Packaging** (`build.sh`, `src-tauri/tauri.conf.json`) — bundle Tauri → .deb uniquement

### Décisions d'architecture importantes

- **Le backend Python reste intact** — aucune réécriture de epub/, tts/, core/, data/
- **WebSocket obligatoire** pour le surlignage synchronisé (événements phrase-courante)
- **Tauri sidecar** démarre/arrête le serveur FastAPI automatiquement
- **Fichiers EPUB stockés localement** — l'API reçoit le chemin ou un upload multipart
- **SQLite partagé** entre backend FastAPI et éventuel accès Tauri direct

---

## Conventions de code

- Python : black (formatter), ruff (linter), pytest (tests)
- Commits en français, conventionnel : `feat:`, `fix:`, `perf:`, `docs:`, `chore:`
- Pas de commentaires triviaux — uniquement les invariants non-évidents

---

## Session de debug en cours

**Branche :** `claude/fix-librelector-localhost-XfxCQ` → PR #3 (draft)

### Corrections apportées

| Commit | Problème | Fichiers modifiés |
|--------|----------|-------------------|
| `bbc49b5` | `.deb` ne contenait pas le frontend — `{"detail":"Not Found"}` à l'ouverture | `packaging/build_deb.sh`, `src/librelector/api/app.py` |
| `fa1400f` | Vite 5/6 incompatible avec Node.js v24 (`ERR_MODULE_NOT_FOUND`) | `ui/package.json` (Vite 8 + plugin-react 6) |
| `7f869a6` | Cliquer "Ouvrir EPUB" ne faisait rien (uploadBook n'appelait pas openBook) | `ui/src/store/useStore.ts` |
| `7f869a6` | Paramètres bloqués sur "Chargement…" sans message d'erreur | `ui/src/components/Settings/SettingsModal.tsx` |
| `7f869a6` | WebSocket se reconnectait en boucle (dépendances instables) | `ui/src/hooks/useWebSocket.ts` |

### Détail des corrections

**`src/librelector/api/app.py`** — `_locate_ui_dist()` remonte les dossiers parents
jusqu'à trouver `ui/dist`, compatible dev (`src/librelector/api/…` → racine) et
installé (`/usr/local/lib/librelector/librelector/api/…` → `/usr/local/lib/librelector/ui/dist`).

**`packaging/build_deb.sh`** — ajout de `npm install && npm run build` et copie de
`ui/dist` dans `$LIB_DIR/ui/dist` avant la construction du `.deb`.

**`ui/src/store/useStore.ts`** — `uploadBook()` : après `loadLibrary()`, appelle
maintenant `await get().openBook(book.id)`.

**`ui/src/components/Settings/SettingsModal.tsx`** — `Promise.all` avec `.catch()`
et état `loadError` ; affiche "Erreur de chargement" au lieu de rester suspendu.

**`ui/src/hooks/useWebSocket.ts`** — handlers déplacés dans un `ref` (`handlersRef`),
dépendances de l'effet passées à `[]` pour éviter les reconnexions intempestives.

### Problème restant à investiguer

**Paramètres TTS parfois bloqués sur "Chargement…"** — les appels API retournent 200 OK
(`GET /api/settings` et `GET /api/settings/voices`) mais `settings` reste `null`.
Piste : ouvrir les DevTools (F12) → onglet Console pour voir si une erreur JS
apparaît, et onglet Réseau pour vérifier que les réponses JSON sont bien parsées.

### Commandes de mise à jour rapide (machine de test sans reconstruire le .deb)

```bash
cd /tmp/librelector-src
git fetch origin claude/fix-librelector-localhost-XfxCQ
git reset --hard FETCH_HEAD
cd ui
rm -rf node_modules package-lock.json
npm install          # installe Vite 8 depuis le package.json corrigé
npm run build
sudo cp -r dist/* /usr/local/lib/librelector/ui/dist/
sudo cp /tmp/librelector-src/src/librelector/api/app.py \
        /usr/local/lib/librelector/librelector/api/app.py
```
