import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { X, Send, Mic, Square, Loader2, Bot, User, Paperclip } from 'lucide-react'
import { useStore } from '../../store/useStore'
import { sendMessage, speechToText, getHistory } from '../../services/api'

function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="w-7 h-7 rounded-full bg-cyber-primary/10 flex items-center justify-center">
        <Bot size={14} className="text-cyber-primary" />
      </div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div key={i} className="typing-dot w-1.5 h-1.5 rounded-full bg-cyber-primary" />
        ))}
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: { role: string; content: string } }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 px-4 py-3 ${isUser ? '' : 'bg-white/[0.02]'}`}>
      <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-cyber-accent/10' : 'bg-cyber-primary/10'
      }`}>
        {isUser ? <User size={14} className="text-cyber-accent" /> : <Bot size={14} className="text-cyber-primary" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-cyber-muted/60 mb-1 font-medium tracking-wider uppercase">
          {isUser ? 'Tú' : 'CyberAI'}
        </div>
        <div className="prose prose-invert prose-sm max-w-none [&_pre]:bg-cyber-black/50 [&_pre]:rounded-lg [&_pre]:border [&_pre]:border-white/5 [&_code]:text-cyber-primary">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {msg.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const messages = useStore((s) => s.messages)
  const addMessage = useStore((s) => s.addMessage)
  const conversationId = useStore((s) => s.conversationId)
  const setConversationId = useStore((s) => s.setConversationId)
  const setChatOpen = useStore((s) => s.setChatOpen)
  const setStats = useStore((s) => s.setStats)
  const setConversations = useStore((s) => s.setConversations)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return
    const text = input.trim()
    setInput('')
    addMessage({ role: 'user', content: text })
    setIsProcessing(true)

    try {
      const res = await sendMessage(text, conversationId)
      addMessage({ role: 'assistant', content: res.reply })
      setConversationId(res.conversation_id)
      setStats({
        tokens: res.tokens_used,
        sources: res.sources,
        responseTime: res.processing_time,
      })
      const hist = await getHistory()
      setConversations(hist)
    } catch {
      addMessage({ role: 'assistant', content: '⚠️ Error al conectar con el servidor.' })
    }
    setIsProcessing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
      chunksRef.current = []
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setIsProcessing(true)
        try {
          const text = await speechToText(blob)
          setInput(text)
        } catch {}
        setIsProcessing(false)
        stream.getTracks().forEach((t) => t.stop())
      }
      recorder.start()
      mediaRecorderRef.current = recorder
      setIsRecording(true)
    } catch {}
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setIsRecording(false)
  }

  return (
    <motion.div
      initial={{ width: 0, opacity: 0 }}
      animate={{ width: 400, opacity: 1 }}
      exit={{ width: 0, opacity: 0 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="h-full bg-cyber-dark/80 backdrop-blur-2xl border-l border-white/5 flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Bot size={16} className="text-cyber-primary" />
          <span className="text-sm font-medium">Chat</span>
        </div>
        <button
          onClick={() => setChatOpen(false)}
          className="p-1.5 rounded-lg text-cyber-muted hover:text-cyber-text hover:bg-white/5 transition-all"
        >
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <Bot size={32} className="text-cyber-primary/20 mb-3" />
            <p className="text-sm text-cyber-muted/60">
              Inicia una conversación para ver los mensajes aquí
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {isProcessing && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-white/5">
        <div className="flex items-center gap-2 bg-black/30 rounded-xl border border-white/5 px-3 py-2 focus-within:border-cyber-primary/30 transition-colors">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-1.5 rounded-lg transition-colors ${
              isRecording
                ? 'text-cyber-danger bg-cyber-danger/10 animate-pulse'
                : 'text-cyber-muted hover:text-cyber-primary hover:bg-white/5'
            }`}
          >
            {isRecording ? <Square size={15} /> : <Mic size={15} />}
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe un mensaje..."
            className="flex-1 bg-transparent text-sm text-cyber-text outline-none placeholder:text-cyber-muted/30"
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || isProcessing}
            className="p-1.5 rounded-lg text-cyber-primary hover:bg-cyber-primary/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
          </button>
        </div>
      </div>
    </motion.div>
  )
}
