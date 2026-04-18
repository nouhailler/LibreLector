import { useState } from 'react'
import { useStore } from '../../store/useStore'
import { TableOfContents } from './TableOfContents'
import { ChapterText } from './ChapterText'
import { PlayerControls } from '../Player/PlayerControls'
import { ExportModal } from '../Export/ExportModal'
import { NotesPanel } from '../Notes/NotesPanel'

export function ReaderPanel() {
  const currentBook = useStore(s => s.currentBook)
  const isLoadingBook = useStore(s => s.isLoadingBook)
  const [exportOpen, setExportOpen] = useState(false)

  if (isLoadingBook) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500">
        Chargement du livre…
      </div>
    )
  }

  if (!currentBook) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-3">
        <span className="text-5xl">📖</span>
        <p className="text-sm">Sélectionnez un livre dans la bibliothèque</p>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      {/* Book title + export button */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-slate-700 bg-slate-800 shrink-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-base font-semibold truncate">{currentBook.title}</h1>
          <p className="text-xs text-slate-400 truncate">{currentBook.author}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <NotesPanel />
          <button
            onClick={() => setExportOpen(true)}
            className="px-2 py-1 text-xs text-slate-400 hover:text-slate-200 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
            title="Exporter en MP3"
          >
            🎵 MP3
          </button>
        </div>
      </div>

      {/* Content area */}
      <div className="flex flex-1 min-h-0 relative">
        <TableOfContents />
        <ChapterText />
      </div>

      {/* Player */}
      <PlayerControls />

      {/* Export modal */}
      {exportOpen && <ExportModal onClose={() => setExportOpen(false)} />}
    </div>
  )
}
