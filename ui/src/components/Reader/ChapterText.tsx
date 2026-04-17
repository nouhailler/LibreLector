import { useEffect, useRef } from 'react'
import { useStore } from '../../store/useStore'

export function ChapterText() {
  const { currentChapterContent, currentSentenceIndex, playerState, goToSentence, isLoadingChapter } = useStore(s => ({
    currentChapterContent: s.currentChapterContent,
    currentSentenceIndex: s.currentSentenceIndex,
    playerState: s.playerState,
    goToSentence: s.goToSentence,
    isLoadingChapter: s.isLoadingChapter,
  }))

  const activeRef = useRef<HTMLSpanElement | null>(null)

  // Auto-scroll to active sentence
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [currentSentenceIndex])

  if (isLoadingChapter) {
    return <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">Chargement…</div>
  }

  if (!currentChapterContent) {
    return <div className="flex-1" />
  }

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6">
      <h2 className="text-lg font-semibold text-slate-200 mb-4">{currentChapterContent.title}</h2>
      <div className="text-slate-300 leading-relaxed text-base">
        {currentChapterContent.sentences.map(s => {
          const isActive = s.index === currentSentenceIndex && (playerState === 'playing' || playerState === 'paused')
          return (
            <span
              key={s.index}
              ref={isActive ? activeRef : null}
              onClick={() => goToSentence(s.index)}
              className={`cursor-pointer rounded px-0.5 transition-colors ${isActive ? 'sentence-active' : 'hover:bg-slate-700/50'}`}
            >
              {s.text}{' '}
            </span>
          )
        })}
      </div>
    </div>
  )
}
