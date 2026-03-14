# LibreLector

**Lecteur EPUB open-source avec TTS neuronal offline pour Linux**

LibreLector est un lecteur de livres numériques conçu *prioritairement pour l'écoute*.
Contrairement aux lecteurs visuels classiques (Foliate, Calibre…), l'audio est au cœur de l'expérience : voix naturelles hors-ligne via **Piper**, surlignage synchronisé phrase par phrase et mot par mot, et lecture continue multi-chapitres.

---

## Fonctionnalités

| Fonctionnalité | État |
|---|---|
| Ouverture / parsing EPUB | ✅ |
| Affichage texte (GTK4 TextView) | ✅ |
| TTS Piper (offline neuronal) | ✅ |
| TTS Speech Dispatcher (fallback) | ✅ |
| Play / Pause / Stop | ✅ |
| Navigation chapitres | ✅ |
| Vitesse et volume | ✅ |
| Mémorisation de la position | ✅ |
| Surlignage phrase | ✅ |
| Surlignage mot (approximé) | ✅ |
| Bibliothèque SQLite | ✅ |
| Dictionnaire de prononciation | ✅ |
| Lecture continue multi-chapitres | ✅ |
| Interface GTK4 / Libadwaita | ✅ |
| Export audio (MP3/OGG) | 🔜 |
| Mode podcast / écran éteint | 🔜 |
| Packaging Flatpak / AppImage | 🔜 |

---

## Architecture

```
src/librelector/
├── epub/
│   ├── models.py          # EpubBook, EpubChapter, TextSegment
│   └── parser.py          # ZIP → OPF → HTML → plain text → segments
├── tts/
│   ├── base.py            # TTSEngine (classe abstraite)
│   ├── piper.py           # Piper (voix neuronales offline)
│   ├── speech_dispatcher.py  # Speech Dispatcher (fallback)
│   └── factory.py         # Sélection automatique du moteur
├── core/
│   ├── player.py          # Orchestrateur principal
│   └── pronunciation.py   # Dictionnaire de prononciation JSON
├── data/
│   ├── library.py         # Gestionnaire SQLite
│   └── models.py          # BookRecord, ReadingProgress, Bookmark
├── ui/
│   ├── application.py     # Adw.Application
│   ├── window.py          # Fenêtre principale
│   ├── library_view.py    # Sidebar bibliothèque
│   ├── reader_view.py     # Zone de lecture + contrôles
│   └── settings_dialog.py # Paramètres
└── main.py                # Point d'entrée CLI
```

---

## Installation

### 1. Dépendances système

```bash
# GTK4 + Libadwaita
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# WebKitGTK (optionnel, pour rendu HTML riche)
sudo apt install gir1.2-webkit-6.0

# Speech Dispatcher (TTS fallback)
sudo apt install speech-dispatcher

# aplay (lecture audio raw pour Piper)
sudo apt install alsa-utils
```

### 2. Piper (voix neuronales offline – recommandé)

```bash
# Télécharger le binaire Piper
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo mv piper/piper /usr/local/bin/

# Télécharger un modèle de voix (exemple : français)
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

### 3. LibreLector

```bash
git clone https://github.com/votre-compte/LibreLector.git
cd LibreLector
pip install -e .
```

---

## Utilisation

```bash
# Lancer l'interface graphique
librelector

# Ouvrir directement un fichier EPUB
librelector mon_livre.epub
```

### Configuration Piper (première utilisation)

Dans l'interface : **≡ → Paramètres**
- Moteur préféré : `piper`
- Chemin modèle : `~/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx`

Ou en éditant directement :

```json
// ~/.local/share/LibreLector/settings.json
{
  "tts_engine": "piper",
  "piper_model": "/home/utilisateur/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr"
}
```

### Dictionnaire de prononciation

```json
// ~/.local/share/LibreLector/pronunciation.json
{
  "LLM": "L L M",
  "Kubernetes": "koubernetesse",
  "GPU": "gépéu"
}
```

---

## Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Fichiers de données

```
~/.local/share/LibreLector/
├── metadata.db          # Bibliothèque SQLite
├── settings.json        # Préférences
├── pronunciation.json   # Dictionnaire de prononciation
└── voices/              # Modèles Piper
```

---

## Feuille de route

- **v0.1** – MVP : parsing EPUB, TTS, surlignage, bibliothèque (actuel)
- **v0.2** – Export audio (WAV → MP3/OGG via FFmpeg)
- **v0.3** – Mode podcast, navigation intelligente (dialogues, titres)
- **v0.4** – Mode apprentissage langue (répétition de phrases)
- **v0.5** – Packaging Flatpak / AppImage
- **v1.0** – Release stable

---

## Contribuer

Les contributions sont les bienvenues !
Ouvrez une *issue* ou soumettez une *pull request*.

---

## Licence

GNU General Public License v3.0 – voir [LICENSE](LICENSE).
