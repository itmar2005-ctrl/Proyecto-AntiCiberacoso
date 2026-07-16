import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  MessageSquare, FileText, Settings, ChevronLeft, Plus, Trash2,
  Home, BarChart3, Globe, FileUp, X, Shield
} from 'lucide-react'
import { useStore } from '../../store/useStore'
import { deleteConversation, getHistory, uploadDocument, uploadUrl, getDocuments } from '../../services/api'

export default function Sidebar() {
  const [activeTab, setActiveTab] = useState<'history' | 'documents' | 'settings'>('history')
  const [urlInput, setUrlInput] = useState('')

  const setSidebarOpen = useStore((s) => s.setSidebarOpen)
  const conversations = useStore((s) => s.conversations)
  const setConversations = useStore((s) => s.setConversations)
  const documents = useStore((s) => s.documents)
  const setDocuments = useStore((s) => s.setDocuments)
  const setMessages = useStore((s) => s.setMessages)
  const setConversationId = useStore((s) => s.setConversationId)

  const handleSelectConversation = async (id: string) => {
    try {
      const { getConversation } = await import('../../services/api')
      const conv = await getConversation(id)
      setMessages(conv.messages || [])
      setConversationId(id)
      setSidebarOpen(false)
    } catch {}
  }

  const handleDeleteConversation = async (id: string) => {
    await deleteConversation(id)
    const hist = await getHistory()
    setConversations(hist)
  }

  const handleUploadFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return
    for (const file of Array.from(files)) {
      await uploadDocument(file)
    }
    const docs = await getDocuments()
    setDocuments(docs)
  }

  const handleUploadUrl = async () => {
    if (!urlInput.trim()) return
    await uploadUrl(urlInput.trim())
    setUrlInput('')
    const docs = await getDocuments()
    setDocuments(docs)
  }

  const tabs = [
    { id: 'history', icon: MessageSquare, label: 'Historial' },
    { id: 'documents', icon: FileText, label: 'Documentos' },
    { id: 'settings', icon: Settings, label: 'Ajustes' },
  ] as const

  return (
    <motion.aside
      initial={{ width: 0, opacity: 0 }}
      animate={{ width: 320, opacity: 1 }}
      exit={{ width: 0, opacity: 0 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="h-full bg-cyber-dark/80 backdrop-blur-2xl border-r border-white/5 flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Shield size={18} className="text-cyber-primary" />
          <span className="text-sm font-display font-semibold text-gradient">CyberAI</span>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="p-1.5 rounded-lg text-cyber-muted hover:text-cyber-text hover:bg-white/5 transition-all"
        >
          <ChevronLeft size={16} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex px-3 gap-1 py-2 border-b border-white/5">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-cyber-primary/10 text-cyber-primary'
                : 'text-cyber-muted hover:text-cyber-text hover:bg-white/5'
            }`}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'history' && (
          <div className="p-3 space-y-1">
            <button
              onClick={async () => {
                setMessages([])
                setConversationId(null)
                setSidebarOpen(false)
              }}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-cyber-primary hover:bg-cyber-primary/5 border border-dashed border-cyber-primary/20 transition-all mb-3"
            >
              <Plus size={16} />
              Nueva conversación
            </button>
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className="group flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
                onClick={() => handleSelectConversation(conv.id)}
              >
                <MessageSquare size={14} className="text-cyber-muted flex-shrink-0" />
                <span className="flex-1 truncate text-sm text-cyber-text/70">{conv.title}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDeleteConversation(conv.id) }}
                  className="opacity-0 group-hover:opacity-100 text-cyber-muted hover:text-cyber-danger transition-all p-1"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
            {conversations.length === 0 && (
              <p className="text-xs text-cyber-muted/40 text-center py-8">Sin conversaciones aún</p>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="p-3">
            <label className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-dashed border-white/10 text-sm text-cyber-muted hover:text-cyber-primary hover:border-cyber-primary/30 cursor-pointer transition-all mb-3">
              <FileUp size={16} />
              Subir archivos
              <input type="file" className="hidden" multiple accept=".pdf,.docx,.txt,.csv,.xlsx,.pptx,.html,.md" onChange={handleUploadFiles} />
            </label>

            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="URL de documentación..."
                className="flex-1 bg-black/30 border border-white/5 rounded-lg px-3 py-1.5 text-xs text-cyber-text outline-none focus:border-cyber-primary/30 placeholder:text-cyber-muted/20"
                onKeyDown={(e) => e.key === 'Enter' && handleUploadUrl()}
              />
              <button
                onClick={handleUploadUrl}
                className="p-1.5 rounded-lg bg-cyber-primary/10 text-cyber-primary hover:bg-cyber-primary/20 transition-colors"
              >
                <Globe size={14} />
              </button>
            </div>

            <div className="space-y-1">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center gap-2 px-3 py-2 text-xs text-cyber-text/60 hover:bg-white/5 rounded-lg">
                  <FileText size={12} className="text-cyber-primary/40" />
                  <span className="flex-1 truncate">{doc.filename}</span>
                </div>
              ))}
              {documents.length === 0 && (
                <p className="text-xs text-cyber-muted/40 text-center py-8">Sube documentos para la base de conocimiento RAG</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="p-4 space-y-4">
            <div>
              <label className="text-xs text-cyber-muted uppercase tracking-wider font-medium">Modelo de IA</label>
              <select className="w-full mt-1 bg-black/30 border border-white/5 rounded-lg px-3 py-2 text-sm text-cyber-text outline-none focus:border-cyber-primary/30">
                <option value="llama3-8b-8192">Groq Llama 3.1 8B</option>
                <option value="llama3-70b-8192">Groq Llama 3.1 70B</option>
                <option value="mixtral-8x7b-32768">Groq Mixtral 8x7B</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-cyber-text/70">Respuesta por voz</span>
              <input type="checkbox" defaultChecked className="accent-cyber-primary" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-cyber-text/70">Usar base de conocimiento</span>
              <input type="checkbox" defaultChecked className="accent-cyber-primary" />
            </div>
            <div className="pt-3 border-t border-white/5 text-xs text-cyber-muted/40 space-y-1">
              <p>ChromaDB · RAG activo</p>
              <p>Whisper STT · Groq TTS</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-white/5 text-center">
        <span className="text-[10px] text-cyber-muted/30 tracking-wider">CYBERAI v2.0.0</span>
      </div>
    </motion.aside>
  )
}
