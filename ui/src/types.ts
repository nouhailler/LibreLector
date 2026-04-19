export interface Folder {
  id: number
  name: string
  created_at: string
}

export interface Book {
  id: number
  file_path: string
  title: string
  author: string
  language: string
  chapter_count: number
  added_at: string
  folder_id: number | null
  cover_path: string | null
}

export interface ChapterMeta {
  order: number
  title: string
  sentence_count: number
}

export interface Sentence {
  text: string
  index: number
  char_start: number
  char_end: number
}

export interface ChapterContent {
  order: number
  title: string
  sentences: Sentence[]
}

export interface Settings {
  tts_engine: string
  piper_model: string
  language: string
}

export interface Progress {
  chapter_order: number
  sentence_index: number
}

export type PlayerState = 'idle' | 'playing' | 'paused' | 'stopped'

export interface Note {
  id: number
  book_id: number
  chapter_order: number
  sentence_index: number
  char_start: number
  char_end: number
  highlighted_text: string
  content: string
  type: 'note' | 'highlight'
  created_at: string
  updated_at: string
}

export interface Bookmark {
  id: number
  book_id: number
  chapter_order: number
  sentence_index: number
  label: string
  created_at: string
}
