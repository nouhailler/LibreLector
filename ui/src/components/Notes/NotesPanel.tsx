import { useState } from 'react'
import { useStore } from '../../store/useStore'
import type { Note, Bookmark } from '../../types'

type AnnotationItem =
  | { kind: 'note'; data: Note }
  | { kind: 'bookmark'; data: Bookmark }

export function NotesPanel() {
  const { notes, bookmarks, notesOpen, setNotesOpen, removeNote, editNote, removeBookmark, goToChapter, goToSentence, currentBook, chapters } = useStore(s => ({
    notes: s.notes,
    bookmarks: s.bookmarks,
    notesOpen: s.notesOpen,
    setNotesOpen: s.setNotesOpen,
    removeNote: s.removeNote,
    editNote: s.editNote,
    removeBookmark: s.removeBookmark,
    goToChapter: s.goToChapter,
    goToSentence: s.goToSentence,
    currentBook: s.currentBook,
    chapters: s.chapters,
  }))

  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')

  function chapterTitle(order: number): string {
    const ch = chapters.find(c => c.order === order)
    return ch ? `Chapitre ${order + 1} — ${ch.title}` : `Chapitre ${order + 1}`
  }

  function exportAnnotations() {
    if (!currentBook) return
    const date = new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
    const lines: string[] = []

    const sep = '═'.repeat(60)
    const thin = '─'.repeat(60)

    lines.push(sep)
    lines.push(`  ${currentBook.title}`)
    if (currentBook.author) lines.push(`  ${currentBook.author}`)
    lines.push(`  Exporté le ${date}`)
    lines.push(sep)

    // ── Notes ──────────────────────────────────────────────
    const noteItems = notes.filter(n => n.type === 'note')
    if (noteItems.length > 0) {
      lines.push('')
      lines.push(`📝  NOTES  (${noteItems.length})`)
      lines.push(thin)
      for (const n of noteItems) {
        lines.push('')
        lines.push(`▸ ${chapterTitle(n.chapter_order)} · Phrase ${n.sentence_index + 1}`)
        if (n.highlighted_text) lines.push(`  « ${n.highlighted_text} »`)
        lines.push(`  ${n.content}`)
      }
    }

    // ── Surlignages ────────────────────────────────────────
    const hlItems = notes.filter(n => n.type === 'highlight')
    if (hlItems.length > 0) {
      lines.push('')
      lines.push(`🖊  SURLIGNAGES  (${hlItems.length})`)
      lines.push(thin)
      for (const n of hlItems) {
        lines.push('')
        lines.push(`▸ ${chapterTitle(n.chapter_order)} · Phrase ${n.sentence_index + 1}`)
        lines.push(`  « ${n.highlighted_text} »`)
      }
    }

    // ── Marque-pages ───────────────────────────────────────
    if (bookmarks.length > 0) {
      lines.push('')
      lines.push(`🔖  MARQUE-PAGES  (${bookmarks.length})`)
      lines.push(thin)
      for (const b of bookmarks) {
        lines.push('')
        lines.push(`▸ ${chapterTitle(b.chapter_order)} · Phrase ${b.sentence_index + 1}`)
        if (b.label) lines.push(`  ${b.label}`)
      }
    }

    lines.push('')
    lines.push(sep)

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentBook.title.replace(/[^a-zA-Z0-9\u00C0-\u024F ]/g, '_')}_annotations.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Fusionner et trier toutes les annotations par position
  const items: AnnotationItem[] = [
    ...notes.map(n => ({ kind: 'note' as const, data: n })),
    ...bookmarks.map(b => ({ kind: 'bookmark' as const, data: b })),
  ].sort((a, b) => {
    const aChapter = a.data.chapter_order
    const bChapter = b.data.chapter_order
    if (aChapter !== bChapter) return aChapter - bChapter
    const aSentence = a.data.sentence_index
    const bSentence = b.data.sentence_index
    return aSentence - bSentence
  })

  const totalCount = notes.length + bookmarks.length

  function startEdit(note: Note) {
    setEditingId(note.id)
    setEditContent(note.content)
  }

  async function saveEdit(id: number) {
    if (editContent.trim()) await editNote(id, editContent.trim())
    setEditingId(null)
  }

  async function navigateTo(chapterOrder: number, sentenceIndex: number) {
    await goToChapter(chapterOrder)
    await goToSentence(sentenceIndex)
  }

  function formatDate(iso: string) {
    try {
      return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
    } catch {
      return iso.slice(0, 10)
    }
  }

  return (
    <>
      {/* Bouton toggle */}
      <button
        onClick={() => setNotesOpen(!notesOpen)}
        title={notesOpen ? 'Fermer les annotations' : 'Voir les annotations'}
        className={`shrink-0 px-2 py-1 text-xs rounded transition-colors ${
          notesOpen
            ? 'bg-yellow-500 text-slate-900 font-semibold'
            : 'text-slate-400 hover:text-slate-200 bg-slate-700 hover:bg-slate-600'
        }`}
      >
        📝 {totalCount > 0 ? `${totalCount} annotation${totalCount > 1 ? 's' : ''}` : 'Notes'}
      </button>

      {/* Panneau latéral */}
      {notesOpen && (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-slate-900 border-l border-slate-700 flex flex-col z-30 shadow-2xl">
          {/* En-tête */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700 shrink-0">
            <h2 className="text-sm font-semibold text-slate-100">
              Annotations ({totalCount})
            </h2>
            <div className="flex items-center gap-2">
              {totalCount > 0 && (
                <button
                  onClick={exportAnnotations}
                  className="text-xs text-slate-400 hover:text-slate-100 bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded transition-colors"
                  title="Exporter les annotations en fichier texte"
                >
                  ↓ Exporter
                </button>
              )}
              <button
                onClick={() => setNotesOpen(false)}
                className="text-slate-500 hover:text-slate-200 text-lg leading-none"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Légende */}
          {totalCount > 0 && (
            <div className="flex gap-3 px-4 py-2 border-b border-slate-800 text-xs text-slate-500">
              <span className="flex items-center gap-1"><span className="inline-block w-2 h-2 rounded-full bg-yellow-400" />Note</span>
              <span className="flex items-center gap-1"><span className="inline-block w-2 h-2 rounded-full bg-orange-400" />Surlignage</span>
              <span className="flex items-center gap-1"><span className="inline-block w-2 h-2 rounded-full bg-blue-400" />Marque-page</span>
            </div>
          )}

          {/* Liste */}
          <div className="flex-1 overflow-y-auto">
            {items.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-2 text-slate-500 text-sm px-4 text-center">
                <span className="text-3xl">📝</span>
                <p>Aucune annotation pour ce livre.</p>
                <p className="text-xs">Sélectionnez du texte pour surligner ou ajouter une note. Utilisez 🔖 pour poser un marque-page.</p>
              </div>
            ) : (
              <ul className="divide-y divide-slate-800">
                {items.map(item => {
                  if (item.kind === 'bookmark') {
                    const bm = item.data
                    return (
                      <li key={`bm-${bm.id}`} className="px-4 py-3 flex flex-col gap-2 hover:bg-slate-800/50 group">
                        {/* Bandeau marque-page */}
                        <div className="flex items-center gap-2">
                          <span className="text-base">🔖</span>
                          <div
                            className="flex-1 border-l-2 border-blue-400 pl-2 cursor-pointer"
                            onClick={() => navigateTo(bm.chapter_order, bm.sentence_index)}
                            title="Aller à ce marque-page"
                          >
                            {bm.label ? (
                              <p className="text-sm text-blue-300 font-medium">{bm.label}</p>
                            ) : (
                              <p className="text-xs text-slate-400 italic">Chapitre {bm.chapter_order + 1}, phrase {bm.sentence_index + 1}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-600">{formatDate(bm.created_at)}</span>
                          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => navigateTo(bm.chapter_order, bm.sentence_index)}
                              className="text-xs text-slate-500 hover:text-slate-200"
                              title="Aller au passage"
                            >
                              ↗
                            </button>
                            <button
                              onClick={() => removeBookmark(bm.id)}
                              className="text-xs text-slate-500 hover:text-red-400"
                              title="Supprimer"
                            >
                              🗑
                            </button>
                          </div>
                        </div>
                      </li>
                    )
                  }

                  // Note ou Surlignage
                  const note = item.data as Note
                  const isHighlight = note.type === 'highlight'
                  const borderColor = isHighlight ? 'border-orange-400' : 'border-yellow-400'
                  const icon = isHighlight ? '🖊' : '📝'

                  return (
                    <li key={`note-${note.id}`} className="px-4 py-3 flex flex-col gap-2 hover:bg-slate-800/50 group">
                      {/* Icône + texte surligné */}
                      <div className="flex items-start gap-2">
                        <span className="text-base shrink-0 mt-0.5">{icon}</span>
                        {note.highlighted_text && (
                          <blockquote
                            className={`border-l-2 ${borderColor} pl-2 text-xs text-slate-400 italic line-clamp-2 cursor-pointer hover:text-slate-200 transition-colors`}
                            onClick={() => navigateTo(note.chapter_order, note.sentence_index)}
                            title="Aller à ce passage"
                          >
                            « {note.highlighted_text} »
                          </blockquote>
                        )}
                      </div>

                      {/* Contenu de la note (absent pour les surlignages purs) */}
                      {!isHighlight && (
                        editingId === note.id ? (
                          <div className="flex flex-col gap-1">
                            <textarea
                              autoFocus
                              value={editContent}
                              onChange={e => setEditContent(e.target.value)}
                              className="bg-slate-700 text-slate-100 rounded px-2 py-1 text-xs resize-none h-20 focus:outline-none focus:ring-1 focus:ring-yellow-400"
                              onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) saveEdit(note.id) }}
                            />
                            <div className="flex gap-2">
                              <button onClick={() => saveEdit(note.id)} className="text-xs text-yellow-400 hover:text-yellow-300">Sauver</button>
                              <button onClick={() => setEditingId(null)} className="text-xs text-slate-500 hover:text-slate-300">Annuler</button>
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-slate-200 whitespace-pre-wrap pl-6">{note.content}</p>
                        )
                      )}

                      {/* Pied : date + actions */}
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-600">{formatDate(note.created_at)}</span>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => navigateTo(note.chapter_order, note.sentence_index)}
                            className="text-xs text-slate-500 hover:text-slate-200"
                            title="Aller au passage"
                          >
                            ↗
                          </button>
                          {!isHighlight && (
                            <button
                              onClick={() => startEdit(note)}
                              className="text-xs text-slate-500 hover:text-yellow-400"
                              title="Modifier"
                            >
                              ✏️
                            </button>
                          )}
                          <button
                            onClick={() => removeNote(note.id)}
                            className="text-xs text-slate-500 hover:text-red-400"
                            title="Supprimer"
                          >
                            🗑
                          </button>
                        </div>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </div>
      )}
    </>
  )
}
