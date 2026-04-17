import { useState } from 'react'
import { useStore } from '../../store/useStore'
import { FolderItem } from './FolderItem'
import { BookItem } from './BookItem'

export function LibraryPanel() {
  const { folders, books, addFolder, isLoadingLibrary } = useStore(s => ({
    folders: s.folders,
    books: s.books,
    addFolder: s.addFolder,
    isLoadingLibrary: s.isLoadingLibrary,
  }))
  const [newFolderName, setNewFolderName] = useState('')
  const [showInput, setShowInput] = useState(false)

  const booksWithoutFolder = books.filter(b => b.folder_id === null)

  const handleAddFolder = async () => {
    if (!newFolderName.trim()) return
    await addFolder(newFolderName.trim())
    setNewFolderName('')
    setShowInput(false)
  }

  return (
    <aside className="w-72 shrink-0 flex flex-col bg-slate-800 border-r border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-700">
        <span className="text-sm font-semibold text-slate-300">Bibliothèque</span>
        <button
          onClick={() => setShowInput(v => !v)}
          className="text-slate-400 hover:text-slate-200 text-xs"
          title="Nouveau dossier"
        >
          📁+
        </button>
      </div>

      {/* New folder input */}
      {showInput && (
        <div className="px-3 py-2 border-b border-slate-700 flex gap-1">
          <input
            autoFocus
            value={newFolderName}
            onChange={e => setNewFolderName(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleAddFolder(); if (e.key === 'Escape') setShowInput(false) }}
            placeholder="Nom du dossier"
            className="flex-1 text-sm bg-slate-700 rounded px-2 py-1 outline-none"
          />
          <button onClick={handleAddFolder} className="text-xs text-blue-400 hover:text-blue-300">OK</button>
        </div>
      )}

      {/* Scrollable list */}
      <div className="flex-1 overflow-y-auto py-1">
        {isLoadingLibrary ? (
          <p className="text-xs text-slate-500 px-3 py-2">Chargement…</p>
        ) : (
          <>
            {folders.map(folder => (
              <FolderItem
                key={folder.id}
                folder={folder}
                books={books.filter(b => b.folder_id === folder.id)}
              />
            ))}
            {booksWithoutFolder.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 px-3 pt-2 pb-1">Sans dossier</p>
                {booksWithoutFolder.map(book => (
                  <BookItem key={book.id} book={book} />
                ))}
              </div>
            )}
            {folders.length === 0 && booksWithoutFolder.length === 0 && (
              <p className="text-xs text-slate-500 px-3 py-4 text-center">
                Aucun livre.<br />Cliquez sur « + Ouvrir EPUB »
              </p>
            )}
          </>
        )}
      </div>
    </aside>
  )
}
