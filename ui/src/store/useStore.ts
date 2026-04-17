import { create } from 'zustand'
import { api } from '../api/client'
import type { Book, Folder, ChapterMeta, ChapterContent, PlayerState, Settings } from '../types'

interface LibreLectorState {
  // Library
  folders: Folder[]
  books: Book[]

  // Reader
  currentBook: Book | null
  chapters: ChapterMeta[]
  currentChapterOrder: number
  currentChapterContent: ChapterContent | null
  currentSentenceIndex: number

  // Player
  playerState: PlayerState
  speed: number
  volume: number

  // UI
  settingsOpen: boolean

  // Chargement
  isLoadingLibrary: boolean
  isLoadingBook: boolean
  isLoadingChapter: boolean

  // Actions library
  loadLibrary: () => Promise<void>
  uploadBook: (file: File) => Promise<void>
  deleteBook: (id: number) => Promise<void>
  addFolder: (name: string) => Promise<void>
  renameFolder: (id: number, name: string) => Promise<void>
  deleteFolder: (id: number) => Promise<void>
  moveBook: (bookId: number, folderId: number | null) => Promise<void>

  // Actions reader
  openBook: (bookId: number) => Promise<void>
  loadChapter: (order: number) => Promise<void>

  // Actions player
  play: () => Promise<void>
  pause: () => Promise<void>
  stop: () => Promise<void>
  nextChapter: () => Promise<void>
  prevChapter: () => Promise<void>
  goToChapter: (order: number) => Promise<void>
  goToSentence: (idx: number) => Promise<void>
  setSpeed: (speed: number) => Promise<void>
  setVolume: (volume: number) => Promise<void>

  // UI
  setSettingsOpen: (open: boolean) => void

  // WS handlers
  handleSentenceEvent: (index: number) => void
  handleStateEvent: (value: string) => void
  handleChapterEvent: (order: number) => void
}

export const useStore = create<LibreLectorState>((set, get) => ({
  folders: [],
  books: [],
  currentBook: null,
  chapters: [],
  currentChapterOrder: 0,
  currentChapterContent: null,
  currentSentenceIndex: 0,
  playerState: 'idle',
  speed: 1.0,
  volume: 1.0,
  settingsOpen: false,
  isLoadingLibrary: false,
  isLoadingBook: false,
  isLoadingChapter: false,

  loadLibrary: async () => {
    set({ isLoadingLibrary: true })
    try {
      const data = await api.getLibrary()
      set({ folders: data.folders, books: data.books })
    } finally {
      set({ isLoadingLibrary: false })
    }
  },

  uploadBook: async (file) => {
    const book = await api.uploadBook(file)
    await get().loadLibrary()
    return book
  },

  deleteBook: async (id) => {
    await api.deleteBook(id)
    await get().loadLibrary()
  },

  addFolder: async (name) => {
    await api.addFolder(name)
    await get().loadLibrary()
  },

  renameFolder: async (id, name) => {
    await api.renameFolder(id, name)
    await get().loadLibrary()
  },

  deleteFolder: async (id) => {
    await api.deleteFolder(id)
    await get().loadLibrary()
  },

  moveBook: async (bookId, folderId) => {
    await api.moveBook(bookId, folderId)
    await get().loadLibrary()
  },

  openBook: async (bookId) => {
    set({ isLoadingBook: true })
    try {
      const data = await api.openBook(bookId)
      const progress = data.progress
      const initialChapter = progress?.chapter_order ?? 0
      set({
        currentBook: data.book,
        chapters: data.chapters,
        currentChapterOrder: initialChapter,
        currentSentenceIndex: progress?.sentence_index ?? 0,
        playerState: 'idle',
        currentChapterContent: null,
      })
      await get().loadChapter(initialChapter)
    } finally {
      set({ isLoadingBook: false })
    }
  },

  loadChapter: async (order) => {
    set({ isLoadingChapter: true })
    try {
      const content = await api.getChapter(order)
      set({ currentChapterContent: content, currentChapterOrder: order })
    } finally {
      set({ isLoadingChapter: false })
    }
  },

  play: async () => {
    await api.play()
    set({ playerState: 'playing' })
  },

  pause: async () => {
    await api.pause()
    set({ playerState: 'paused' })
  },

  stop: async () => {
    await api.stop()
    set({ playerState: 'stopped' })
  },

  nextChapter: async () => {
    const res = await api.next()
    if (res.advanced) {
      const nextOrder = get().currentChapterOrder + 1
      set({ currentChapterOrder: nextOrder, currentSentenceIndex: 0 })
      await get().loadChapter(nextOrder)
    }
  },

  prevChapter: async () => {
    const res = await api.prev()
    if (res.advanced) {
      const prevOrder = get().currentChapterOrder - 1
      set({ currentChapterOrder: prevOrder, currentSentenceIndex: 0 })
      await get().loadChapter(prevOrder)
    }
  },

  goToChapter: async (order) => {
    await api.goToChapter(order)
    set({ currentChapterOrder: order, currentSentenceIndex: 0 })
    await get().loadChapter(order)
  },

  goToSentence: async (idx) => {
    await api.goToSentence(idx)
    set({ currentSentenceIndex: idx })
  },

  setSpeed: async (speed) => {
    await api.setSpeed(speed)
    set({ speed })
  },

  setVolume: async (volume) => {
    await api.setVolume(volume)
    set({ volume })
  },

  setSettingsOpen: (open) => set({ settingsOpen: open }),

  handleSentenceEvent: (index) => set({ currentSentenceIndex: index }),

  handleStateEvent: (value) => {
    const state = value as PlayerState
    set({ playerState: state })
  },

  handleChapterEvent: (order) => {
    const { currentChapterOrder, loadChapter } = get()
    if (order !== currentChapterOrder) {
      set({ currentChapterOrder: order, currentSentenceIndex: 0 })
      loadChapter(order)
    }
  },
}))
