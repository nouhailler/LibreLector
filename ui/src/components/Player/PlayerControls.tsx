import { useStore } from '../../store/useStore'

export function PlayerControls() {
  const { playerState, speed, volume, currentBook, play, pause, stop, nextChapter, prevChapter, setSpeed, setVolume } = useStore(s => ({
    playerState: s.playerState,
    speed: s.speed,
    volume: s.volume,
    currentBook: s.currentBook,
    play: s.play,
    pause: s.pause,
    stop: s.stop,
    nextChapter: s.nextChapter,
    prevChapter: s.prevChapter,
    setSpeed: s.setSpeed,
    setVolume: s.setVolume,
  }))

  if (!currentBook) return null

  const isPlaying = playerState === 'playing'

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-slate-800 border-t border-slate-700 shrink-0">
      {/* Navigation */}
      <button onClick={prevChapter} className="text-slate-400 hover:text-slate-200 text-lg" title="Chapitre précédent">⏮</button>

      {/* Play / Pause */}
      <button
        onClick={isPlaying ? pause : play}
        className="w-10 h-10 flex items-center justify-center bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg transition-colors"
      >
        {isPlaying ? '⏸' : '▶'}
      </button>

      {/* Stop */}
      <button onClick={stop} className="text-slate-400 hover:text-slate-200 text-lg" title="Arrêter">⏹</button>

      <button onClick={nextChapter} className="text-slate-400 hover:text-slate-200 text-lg" title="Chapitre suivant">⏭</button>

      {/* State indicator */}
      <span className="text-xs text-slate-500 w-14">
        {playerState === 'playing' ? '▶ Lecture' : playerState === 'paused' ? '⏸ Pause' : playerState === 'stopped' ? '⏹ Arrêt' : ''}
      </span>

      <div className="flex-1" />

      {/* Speed */}
      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-400">Vitesse</label>
        <input
          type="range"
          min={0.5}
          max={2.0}
          step={0.1}
          value={speed}
          onChange={e => setSpeed(parseFloat(e.target.value))}
          className="w-24 accent-blue-500"
        />
        <span className="text-xs text-slate-300 w-8">{speed.toFixed(1)}×</span>
      </div>

      {/* Volume */}
      <div className="flex items-center gap-2">
        <span className="text-slate-400 text-sm">🔊</span>
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={volume}
          onChange={e => setVolume(parseFloat(e.target.value))}
          className="w-24 accent-blue-500"
        />
      </div>
    </div>
  )
}
