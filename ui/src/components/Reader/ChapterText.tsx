import { useEffect, useRef, useState, useCallback } from 'react'
import { useStore } from '../../store/useStore'
import { NoteDialog } from '../Notes/NoteDialog'

interface SelectionInfo {
  text: string
  sentenceIndex: number
  charStart: number
  charEnd: number
  x: number
  y: number
}

export function ChapterText() {
  const { currentChapterContent, currentChapterOrder, currentSentenceIndex, playerState, goToSentence, isLoadingChapter, addHighlight, setNotesOpen } = useStore(s => ({
    currentChapterContent: s.currentChapterContent,
    currentChapterOrder: s.currentChapterOrder,
    currentSentenceIndex: s.currentSentenceIndex,
    playerState: s.playerState,
    goToSentence: s.goToSentence,
    isLoadingChapter: s.isLoadingChapter,
    addHighlight: s.addHighlight,
    setNotesOpen: s.setNotesOpen,
  }))

  const activeRef = useRef<HTMLSpanElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  // Bouton flottant (disparaît au clic ailleurs)
  const [floatingBtn, setFloatingBtn] = useState<SelectionInfo | null>(null)
  // Copie gelée utilisée par la dialog (survive à setFloatingBtn(null))
  const [pendingNote, setPendingNote] = useState<SelectionInfo | null>(null)
  const [noteDialogOpen, setNoteDialogOpen] = useState(false)

  // Auto-scroll vers la phrase active
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [currentSentenceIndex])

  // Masquer le bouton flottant au clic hors de lui
  useEffect(() => {
    const hide = (e: MouseEvent) => {
      const btn = document.getElementById('note-float-menu')
      if (btn && btn.contains(e.target as Node)) return
      setFloatingBtn(null)
    }
    document.addEventListener('mousedown', hide)
    return () => document.removeEventListener('mousedown', hide)
  }, [])

  const handleMouseUp = useCallback(() => {
    const sel = window.getSelection()
    if (!sel || sel.isCollapsed || !sel.toString().trim()) {
      setFloatingBtn(null)
      return
    }

    const text = sel.toString().trim()
    const range = sel.getRangeAt(0)
    const rect = range.getBoundingClientRect()
    const containerRect = containerRef.current?.getBoundingClientRect()
    if (!containerRect) return

    // Trouver quelle phrase est sélectionnée
    let node: Node | null = range.startContainer
    while (node && node !== containerRef.current) {
      if (node instanceof HTMLElement && node.dataset.sentenceIndex !== undefined) {
        const idx = parseInt(node.dataset.sentenceIndex, 10)
        const sentence = currentChapterContent?.sentences[idx]
        if (sentence) {
          setFloatingBtn({
            text,
            sentenceIndex: idx,
            charStart: sentence.char_start,
            charEnd: sentence.char_end,
            x: rect.left - containerRect.left + rect.width / 2,
            y: rect.top - containerRect.top - 8,
          })
          return
        }
      }
      node = node.parentNode
    }

    // Fallback : première phrase
    const first = currentChapterContent?.sentences[0]
    setFloatingBtn({
      text,
      sentenceIndex: 0,
      charStart: first?.char_start ?? 0,
      charEnd: first?.char_end ?? text.length,
      x: rect.left - containerRect.left + rect.width / 2,
      y: rect.top - containerRect.top - 8,
    })
  }, [currentChapterContent])

  function openNoteDialog() {
    if (!floatingBtn) return
    setPendingNote({ ...floatingBtn })
    setFloatingBtn(null)
    setNoteDialogOpen(true)
  }

  async function saveHighlight() {
    if (!floatingBtn) return
    const info = { ...floatingBtn }
    setFloatingBtn(null)
    window.getSelection()?.removeAllRanges()
    await addHighlight({
      chapter_order: currentChapterOrder,
      sentence_index: info.sentenceIndex,
      char_start: info.charStart,
      char_end: info.charEnd,
      highlighted_text: info.text,
    })
    setNotesOpen(true)
  }

  if (isLoadingChapter) {
    return <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">Chargement…</div>
  }

  if (!currentChapterContent) {
    return <div className="flex-1" />
  }

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto px-8 py-6 relative select-text">
      <h2 className="text-lg font-semibold text-slate-200 mb-4">{currentChapterContent.title}</h2>

      <div className="text-slate-300 leading-relaxed text-base" onMouseUp={handleMouseUp}>
        {currentChapterContent.sentences.map(s => {
          const isActive = s.index === currentSentenceIndex && (playerState === 'playing' || playerState === 'paused')
          return (
            <span
              key={s.index}
              ref={isActive ? activeRef : null}
              data-sentence-index={s.index}
              onClick={() => goToSentence(s.index)}
              className={`cursor-pointer rounded px-0.5 transition-colors ${isActive ? 'sentence-active' : 'hover:bg-slate-700/50'}`}
            >
              {s.text}{' '}
            </span>
          )
        })}
      </div>

      {/* Menu flottant deux actions — id utilisé par le guard mousedown */}
      {floatingBtn && (
        <div
          id="note-float-menu"
          style={{ left: floatingBtn.x, top: floatingBtn.y }}
          className="absolute -translate-x-1/2 -translate-y-full flex gap-1 z-20"
        >
          <button
            onClick={saveHighlight}
            className="bg-orange-500 hover:bg-orange-400 text-white text-xs font-semibold px-3 py-1.5 rounded-l shadow-lg whitespace-nowrap transition-colors"
            title="Sauvegarder le surlignage sans note"
          >
            🖊 Surligner
          </button>
          <button
            onClick={openNoteDialog}
            className="bg-yellow-400 hover:bg-yellow-300 text-slate-900 text-xs font-semibold px-3 py-1.5 rounded-r shadow-lg whitespace-nowrap transition-colors"
            title="Ajouter une note à ce passage"
          >
            📝 Note
          </button>
        </div>
      )}

      {/* Dialog de création de note — utilise pendingNote, survive à floatingBtn=null */}
      {noteDialogOpen && pendingNote && (
        <NoteDialog
          highlightedText={pendingNote.text}
          chapterOrder={currentChapterOrder}
          sentenceIndex={pendingNote.sentenceIndex}
          charStart={pendingNote.charStart}
          charEnd={pendingNote.charEnd}
          onClose={() => { setNoteDialogOpen(false); setPendingNote(null) }}
        />
      )}
    </div>
  )
}
