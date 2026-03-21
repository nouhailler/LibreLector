# Guide utilisateur — LibreLector

LibreLector est un lecteur de livres numériques (EPUB) conçu pour l'écoute.
Il lit votre livre à voix haute pendant que le texte défile et que les phrases sont surlignées une à une.

---

## Table des matières

1. [Installation](#1-installation)
2. [Lancer l'application](#2-lancer-lapplication)
3. [L'interface en un coup d'œil](#3-linterface-en-un-coup-dœil)
4. [La bibliothèque](#4-la-bibliothèque)
5. [Les dossiers](#5-les-dossiers)
6. [Lire un livre](#6-lire-un-livre)
7. [Contrôles de lecture](#7-contrôles-de-lecture)
8. [Navigation dans le texte](#8-navigation-dans-le-texte)
9. [La voix — Piper vs Speech Dispatcher](#9-la-voix--piper-vs-speech-dispatcher)
10. [Paramètres](#10-paramètres)
11. [Export MP3](#11-export-mp3)
12. [Dictionnaire de prononciation](#12-dictionnaire-de-prononciation)
13. [Données sauvegardées](#13-données-sauvegardées)
14. [Dépannage](#14-dépannage)

---

## 1. Installation

### Via le paquet .deb (recommandé)

```bash
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_0.2.0_amd64.deb
sudo dpkg -i librelector_0.2.0_amd64.deb
sudo apt install -f
```

### Dépendances optionnelles

| Paquet | Rôle | Commande |
|---|---|---|
| `gir1.2-webkit-6.0` | Rendu HTML riche du texte | `sudo apt install gir1.2-webkit-6.0` |
| `ffmpeg` | Export MP3 | `sudo apt install ffmpeg` |
| `piper-tts` + `pathvalidate` | Voix naturelle | `pip3 install piper-tts pathvalidate --break-system-packages` |

---

## 2. Lancer l'application

```bash
librelector
```

Ou pour ouvrir directement un fichier EPUB :

```bash
librelector /chemin/vers/mon_livre.epub
```

Au premier lancement, la bibliothèque est vide. Un message vous invite à ajouter un livre.

---

## 3. L'interface en un coup d'œil

L'interface est divisée en deux panneaux côte à côte :

```
┌──────────────────────┬────────────────────────────────────────────┐
│  SIDEBAR             │  ZONE DE LECTURE                           │
│  (bibliothèque)      │                                            │
│                      │  Titre — Auteur              [menu ☰]      │
│  ▼ Histoire          │                                            │
│    📕 Livre A        │  Chapitre 1     Le texte du chapitre       │
│    📗 Livre B   ···  │  Chapitre 2     s'affiche ici. La phrase   │
│  ▶ Roman             │  Chapitre 3 ◀   en cours de lecture est    │
│  ▼ Sans dossier      │                 surlignée en jaune.        │
│    📘 Livre C   ···  │                                            │
│                      │  ⏮   ▶   ⏹   ⏭   Vitesse 1.00  🔊───●   │
└──────────────────────┴────────────────────────────────────────────┘
```

**Panneau gauche — Bibliothèque** : liste de vos livres, organisés en dossiers.

**Panneau droit — Lecture** :
- En haut : table des matières du livre (chapitres) à gauche, texte à droite
- En bas : barre de contrôle (lecture, vitesse, volume)

---

## 4. La bibliothèque

La bibliothèque est la liste de tous les livres que vous avez ajoutés à LibreLector.
Elle se trouve dans le panneau de gauche.

### Ajouter un livre

Cliquez sur le bouton **+** (en haut à droite de la sidebar).
Une fenêtre s'ouvre pour sélectionner un fichier `.epub` sur votre ordinateur.

Le livre est ajouté à la bibliothèque et sa couverture (si disponible) s'affiche.
**Le fichier EPUB n'est pas copié** : LibreLector mémorise son emplacement d'origine.

### Ouvrir un livre

Cliquez sur le titre d'un livre dans la sidebar. Le texte du premier chapitre (ou du chapitre
où vous vous étiez arrêté) s'affiche immédiatement dans le panneau de droite.

### Menu contextuel d'un livre (bouton `···`)

Chaque livre dispose d'un bouton `···` sur sa droite. Il donne accès à :

- **Déplacer vers [dossier]** — assigner le livre à un dossier existant
- **Retirer du dossier** — remettre le livre dans "Sans dossier" (visible seulement si le livre est dans un dossier)
- **Supprimer de la bibliothèque** — retire le livre de la liste (le fichier EPUB n'est pas supprimé)

---

## 5. Les dossiers

Les dossiers permettent d'organiser vos livres par thème (Histoire, Roman, Philosophie…).

### Créer un dossier

Cliquez sur le bouton **dossier+** (à gauche du bouton +) dans le header de la sidebar.
Saisissez le nom du dossier et cliquez **Créer**.

### Renommer ou supprimer un dossier

Chaque dossier affiche deux icônes à sa droite :
- **Crayon** — renommer le dossier
- **Corbeille** — supprimer le dossier (les livres qu'il contient passent dans "Sans dossier")

### Assigner un livre à un dossier

Utilisez le bouton `···` sur le livre → **Déplacer vers [nom du dossier]**.

### Section "Sans dossier"

Si vous avez créé au moins un dossier, les livres non classés apparaissent automatiquement
dans une section **"Sans dossier"** en bas de la sidebar.

Si vous n'avez aucun dossier, tous vos livres s'affichent en liste plate (comportement par défaut).

---

## 6. Lire un livre

1. Cliquez sur un livre dans la sidebar → le texte s'affiche
2. Cliquez sur **▶** (bouton Play) pour démarrer la lecture
3. Le texte est lu à voix haute, phrase par phrase
4. La phrase en cours est **surlignée en jaune**
5. La table des matières met en évidence le chapitre en cours
6. À la fin d'un chapitre, la lecture **continue automatiquement** au chapitre suivant

### Reprendre où vous vous étiez arrêté

LibreLector mémorise automatiquement votre position (chapitre + phrase) à chaque pause ou arrêt.
La prochaine fois que vous ouvrez le même livre, la lecture reprend au même endroit.

---

## 7. Contrôles de lecture

La barre de contrôle se trouve en bas du panneau de lecture.

| Bouton | Action |
|---|---|
| **⏮** | Chapitre précédent |
| **▶ / ⏸** | Lancer la lecture / Mettre en pause |
| **⏹** | Arrêter la lecture et revenir au début du chapitre |
| **⏭** | Chapitre suivant |

### Différence entre Pause et Arrêt

- **Pause (⏸)** : suspend la lecture à l'endroit exact où elle en est. Cliquer sur ▶ reprend à la même phrase.
- **Arrêt (⏹)** : stoppe la lecture et **revient au début du chapitre actuel**. La position est sauvegardée.

### Vitesse de lecture

Le champ **Vitesse** (de 0.25× à 4×) ajuste la rapidité de la voix.
- `1.00` = vitesse normale
- `1.50` = 50 % plus rapide
- `0.75` = ralenti (utile pour apprendre)

La vitesse prend effet à la phrase suivante.

### Volume

Le curseur **volume** (icône haut-parleur) ajuste le niveau sonore de la synthèse vocale,
indépendamment du volume système.

---

## 8. Navigation dans le texte

### Table des matières (chapitres)

La colonne de gauche dans la zone de lecture liste tous les chapitres du livre.
Cliquez sur un chapitre pour y accéder directement. La lecture redémarre depuis le début
de ce chapitre.

### Démarrer la lecture à une phrase précise

**Double-cliquez** sur n'importe quelle phrase dans le texte.
La lecture démarre exactement à cette phrase.

---

## 9. La voix — Piper vs Speech Dispatcher

LibreLector supporte deux moteurs de synthèse vocale.

### Piper (recommandé) — voix neuronale naturelle

Piper est un moteur de TTS neuronal qui produit une voix naturelle, proche d'une voix humaine.
Il fonctionne entièrement **hors-ligne**, sans connexion internet.

**Installer Piper :**

```bash
pip3 install piper-tts pathvalidate --break-system-packages
```

**Télécharger un modèle de voix française :**

```bash
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

**Configurer LibreLector pour utiliser Piper :**

Via l'interface : **☰ → Paramètres** → choisir "piper" et renseigner le chemin du modèle.

Ou manuellement dans `~/.local/share/LibreLector/settings.json` :

```json
{
  "tts_engine": "piper",
  "piper_model": "/home/VOTRE_USER/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr"
}
```

Remplacez `VOTRE_USER` par votre nom d'utilisateur Linux.

> Les paramètres sont pris en compte au prochain lancement de l'application.

**Autres voix disponibles :** [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)
(choisir `fr/fr_FR/` pour le français, télécharger les fichiers `.onnx` et `.onnx.json`)

### Speech Dispatcher — voix robot (fallback)

Speech Dispatcher est le système de TTS intégré à Linux (voix espeak-ng par défaut).
La qualité sonore est robotique mais il fonctionne sans aucune configuration.

Il est utilisé automatiquement si Piper n'est pas installé ou mal configuré.

**Comment savoir quel moteur est actif ?**

Après l'ouverture d'un livre, un message apparaît brièvement en bas de l'écran :
- _"Voix : Piper (neuronale)"_ → Piper est actif, voix naturelle
- _"Voix : Speech Dispatcher (robot)"_ → Piper n'est pas configuré correctement

---

## 10. Paramètres

Accès : **☰ (menu hamburger) → Paramètres**

| Paramètre | Description |
|---|---|
| **Moteur TTS** | `piper` ou `speech_dispatcher` |
| **Chemin modèle Piper** | Chemin complet vers le fichier `.onnx` de la voix |
| **Code langue** | `fr` pour français, `en` pour anglais, etc. |

Les modifications sont sauvegardées immédiatement mais prennent effet au prochain lancement.

---

## 11. Export MP3

LibreLector peut convertir un livre entier en fichiers MP3, un fichier par chapitre.

**Prérequis :** Piper configuré + FFmpeg installé (`sudo apt install ffmpeg`)

**Lancer l'export :** **☰ → Exporter en MP3…**

Les fichiers sont générés dans `~/Music/LibreLector/[Titre du livre]/`.
Chaque chapitre devient un fichier `chapitre_01.mp3`, `chapitre_02.mp3`, etc.

L'export se fait en arrière-plan. Une barre de progression indique l'avancement.

---

## 12. Dictionnaire de prononciation

Certains mots (sigles, noms propres, termes techniques) sont mal prononcés par les moteurs TTS.
Vous pouvez corriger leur prononciation dans le fichier :

```
~/.local/share/LibreLector/pronunciation.json
```

**Format :**

```json
{
  "LLM": "L L M",
  "Kubernetes": "koubernetesse",
  "GPU": "gépéu",
  "EPUB": "é pu b"
}
```

La clé est le mot tel qu'il apparaît dans le texte, la valeur est la transcription phonétique
à lire à la place. Les corrections sont appliquées en temps réel à chaque phrase lue.

---

## 13. Données sauvegardées

Toutes les données de LibreLector sont stockées dans :

```
~/.local/share/LibreLector/
├── metadata.db          # Base SQLite : livres, dossiers, progression, marque-pages
├── settings.json        # Préférences : moteur TTS, modèle Piper, langue
├── pronunciation.json   # Dictionnaire de prononciation personnalisé
└── voices/              # Modèles de voix Piper (.onnx et .onnx.json)
```

**La base `metadata.db` contient :**
- La liste des livres ajoutés (titre, auteur, chemin du fichier)
- Les dossiers créés et l'appartenance de chaque livre
- La position de lecture de chaque livre (chapitre + phrase)
- Les marque-pages

**Supprimer des données :**
- Supprimer un livre de la bibliothèque : bouton `···` → "Supprimer de la bibliothèque"
- Supprimer toutes les données : supprimer le dossier `~/.local/share/LibreLector/`

---

## 14. Dépannage

### Aucun son au lancement

1. Vérifiez que le volume système n'est pas coupé
2. Vérifiez que Speech Dispatcher fonctionne : `spd-say "test"`
3. Si vous utilisez Piper, vérifiez que `piper` est dans votre PATH : `which piper`

### La voix reste robotique malgré Piper installé

Lancez l'application depuis un terminal pour voir les logs :

```bash
librelector 2>&1 | grep -i piper
```

Causes fréquentes :
- Le `settings.json` contient une erreur de syntaxe JSON → vérifiez avec `python3 -m json.tool ~/.local/share/LibreLector/settings.json`
- Le chemin du modèle `.onnx` est incorrect → vérifiez que le fichier existe : `ls ~/.local/share/LibreLector/voices/`
- Le module `pathvalidate` est manquant → `pip3 install pathvalidate --break-system-packages`

### L'application ne trouve pas un livre

LibreLector mémorise le **chemin absolu** du fichier EPUB. Si vous avez déplacé ou renommé
le fichier, supprimez-le de la bibliothèque et ajoutez-le à nouveau depuis son nouvel emplacement.

### Délai au début de la lecture

Un délai de 1 à 2 secondes au démarrage est normal : Piper charge le modèle de voix.
Ce chargement n'a lieu qu'une seule fois par chapitre, la lecture est ensuite continue.

### L'export MP3 échoue

- Vérifiez que FFmpeg est installé : `ffmpeg -version`
- Vérifiez que Piper est configuré (l'export utilise Piper, pas Speech Dispatcher)
- Vérifiez que le dossier `~/Music/LibreLector/` est accessible en écriture
