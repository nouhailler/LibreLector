import { useState } from 'react'
import { useStore } from '../../store/useStore'

const BASE = 'http://localhost:7531'

interface ExportEvent {
  type: 'progress' | 'done' | 'error'
  current?: number
  total?: number
  title?: string
  path?: string
  message?: string
}

interface Props {
  onClose: () => void
}

export function ExportModal({ onClose }: Props) {
  const { currentBook, chapters, currentChapterOrder } = useStore(s => ({
    currentBook: s.currentBook,
    chapters: s.chapters,
    currentChapterOrder: s.currentChapterOrder,
  }))

  const [exporting, setExporting] = useState(false)
  const [events, setEvents] = useState<ExportEvent[]>([])
  const [done, setDone] = useState(false)

  if (!currentBook) return null

  const exportChapter = async (order: number) => {
    setExporting(true)
    setDone(false)
    setEvents([])

    try {
      const res = await fetch(`${BASE}/api/export/chapter/${order}`, { method: 'POST' })
      if (!res.ok) {
        const err = await res.json()
        setEvents([{ type: 'error', message: err.detail ?? 'Erreur inconnue' }])
        setExporting(false)
        return
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done: streamDone, value } = await reader.read()
        if (streamDone) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const evt: ExportEvent = JSON.parse(line.slice(6))
              setEvents(prev => [...prev, evt])
              if (evt.type === 'done' || evt.type === 'error') setDone(true)
            } catch {
              // ignore malformed line
            }
          }
        }
      }
    } catch (e) {
      setEvents([{ type: 'error', message: String(e) }])
    } finally {
      setExporting(false)
      setDone(true)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-slate-800 rounded-lg shadow-xl w-full max-w-md p-6 flex flex-col gap-4"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Export MP3</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>

        <p className="text-sm text-slate-400">
          Chapitre courant : <span className="text-slate-200 font-medium">
            {chapters.find(c => c.order === currentChapterOrder)?.title ?? `Chapitre ${currentChapterOrder}`}
          </span>
        </p>

        {/* Export current chapter */}
        <button
          onClick={() => exportChapter(currentChapterOrder)}
          disabled={exporting}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded text-sm font-medium transition-colors"
        >
          {exporting ? 'Export en cours…' : '🎵 Exporter ce chapitre en MP3'}
        </button>

        {/* Progress log */}
        {events.length > 0 && (
          <div className="bg-slate-900 rounded p-3 flex flex-col gap-1 max-h-40 overflow-y-auto">
            {events.map((evt, i) => (
              <p key={i} className={`text-xs ${evt.type === 'error' ? 'text-red-400' : evt.type === 'done' ? 'text-green-400' : 'text-slate-300'}`}>
                {evt.type === 'progress' && `✓ ${evt.title}`}
                {evt.type === 'done' && `✅ Exporté : ${evt.path}`}
                {evt.type === 'error' && `❌ Erreur : ${evt.message}`}
              </p>
            ))}
          </div>
        )}

        {done && (
          <button onClick={onClose} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm transition-colors">
            Fermer
          </button>
        )}
      </div>
    </div>
  )
}
