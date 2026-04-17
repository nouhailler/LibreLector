import { useStore } from '../../store/useStore'
import type { Book } from '../../types'

interface Props {
  book: Book
  indent?: boolean
}

export function BookItem({ book, indent }: Props) {
  const { openBook, deleteBook, currentBook } = useStore(s => ({
    openBook: s.openBook,
    deleteBook: s.deleteBook,
    currentBook: s.currentBook,
  }))
  const isActive = currentBook?.id === book.id

  return (
    <div
      className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer group hover:bg-slate-700 ${indent ? 'pl-8' : 'pl-4'} ${isActive ? 'bg-blue-900/40 border-l-2 border-blue-500' : ''}`}
      onClick={() => openBook(book.id)}
    >
      <span className="text-sm text-slate-400">📗</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-200 truncate">{book.title}</p>
        <p className="text-xs text-slate-500 truncate">{book.author}</p>
      </div>
      <button
        onClick={e => { e.stopPropagation(); deleteBook(book.id) }}
        className="hidden group-hover:block text-xs text-red-400 hover:text-red-300 shrink-0"
      >
        ✕
      </button>
    </div>
  )
}
