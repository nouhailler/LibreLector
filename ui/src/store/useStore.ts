import { create } from 'zustand'
import { api } from '../api/client'
import type { Book, Folder, ChapterMeta, ChapterContent, PlayerState, Settings, Note, Bookmark } from '../types'

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

  // Notes
  notes: Note[]
  bookmarks: Bookmark[]
  notesOpen: boolean

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

  // Notes actions
  loadNotes: (bookId: number) => Promise<void>
  addNote: (data: { chapter_order: number; sentence_index: number; char_start: number; char_end: number; highlighted_text: string; content: string }) => Promise<void>
  addHighlight: (data: { chapter_order: number; sentence_index: number; char_start: number; char_end: number; highlighted_text: string }) => Promise<void>
  editNote: (id: number, content: string) => Promise<void>
  removeNote: (id: number) => Promise<void>
  setNotesOpen: (open: boolean) => void

  // Bookmarks actions
  loadBookmarks: (bookId: number) => Promise<void>
  addBookmark: (label?: string) => Promise<void>
  removeBookmark: (id: number) => Promise<void>

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
  notes: [],
  bookmarks: [],
  notesOpen: false,
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
    await get().openBook(book.id)
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
        notes: [],
        bookmarks: [],
      })
      await get().loadChapter(initialChapter)
      await get().loadNotes(bookId)
      await get().loadBookmarks(bookId)
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

  loadNotes: async (bookId) => {
    const data = await api.getNotes(bookId)
    set({ notes: data.notes })
  },

  addNote: async (data) => {
    const book = get().currentBook
    if (!book) return
    await api.createNote({ book_id: book.id, type: 'note', ...data })
    await get().loadNotes(book.id)
  },

  addHighlight: async (data) => {
    const book = get().currentBook
    if (!book) return
    await api.createNote({ book_id: book.id, content: '', type: 'highlight', ...data })
    await get().loadNotes(book.id)
  },

  editNote: async (id, content) => {
    await api.updateNote(id, content)
    set(s => ({ notes: s.notes.map(n => n.id === id ? { ...n, content } : n) }))
  },

  removeNote: async (id) => {
    await api.deleteNote(id)
    set(s => ({ notes: s.notes.filter(n => n.id !== id) }))
  },

  setNotesOpen: (open) => set({ notesOpen: open }),

  loadBookmarks: async (bookId) => {
    const data = await api.getBookmarks(bookId)
    set({ bookmarks: data.bookmarks })
  },

  addBookmark: async (label = '') => {
    const { currentBook, currentChapterOrder, currentSentenceIndex } = get()
    if (!currentBook) return
    await api.createBookmark({
      book_id: currentBook.id,
      chapter_order: currentChapterOrder,
      sentence_index: currentSentenceIndex,
      label,
    })
    await get().loadBookmarks(currentBook.id)
  },

  removeBookmark: async (id) => {
    await api.deleteBookmark(id)
    set(s => ({ bookmarks: s.bookmarks.filter(b => b.id !== id) }))
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
