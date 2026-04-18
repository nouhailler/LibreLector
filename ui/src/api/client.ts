import type { Folder, Book, ChapterMeta, ChapterContent, Progress, PlayerState, Settings, Note } from '../types'

// En dev Vite proxie /api → localhost:7531 ; en prod l'URL absolue est nécessaire
const BASE = (typeof import.meta !== 'undefined' && (import.meta as any).env?.DEV) ? '' : 'http://localhost:7531'

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${method} ${path} → ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  // Library
  getLibrary: () => request<{ folders: Folder[]; books: Book[] }>('GET', '/api/library'),
  uploadBook: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE}/api/library/books/upload`, { method: 'POST', body: form }).then(r => r.json())
  },
  deleteBook: (id: number) => request<void>('DELETE', `/api/library/books/${id}`),
  addFolder: (name: string) => request<Folder>('POST', '/api/library/folders', { name }),
  renameFolder: (id: number, name: string) => request<void>('PUT', `/api/library/folders/${id}`, { name }),
  deleteFolder: (id: number) => request<void>('DELETE', `/api/library/folders/${id}`),
  moveBook: (bookId: number, folderId: number | null) =>
    request<void>('PUT', `/api/library/books/${bookId}/folder`, { folder_id: folderId }),

  // Reader
  openBook: (bookId: number) =>
    request<{ book: Book; chapters: ChapterMeta[]; progress: Progress | null }>('POST', `/api/reader/open/${bookId}`),
  getChapter: (order: number) => request<ChapterContent>('GET', `/api/reader/chapter/${order}`),
  getState: () => request<{ book_id: number | null; chapter_order: number; sentence_index: number; player_state: PlayerState }>('GET', '/api/reader/state'),

  // Player
  play: () => request<void>('POST', '/api/player/play'),
  pause: () => request<void>('POST', '/api/player/pause'),
  stop: () => request<void>('POST', '/api/player/stop'),
  next: () => request<{ advanced: boolean }>('POST', '/api/player/next'),
  prev: () => request<{ advanced: boolean }>('POST', '/api/player/prev'),
  goToChapter: (order: number) => request<void>('POST', `/api/player/chapter/${order}`),
  goToSentence: (idx: number) => request<void>('POST', `/api/player/sentence/${idx}`),
  setSpeed: (speed: number) => request<void>('PUT', '/api/player/speed', { speed }),
  setVolume: (volume: number) => request<void>('PUT', '/api/player/volume', { volume }),

  // Settings
  getSettings: () => request<Settings>('GET', '/api/settings'),
  saveSettings: (s: Settings) => request<Settings>('PUT', '/api/settings', s),
  getVoices: () => request<{ voices: { name: string; path: string }[] }>('GET', '/api/settings/voices'),

  // Notes
  getNotes: (bookId: number) => request<{ notes: Note[] }>('GET', `/api/notes/${bookId}`),
  createNote: (data: {
    book_id: number; chapter_order: number; sentence_index: number
    char_start: number; char_end: number; highlighted_text: string; content: string
  }) => request<Note>('POST', '/api/notes', data),
  updateNote: (id: number, content: string) => request<void>('PUT', `/api/notes/${id}`, { content }),
  deleteNote: (id: number) => request<void>('DELETE', `/api/notes/${id}`),

  // Health
  health: () => request<{ status: string }>('GET', '/api/health'),
}

