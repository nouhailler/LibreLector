import { useState } from 'react'
import { useStore } from '../../store/useStore'

interface Props {
  highlightedText: string
  chapterOrder: number
  sentenceIndex: number
  charStart: number
  charEnd: number
  onClose: () => void
}

export function NoteDialog({ highlightedText, chapterOrder, sentenceIndex, charStart, charEnd, onClose }: Props) {
  const addNote = useStore(s => s.addNote)
  const [content, setContent] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!content.trim()) return
    setSaving(true)
    try {
      await addNote({
        chapter_order: chapterOrder,
        sentence_index: sentenceIndex,
        char_start: charStart,
        char_end: charEnd,
        highlighted_text: highlightedText,
        content: content.trim(),
      })
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-slate-800 rounded-xl shadow-2xl w-full max-w-md mx-4 flex flex-col gap-4 p-5"
        onClick={e => e.stopPropagation()}
      >
        <h2 className="text-base font-semibold text-slate-100">📝 Nouvelle note</h2>

        {/* Texte surligné */}
        {highlightedText && (
          <blockquote className="border-l-2 border-yellow-400 pl-3 text-sm text-slate-300 italic line-clamp-3">
            « {highlightedText} »
          </blockquote>
        )}

        {/* Champ note */}
        <textarea
          autoFocus
          value={content}
          onChange={e => setContent(e.target.value)}
          placeholder="Écrivez votre note…"
          className="bg-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm resize-none h-28 focus:outline-none focus:ring-2 focus:ring-yellow-400"
          onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSave() }}
        />

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-sm text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-700 transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={!content.trim() || saving}
            className="px-4 py-1.5 text-sm bg-yellow-500 hover:bg-yellow-400 text-slate-900 font-medium rounded-lg disabled:opacity-40 transition-colors"
          >
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </div>
        <p className="text-xs text-slate-500 -mt-2">Ctrl+Entrée pour enregistrer rapidement</p>
      </div>
    </div>
  )
}
