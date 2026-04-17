import { useEffect, useRef } from 'react'
import { useStore } from '../store/useStore'

const WS_URL = 'ws://localhost:7531/ws'

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const handleSentenceEvent = useStore(s => s.handleSentenceEvent)
  const handleStateEvent = useStore(s => s.handleStateEvent)
  const handleChapterEvent = useStore(s => s.handleChapterEvent)

  useEffect(() => {
    let reconnectTimeout: number

    function connect() {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'sentence') handleSentenceEvent(msg.index)
          else if (msg.type === 'state') handleStateEvent(msg.value)
          else if (msg.type === 'chapter') handleChapterEvent(msg.order)
        } catch {
          // ignore parse errors
        }
      }

      ws.onclose = () => {
        reconnectTimeout = window.setTimeout(connect, 2000)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      clearTimeout(reconnectTimeout)
      wsRef.current?.close()
    }
  }, [handleSentenceEvent, handleStateEvent, handleChapterEvent])
}
