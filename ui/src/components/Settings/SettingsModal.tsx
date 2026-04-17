import { useEffect, useState } from 'react'
import { useStore } from '../../store/useStore'
import { api } from '../../api/client'
import type { Settings } from '../../types'

export function SettingsModal() {
  const setSettingsOpen = useStore(s => s.setSettingsOpen)
  const [settings, setSettings] = useState<Settings | null>(null)
  const [voices, setVoices] = useState<{ name: string; path: string }[]>([])
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    Promise.all([api.getSettings(), api.getVoices()]).then(([s, v]) => {
      setSettings(s)
      setVoices(v.voices)
    })
  }, [])

  const handleSave = async () => {
    if (!settings) return
    setSaving(true)
    try {
      await api.saveSettings(settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setSettingsOpen(false)}>
      <div
        className="bg-slate-800 rounded-lg shadow-xl w-full max-w-md p-6 flex flex-col gap-4"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Paramètres TTS</h2>
          <button onClick={() => setSettingsOpen(false)} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>

        {!settings ? (
          <p className="text-slate-400 text-sm">Chargement…</p>
        ) : (
          <>
            {/* Engine */}
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-300">Moteur TTS</label>
              <select
                value={settings.tts_engine}
                onChange={e => setSettings({ ...settings, tts_engine: e.target.value })}
                className="bg-slate-700 rounded px-2 py-1.5 text-sm outline-none"
              >
                <option value="piper">Piper (neural, offline)</option>
                <option value="speech_dispatcher">Speech Dispatcher (système)</option>
              </select>
            </div>

            {/* Piper model */}
            {settings.tts_engine === 'piper' && (
              <div className="flex flex-col gap-1">
                <label className="text-sm text-slate-300">Modèle Piper</label>
                {voices.length > 0 ? (
                  <select
                    value={settings.piper_model}
                    onChange={e => setSettings({ ...settings, piper_model: e.target.value })}
                    className="bg-slate-700 rounded px-2 py-1.5 text-sm outline-none"
                  >
                    <option value="">— Choisir une voix —</option>
                    {voices.map(v => (
                      <option key={v.path} value={v.path}>{v.name}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    value={settings.piper_model}
                    onChange={e => setSettings({ ...settings, piper_model: e.target.value })}
                    placeholder="/chemin/vers/model.onnx"
                    className="bg-slate-700 rounded px-2 py-1.5 text-sm outline-none"
                  />
                )}
              </div>
            )}

            {/* Language */}
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-300">Langue</label>
              <input
                value={settings.language}
                onChange={e => setSettings({ ...settings, language: e.target.value })}
                placeholder="fr"
                className="bg-slate-700 rounded px-2 py-1.5 text-sm outline-none w-20"
              />
            </div>

            {/* Save button */}
            <button
              onClick={handleSave}
              disabled={saving}
              className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium disabled:opacity-50 transition-colors"
            >
              {saved ? '✓ Enregistré' : saving ? 'Enregistrement…' : 'Enregistrer'}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
