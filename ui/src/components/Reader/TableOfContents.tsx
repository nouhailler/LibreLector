import { useStore } from '../../store/useStore'

export function TableOfContents() {
  const { chapters, currentChapterOrder, goToChapter } = useStore(s => ({
    chapters: s.chapters,
    currentChapterOrder: s.currentChapterOrder,
    goToChapter: s.goToChapter,
  }))

  return (
    <div className="w-48 shrink-0 border-r border-slate-700 overflow-y-auto bg-slate-850">
      <p className="text-xs font-semibold text-slate-500 px-3 py-2 uppercase tracking-wider">Chapitres</p>
      {chapters.map(ch => (
        <button
          key={ch.order}
          onClick={() => goToChapter(ch.order)}
          className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-700 transition-colors ${ch.order === currentChapterOrder ? 'bg-blue-900/40 text-blue-300 border-l-2 border-blue-500' : 'text-slate-300'}`}
        >
          {ch.title}
        </button>
      ))}
    </div>
  )
}
