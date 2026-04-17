import { useState } from 'react'

interface Section {
  id: string
  label: string
  icon: string
}

const SECTIONS: Section[] = [
  { id: 'intro',      label: 'Présentation',        icon: '📖' },
  { id: 'demarrage', label: 'Démarrage rapide',     icon: '🚀' },
  { id: 'bibliotheque', label: 'Bibliothèque',      icon: '📚' },
  { id: 'lecture',   label: 'Lecture & surlignage', icon: '🎧' },
  { id: 'controles', label: 'Contrôles du lecteur', icon: '⏯' },
  { id: 'parametres', label: 'Paramètres TTS',      icon: '⚙' },
  { id: 'export',    label: 'Export MP3',            icon: '🎵' },
  { id: 'erreurs',   label: 'Erreurs & solutions',  icon: '🔧' },
]

interface Props {
  onClose: () => void
}

export function HelpModal({ onClose }: Props) {
  const [activeSection, setActiveSection] = useState('intro')

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-slate-800 rounded-xl shadow-2xl w-full max-w-4xl h-[85vh] flex flex-col overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-700 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📖</span>
            <div>
              <h1 className="text-base font-bold text-slate-100">Documentation LibreLector</h1>
              <p className="text-xs text-slate-400">Guide complet — v1.0</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xl px-2">✕</button>
        </div>

        {/* Body */}
        <div className="flex flex-1 min-h-0">
          {/* Sidebar */}
          <nav className="w-52 shrink-0 bg-slate-900 border-r border-slate-700 overflow-y-auto py-2">
            {SECTIONS.map(s => (
              <button
                key={s.id}
                onClick={() => setActiveSection(s.id)}
                className={`w-full text-left flex items-center gap-2 px-4 py-2.5 text-sm transition-colors ${
                  activeSection === s.id
                    ? 'bg-blue-600/20 text-blue-300 border-l-2 border-blue-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span>{s.icon}</span>
                <span>{s.label}</span>
              </button>
            ))}
          </nav>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-8 py-6 text-slate-300 text-sm leading-relaxed">
            {activeSection === 'intro'      && <SectionIntro />}
            {activeSection === 'demarrage' && <SectionDemarrage />}
            {activeSection === 'bibliotheque' && <SectionBibliotheque />}
            {activeSection === 'lecture'   && <SectionLecture />}
            {activeSection === 'controles' && <SectionControles />}
            {activeSection === 'parametres' && <SectionParametres />}
            {activeSection === 'export'    && <SectionExport />}
            {activeSection === 'erreurs'   && <SectionErreurs />}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Composants utilitaires ────────────────────────────────────────────────────

function H2({ children }: { children: React.ReactNode }) {
  return <h2 className="text-base font-bold text-slate-100 mb-3 mt-6 first:mt-0">{children}</h2>
}

function H3({ children }: { children: React.ReactNode }) {
  return <h3 className="text-sm font-semibold text-slate-200 mb-2 mt-4">{children}</h3>
}

function P({ children }: { children: React.ReactNode }) {
  return <p className="mb-3 text-slate-300">{children}</p>
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code className="bg-slate-900 text-green-400 px-1.5 py-0.5 rounded text-xs font-mono">
      {children}
    </code>
  )
}

function Callout({ type, children }: { type: 'info' | 'warn' | 'error' | 'ok'; children: React.ReactNode }) {
  const styles = {
    info:  'bg-blue-900/30 border-blue-500 text-blue-200',
    warn:  'bg-yellow-900/30 border-yellow-500 text-yellow-200',
    error: 'bg-red-900/30 border-red-500 text-red-200',
    ok:    'bg-green-900/30 border-green-500 text-green-200',
  }
  const icons = { info: 'ℹ', warn: '⚠', error: '✕', ok: '✓' }
  return (
    <div className={`flex gap-2 border-l-4 px-3 py-2 rounded-r mb-3 text-xs ${styles[type]}`}>
      <span className="shrink-0 font-bold">{icons[type]}</span>
      <span>{children}</span>
    </div>
  )
}

function Steps({ items }: { items: string[] }) {
  return (
    <ol className="mb-3 flex flex-col gap-1">
      {items.map((item, i) => (
        <li key={i} className="flex gap-2 items-start">
          <span className="shrink-0 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold mt-0.5">
            {i + 1}
          </span>
          <span>{item}</span>
        </li>
      ))}
    </ol>
  )
}

function Table({ rows }: { rows: [string, string][] }) {
  return (
    <table className="w-full mb-4 text-xs border-collapse">
      <tbody>
        {rows.map(([label, desc], i) => (
          <tr key={i} className="border-b border-slate-700">
            <td className="py-2 pr-4 font-mono text-slate-200 whitespace-nowrap w-40">{label}</td>
            <td className="py-2 text-slate-400">{desc}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// ── Sections ──────────────────────────────────────────────────────────────────

function SectionIntro() {
  return (
    <>
      <H2>Présentation de LibreLector</H2>
      <P>
        LibreLector est un lecteur de livres numériques (EPUB) conçu <strong className="text-slate-100">prioritairement pour l'écoute</strong>.
        Il utilise une synthèse vocale neuronale hors-ligne via <strong className="text-slate-100">Piper TTS</strong>
        pour produire des voix naturelles, et surligne chaque phrase au fil de la lecture.
      </P>

      <H3>Fonctionnalités principales</H3>
      <Table rows={[
        ['Lecture EPUB',      'Ouverture et parsing de livres au format EPUB 2 et EPUB 3'],
        ['TTS neural',        'Synthèse vocale Piper (voix neuronales offline, qualité naturelle)'],
        ['TTS système',       'Fallback Speech Dispatcher si Piper n\'est pas disponible'],
        ['Surlignage',        'Chaque phrase lue est surlignée en temps réel dans le texte'],
        ['Clic sur phrase',   'Double-clic sur n\'importe quelle phrase pour démarrer depuis ce point'],
        ['Navigation',        'Table des matières cliquable, boutons chapitre précédent/suivant'],
        ['Bibliothèque',      'Gestion des livres avec dossiers thématiques, mémorisation de la position'],
        ['Export MP3',        'Conversion d\'un chapitre en fichier MP3 via Piper + FFmpeg'],
        ['Paramètres',        'Sélection du moteur TTS, du modèle de voix, de la langue'],
        ['Vitesse & volume',  'Contrôle de la vitesse de lecture (0.5× à 2×) et du volume'],
      ]} />

      <H3>Architecture</H3>
      <P>
        L'application fonctionne en deux parties qui communiquent en local :
      </P>
      <ul className="mb-3 flex flex-col gap-1 list-none">
        <li className="flex gap-2"><span className="text-blue-400">●</span><span><strong className="text-slate-200">Backend Python (port 7531)</strong> — FastAPI + Piper TTS. Gère le parsing EPUB, la synthèse vocale, la bibliothèque SQLite et l'export MP3.</span></li>
        <li className="flex gap-2"><span className="text-blue-400">●</span><span><strong className="text-slate-200">Frontend React (Vite)</strong> — Interface web. Communique avec le backend via une API REST et un WebSocket pour le surlignage en temps réel.</span></li>
      </ul>
      <Callout type="info">
        Le backend doit être lancé avant d'ouvrir l'interface. Si vous utilisez Tauri (version bureau), il démarre automatiquement.
      </Callout>
    </>
  )
}

function SectionDemarrage() {
  return (
    <>
      <H2>Démarrage rapide</H2>

      <H3>Prérequis système</H3>
      <Table rows={[
        ['Python 3.11+',     'Interpréteur Python — sudo apt install python3'],
        ['pip3',             'Gestionnaire de paquets Python'],
        ['Node.js 20+',      'Pour le frontend React — nodejs.org'],
        ['FFmpeg',           'Pour l\'export MP3 — sudo apt install ffmpeg'],
        ['aplay',            'Pour la lecture audio — sudo apt install alsa-utils'],
        ['Piper TTS',        'Moteur de voix neuronales — pip3 install piper-tts'],
        ['Modèle de voix',   'Fichier .onnx à télécharger (ex. fr_FR-siwis-medium)'],
      ]} />

      <H3>Lancement en mode développement</H3>
      <Steps items={[
        'Ouvrir un premier terminal et lancer le backend :',
      ]} />
      <div className="bg-slate-900 rounded p-3 mb-3 font-mono text-xs text-green-400">
        cd /home/patrick/claude-workspace/LibreLector/.claude/worktrees/hardcore-bhabha-6749ee<br />
        pip3 install -e . --break-system-packages<br />
        python3 -m librelector.api.server
      </div>
      <Steps items={[
        'Ouvrir un second terminal et lancer le frontend :',
      ]} />
      <div className="bg-slate-900 rounded p-3 mb-3 font-mono text-xs text-green-400">
        cd .../hardcore-bhabha-6749ee/ui<br />
        npm install && npm run dev
      </div>
      <Steps items={[
        'Ouvrir http://localhost:5173 dans votre navigateur.',
        'Vérifier que le backend répond : http://localhost:7531/api/health → {"status":"ok"}',
      ]} />

      <H3>Premier livre</H3>
      <Steps items={[
        'Cliquer sur « + Ouvrir EPUB » dans la barre du haut.',
        'Sélectionner un fichier .epub sur votre disque.',
        'Le livre apparaît dans la bibliothèque (panneau gauche).',
        'Cliquer sur le livre pour l\'ouvrir dans le lecteur.',
        'Configurer Piper dans « ⚙ Paramètres » si ce n\'est pas encore fait.',
        'Cliquer sur ▶ pour démarrer la lecture.',
      ]} />

      <Callout type="warn">
        Sans Piper configuré, la synthèse vocale utilisera Speech Dispatcher (voix robot système). Configurez Piper pour une expérience optimale.
      </Callout>
    </>
  )
}

function SectionBibliotheque() {
  return (
    <>
      <H2>Bibliothèque</H2>
      <P>
        La bibliothèque (panneau gauche) affiche tous vos livres organisés en dossiers. Les données sont persistées dans une base SQLite locale.
      </P>

      <H3>Ajouter un livre</H3>
      <P>
        Cliquer sur <strong className="text-slate-100">« + Ouvrir EPUB »</strong> dans la barre supérieure. Le fichier EPUB est copié dans <Code>~/.local/share/LibreLector/books/</Code> et enregistré dans la bibliothèque. La position de lecture est mémorisée automatiquement.
      </P>

      <H3>Supprimer un livre</H3>
      <P>
        Survoler un livre et cliquer sur le <strong className="text-slate-100">✕</strong> rouge qui apparaît. Le livre est retiré de la bibliothèque mais le fichier EPUB sur le disque n'est pas supprimé.
      </P>

      <H3>Dossiers thématiques</H3>
      <Steps items={[
        'Cliquer sur « 📁+ » en haut du panneau bibliothèque.',
        'Saisir le nom du dossier et valider avec Entrée ou OK.',
        'Pour renommer un dossier : double-cliquer sur son nom.',
        'Pour supprimer un dossier : survoler et cliquer ✕ (les livres sont déplacés dans « Sans dossier »).',
        'Pour déplacer un livre dans un dossier : fonctionnalité à venir (actuellement via l\'API).',
      ]} />

      <H3>Mémorisation de la position</H3>
      <P>
        À chaque pause ou arrêt, LibreLector sauvegarde automatiquement le chapitre et la phrase en cours. À la réouverture d'un livre, la lecture reprend depuis cette position.
      </P>
    </>
  )
}

function SectionLecture() {
  return (
    <>
      <H2>Lecture & surlignage synchronisé</H2>

      <H3>Principe</H3>
      <P>
        Quand la lecture est active, chaque phrase est surlignée en <strong className="text-yellow-400">jaune</strong> au moment où Piper la synthétise. Le texte défile automatiquement pour garder la phrase active visible.
      </P>
      <Callout type="info">
        Le surlignage est transmis par WebSocket en temps réel depuis le backend. Un délai de quelques millisecondes est normal — il est lié à la vitesse de synthèse de Piper, pas à un bug.
      </Callout>

      <H3>Navigation dans le texte</H3>
      <Table rows={[
        ['Clic sur une phrase',       'Démarre la lecture depuis cette phrase (arrête la lecture en cours)'],
        ['Clic sur un chapitre (TOC)', 'Charge le chapitre et démarre la lecture depuis le début'],
        ['⏮ / ⏭',                    'Chapitre précédent / suivant'],
        ['Auto-avancement',           'En fin de chapitre, le suivant démarre automatiquement'],
      ]} />

      <H3>Table des matières</H3>
      <P>
        Le panneau central gauche liste tous les chapitres du livre. Le chapitre actif est surligné en bleu. Cliquer sur un chapitre charge son texte et démarre la lecture.
      </P>

      <H3>Vitesse de lecture</H3>
      <P>
        Le curseur <strong className="text-slate-100">Vitesse</strong> dans la barre de contrôle ajuste la vitesse de synthèse Piper (0.5× à 2×). La valeur 1.0× correspond au débit normal. Le surlignage s'adapte automatiquement.
      </P>
    </>
  )
}

function SectionControles() {
  return (
    <>
      <H2>Contrôles du lecteur</H2>
      <P>La barre de contrôle est affichée en bas du panneau de lecture.</P>

      <H3>Boutons de transport</H3>
      <Table rows={[
        ['⏮  Chapitre précédent', 'Retourne au chapitre précédent et démarre la lecture'],
        ['▶  Lecture',            'Démarre la lecture depuis la position mémorisée'],
        ['⏸  Pause',              'Met en pause (position mémorisée)'],
        ['⏹  Arrêt',              'Arrête la lecture et réinitialise Piper'],
        ['⏭  Chapitre suivant',   'Avance au chapitre suivant et démarre la lecture'],
      ]} />

      <H3>Contrôles de vitesse et volume</H3>
      <Table rows={[
        ['Vitesse (0.5× – 2×)', 'Curseur de vitesse de synthèse. Appliqué au prochain chapitre lancé.'],
        ['🔊 Volume (0 – 1)',    'Curseur de volume audio. Appliqué en temps réel via le système.'],
      ]} />

      <Callout type="warn">
        Avec le moteur Piper, la vitesse ne peut pas être modifiée en cours de lecture (limitation de l'architecture subprocess). Elle sera prise en compte au prochain chapitre ou après un arrêt/relance.
      </Callout>

      <H3>Bouton 🎵 MP3</H3>
      <P>
        Affiché à droite du titre du livre. Ouvre la fenêtre d'export MP3 pour le chapitre courant.
      </P>
    </>
  )
}

function SectionParametres() {
  return (
    <>
      <H2>Paramètres TTS</H2>
      <P>
        Accessible via le bouton <strong className="text-slate-100">⚙ Paramètres</strong> dans la barre supérieure.
      </P>

      <H3>Moteur TTS</H3>
      <Table rows={[
        ['Piper (neural, offline)',       'Voix neuronales haute qualité. Requiert le binaire piper et un fichier modèle .onnx.'],
        ['Speech Dispatcher (système)',   'Voix système (qualité robot). Fonctionne sans installation supplémentaire si speech-dispatcher est installé.'],
      ]} />

      <H3>Modèle Piper</H3>
      <P>
        Si des modèles <Code>.onnx</Code> sont présents dans <Code>~/.local/share/LibreLector/voices/</Code>, ils apparaissent dans une liste déroulante. Sinon, saisir manuellement le chemin complet vers le fichier <Code>.onnx</Code>.
      </P>

      <H3>Installer un modèle de voix française</H3>
      <div className="bg-slate-900 rounded p-3 mb-3 font-mono text-xs text-green-400">
        mkdir -p ~/.local/share/LibreLector/voices<br />
        cd ~/.local/share/LibreLector/voices<br />
        wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx<br />
        wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
      </div>
      <P>
        Puis dans Paramètres, sélectionner <Code>fr_FR-siwis-medium</Code> et cliquer Enregistrer.
      </P>

      <H3>Dictionnaire de prononciation</H3>
      <P>
        Le fichier <Code>~/.local/share/LibreLector/pronunciation.json</Code> permet de corriger des prononciations incorrectes. Format : <Code>{'{"mot": "prononciation"}'}</Code>. Les corrections sont appliquées avant chaque synthèse.
      </P>
    </>
  )
}

function SectionExport() {
  return (
    <>
      <H2>Export MP3</H2>
      <P>
        LibreLector peut convertir un chapitre en fichier MP3 via la chaîne <strong className="text-slate-100">Piper → FFmpeg</strong>. Utile pour écouter hors-ligne ou créer un podcast personnel.
      </P>

      <H3>Comment exporter</H3>
      <Steps items={[
        'Ouvrir un livre et naviguer vers le chapitre à exporter.',
        'Cliquer sur « 🎵 MP3 » en haut à droite du panneau de lecture.',
        'Cliquer sur « Exporter ce chapitre en MP3 ».',
        'Patienter — Piper synthétise tout le chapitre, puis FFmpeg encode en MP3.',
        'Le chemin du fichier généré s\'affiche en vert une fois terminé.',
      ]} />

      <H3>Emplacement des fichiers</H3>
      <P>
        Les MP3 sont enregistrés dans <Code>~/Musique/LibreLector/</Code> (ou <Code>/tmp/librelector_export/</Code> si le dossier Musique n'est pas accessible). Le nom du fichier suit le format : <Code>001_Titre_du_chapitre.mp3</Code>.
      </P>

      <Callout type="warn">
        L'export peut prendre plusieurs minutes pour un long chapitre. Ne pas fermer la fenêtre d'export pendant le traitement.
      </Callout>

      <H3>Prérequis pour l'export</H3>
      <Table rows={[
        ['Piper TTS',    'Le binaire piper doit être dans le PATH : pip3 install piper-tts'],
        ['FFmpeg',       'sudo apt install ffmpeg'],
        ['Modèle .onnx', 'Configuré dans les Paramètres'],
      ]} />
    </>
  )
}

function SectionErreurs() {
  return (
    <>
      <H2>Erreurs courantes & solutions</H2>

      <H3>Démarrage de l'application</H3>

      <Callout type="error">
        <strong>« No module named librelector »</strong> — Le package Python n'est pas installé.
        <br />Solution : <Code>pip3 install -e . --break-system-packages</Code> depuis le répertoire du projet.
      </Callout>

      <Callout type="error">
        <strong>« Address already in use (port 7531) »</strong> — Un autre processus occupe le port.
        <br />Solution : <Code>kill $(lsof -ti:7531)</Code> puis relancer le backend.
      </Callout>

      <Callout type="error">
        <strong>L'interface reste blanche ou affiche une erreur réseau</strong> — Le backend n'est pas démarré ou a crashé.
        <br />Solution : vérifier que <Code>python3 -m librelector.api.server</Code> tourne, puis recharger la page.
      </Callout>

      <Callout type="error">
        <strong>WebSocket déconnecté (console navigateur)</strong> — La connexion temps réel est coupée.
        <br />Solution : l'application tente de se reconnecter automatiquement toutes les 2 secondes. Si le problème persiste, redémarrer le backend.
      </Callout>

      <H3>Chargement d'un EPUB</H3>

      <Callout type="error">
        <strong>« Erreur ouverture EPUB »</strong> — Le fichier EPUB est corrompu ou dans un format non supporté.
        <br />Solution : vérifier le fichier avec Calibre ou un autre outil. Les EPUB protégés par DRM ne sont pas supportés.
      </Callout>

      <Callout type="error">
        <strong>Le livre s'affiche sans texte / chapitres vides</strong> — Le parser ne reconnaît pas la structure du fichier.
        <br />Cause : certains EPUB utilisent des chapitres très courts (artefacts de navigation) qui sont filtrés automatiquement si leur texte fait moins de 100 caractères. Ce comportement est normal.
      </Callout>

      <Callout type="warn">
        <strong>Accents ou caractères spéciaux manquants</strong> — Problème d'encodage dans l'EPUB source.
        <br />Solution : re-exporter l'EPUB depuis Calibre en forçant l'encodage UTF-8.
      </Callout>

      <H3>Synthèse vocale (Piper)</H3>

      <Callout type="error">
        <strong>« Piper non disponible »</strong> — Le binaire <Code>piper</Code> n'est pas dans le PATH.
        <br />Solution : <Code>pip3 install piper-tts --break-system-packages</Code>. Vérifier avec <Code>which piper</Code>.
      </Callout>

      <Callout type="error">
        <strong>« Modèle Piper introuvable »</strong> — Le chemin vers le fichier <Code>.onnx</Code> est incorrect dans les paramètres.
        <br />Solution : vérifier l'existence du fichier et corriger le chemin dans ⚙ Paramètres.
      </Callout>

      <Callout type="error">
        <strong>Pas de son pendant la lecture</strong> — <Code>aplay</Code> (ALSA) n'est pas installé ou le périphérique audio n'est pas disponible.
        <br />Solution : <Code>sudo apt install alsa-utils</Code>. Vérifier avec <Code>aplay -l</Code> que des périphériques audio sont listés.
      </Callout>

      <Callout type="warn">
        <strong>Le surlignage avance mais on n'entend rien</strong> — Le volume système est à zéro ou le mauvais périphérique de sortie est sélectionné.
        <br />Solution : vérifier le volume avec <Code>alsamixer</Code> et le périphérique par défaut dans les paramètres ALSA.
      </Callout>

      <Callout type="warn">
        <strong>Voix haché ou avec des silences</strong> — Piper est surchargé ou le modèle est trop lourd pour la machine.
        <br />Solution : réduire la vitesse de lecture ou essayer un modèle plus léger (ex. « low » au lieu de « medium »).
      </Callout>

      <H3>Export MP3</H3>

      <Callout type="error">
        <strong>« Piper ou ffmpeg non disponible »</strong> — L'un des deux outils manque.
        <br />Solution : <Code>pip3 install piper-tts</Code> et <Code>sudo apt install ffmpeg</Code>.
      </Callout>

      <Callout type="error">
        <strong>« Aucun modèle Piper configuré »</strong> — Le champ modèle est vide dans les Paramètres.
        <br />Solution : ouvrir ⚙ Paramètres, sélectionner ou saisir le chemin du modèle <Code>.onnx</Code>.
      </Callout>

      <Callout type="error">
        <strong>Fichier MP3 vide après export</strong> — FFmpeg a reçu des données audio vides de Piper.
        <br />Solution : vérifier que le chapitre contient du texte, et que le modèle <Code>.onnx.json</Code> (fichier de configuration) est présent à côté du <Code>.onnx</Code>.
      </Callout>

      <Callout type="error">
        <strong>L'export semble bloqué</strong> — Piper prend du temps sur un long chapitre (normal).
        <br />Solution : patienter. Pour les chapitres très longs (&gt; 5 000 mots), l'export peut prendre 5 à 15 minutes. La fenêtre d'export affiche la progression.
      </Callout>

      <H3>Speech Dispatcher (fallback)</H3>

      <Callout type="error">
        <strong>« No TTS engine available »</strong> — Ni Piper ni Speech Dispatcher ne sont disponibles.
        <br />Solution : <Code>sudo apt install speech-dispatcher</Code> et/ou configurer Piper.
      </Callout>

      <Callout type="warn">
        <strong>Speech Dispatcher ne produit pas de son</strong> — Le service n'est pas démarré.
        <br />Solution : <Code>systemctl --user start speech-dispatcher</Code> ou <Code>speech-dispatcher -d</Code>.
      </Callout>

      <H3>Données & base de données</H3>

      <Callout type="error">
        <strong>La bibliothèque est vide au redémarrage</strong> — La base SQLite est inaccessible.
        <br />Solution : vérifier les droits sur <Code>~/.local/share/LibreLector/metadata.db</Code>. Si le fichier est corrompu, le supprimer (les livres ne sont pas perdus, seulement les métadonnées).
      </Callout>

      <Callout type="warn">
        <strong>settings.json invalide</strong> — Le fichier de configuration est malformé.
        <br />Solution : supprimer <Code>~/.local/share/LibreLector/settings.json</Code> pour revenir aux valeurs par défaut, puis reconfigurer via ⚙ Paramètres.
      </Callout>
    </>
  )
}
