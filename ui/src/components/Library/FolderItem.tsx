import { useState } from 'react'
import { useStore } from '../../store/useStore'
import { BookItem } from './BookItem'
import type { Folder, Book } from '../../types'

interface Props {
  folder: Folder
  books: Book[]
}

export function FolderItem({ folder, books }: Props) {
  const [expanded, setExpanded] = useState(true)
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(folder.name)
  const { renameFolder, deleteFolder } = useStore(s => ({
    renameFolder: s.renameFolder,
    deleteFolder: s.deleteFolder,
  }))

  const handleRename = async () => {
    if (name.trim() && name !== folder.name) await renameFolder(folder.id, name.trim())
    setEditing(false)
  }

  return (
    <div>
      <div className="flex items-center gap-1 px-2 py-1 hover:bg-slate-700 group cursor-pointer">
        <span onClick={() => setExpanded(v => !v)} className="text-slate-400 w-3 text-center text-xs">
          {expanded ? '▼' : '▶'}
        </span>
        <span className="text-slate-400 text-sm">📁</span>
        {editing ? (
          <input
            autoFocus
            value={name}
            onChange={e => setName(e.target.value)}
            onBlur={handleRename}
            onKeyDown={e => { if (e.key === 'Enter') handleRename(); if (e.key === 'Escape') { setName(folder.name); setEditing(false) } }}
            className="flex-1 text-sm bg-slate-600 rounded px-1 outline-none"
          />
        ) : (
          <span
            className="flex-1 text-sm text-slate-200 truncate"
            onClick={() => setExpanded(v => !v)}
            onDoubleClick={() => setEditing(true)}
          >
            {folder.name}
          </span>
        )}
        <div className="hidden group-hover:flex gap-1">
          <button onClick={() => setEditing(true)} className="text-xs text-slate-400 hover:text-slate-200">✏</button>
          <button onClick={() => deleteFolder(folder.id)} className="text-xs text-red-400 hover:text-red-300">✕</button>
        </div>
      </div>
      {expanded && books.map(book => <BookItem key={book.id} book={book} indent />)}
    </div>
  )
}
