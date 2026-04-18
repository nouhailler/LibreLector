import { useEffect, useState } from 'react'
import { useStore } from './store/useStore'
import { useWebSocket } from './hooks/useWebSocket'
import { LibraryPanel } from './components/Library/LibraryPanel'
import { ReaderPanel } from './components/Reader/ReaderPanel'
import { SettingsModal } from './components/Settings/SettingsModal'
import { HelpModal } from './components/Help/HelpModal'

export default function App() {
  const loadLibrary = useStore(s => s.loadLibrary)
  const settingsOpen = useStore(s => s.settingsOpen)
  const [helpOpen, setHelpOpen] = useState(false)

  useWebSocket()

  // Retry until the Python backend is ready (timing: Tauri window loads before server)
  useEffect(() => {
    let cancelled = false
    const tryLoad = () => {
      loadLibrary().catch(() => {
        if (!cancelled) setTimeout(tryLoad, 1500)
      })
    }
    tryLoad()
    return () => { cancelled = true }
  }, [loadLibrary])

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-blue-400">LibreLector</span>
        </div>
        <HeaderActions onHelpOpen={() => setHelpOpen(true)} />
      </header>

      {/* Main layout */}
      <div className="flex flex-1 min-h-0">
        <LibraryPanel />
        <ReaderPanel />
      </div>

      {/* Modals */}
      {settingsOpen && <SettingsModal />}
      {helpOpen && <HelpModal onClose={() => setHelpOpen(false)} />}
    </div>
  )
}

function HeaderActions({ onHelpOpen }: { onHelpOpen: () => void }) {
  const setSettingsOpen = useStore(s => s.setSettingsOpen)
  const uploadBook = useStore(s => s.uploadBook)

  const handleFileOpen = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.epub,.pdf,.txt,.fb2'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) await uploadBook(file)
    }
    input.click()
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleFileOpen}
        className="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
      >
        + Ouvrir EPUB · TXT · PDF
      </button>
      <button
        onClick={() => setSettingsOpen(true)}
        className="px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-600 rounded-md transition-colors"
      >
        ⚙ Paramètres
      </button>
      <button
        onClick={onHelpOpen}
        className="px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-600 rounded-md transition-colors"
      >
        ? Aide
      </button>
    </div>
  )
}
