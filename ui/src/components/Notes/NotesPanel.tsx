import { useState } from 'react'
import { useStore } from '../../store/useStore'
import type { Note } from '../../types'

export function NotesPanel() {
  const { notes, notesOpen, setNotesOpen, removeNote, editNote, goToChapter, goToSentence } = useStore(s => ({
    notes: s.notes,
    notesOpen: s.notesOpen,
    setNotesOpen: s.setNotesOpen,
    removeNote: s.removeNote,
    editNote: s.editNote,
    goToChapter: s.goToChapter,
    goToSentence: s.goToSentence,
  }))

  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')

  function startEdit(note: Note) {
    setEditingId(note.id)
    setEditContent(note.content)
  }

  async function saveEdit(id: number) {
    if (editContent.trim()) await editNote(id, editContent.trim())
    setEditingId(null)
  }

  async function navigateTo(note: Note) {
    await goToChapter(note.chapter_order)
    await goToSentence(note.sentence_index)
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
      {/* Toggle button */}
      <button
        onClick={() => setNotesOpen(!notesOpen)}
        title={notesOpen ? 'Fermer les notes' : 'Voir les notes'}
        className={`shrink-0 px-2 py-1 text-xs rounded transition-colors ${
          notesOpen
            ? 'bg-yellow-500 text-slate-900 font-semibold'
            : 'text-slate-400 hover:text-slate-200 bg-slate-700 hover:bg-slate-600'
        }`}
      >
        📝 {notes.length > 0 ? `${notes.length} note${notes.length > 1 ? 's' : ''}` : 'Notes'}
      </button>

      {/* Side panel */}
      {notesOpen && (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-slate-900 border-l border-slate-700 flex flex-col z-30 shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700 shrink-0">
            <h2 className="text-sm font-semibold text-slate-100">
              📝 Notes ({notes.length})
            </h2>
            <button
              onClick={() => setNotesOpen(false)}
              className="text-slate-500 hover:text-slate-200 text-lg leading-none"
            >
              ✕
            </button>
          </div>

          {/* Notes list */}
          <div className="flex-1 overflow-y-auto">
            {notes.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-2 text-slate-500 text-sm px-4 text-center">
                <span className="text-3xl">📝</span>
                <p>Aucune note pour ce livre.</p>
                <p className="text-xs">Sélectionnez du texte dans le lecteur pour créer une note.</p>
              </div>
            ) : (
              <ul className="divide-y divide-slate-800">
                {notes.map(note => (
                  <li key={note.id} className="px-4 py-3 flex flex-col gap-2 hover:bg-slate-800/50 group">
                    {/* Highlighted text */}
                    {note.highlighted_text && (
                      <blockquote
                        className="border-l-2 border-yellow-400 pl-2 text-xs text-slate-400 italic line-clamp-2 cursor-pointer hover:text-slate-200 transition-colors"
                        onClick={() => navigateTo(note)}
                        title="Aller à ce passage"
                      >
                        « {note.highlighted_text} »
                      </blockquote>
                    )}

                    {/* Note content */}
                    {editingId === note.id ? (
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
                      <p className="text-sm text-slate-200 whitespace-pre-wrap">{note.content}</p>
                    )}

                    {/* Footer: date + actions */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-600">{formatDate(note.created_at)}</span>
                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => navigateTo(note)}
                          className="text-xs text-slate-500 hover:text-slate-200"
                          title="Aller au passage"
                        >
                          ↗
                        </button>
                        <button
                          onClick={() => startEdit(note)}
                          className="text-xs text-slate-500 hover:text-yellow-400"
                          title="Modifier"
                        >
                          ✏️
                        </button>
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
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </>
  )
}
