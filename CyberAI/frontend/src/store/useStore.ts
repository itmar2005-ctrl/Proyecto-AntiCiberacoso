import { create } from 'zustand'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Conversation {
  id: string
  title: string
  updated_at: string
  message_count: number
}

interface Document {
  id: string
  filename: string
}

interface Stats {
  model: string
  tokens: number
  sources: string[]
  responseTime: number
}

interface AppState {
  // Call state
  isCallActive: boolean
  isCallStarting: boolean
  isSpeaking: boolean
  isListening: boolean
  isMuted: boolean

  // Messages
  messages: Message[]
  conversationId: string | null

  // UI
  chatOpen: boolean
  sidebarOpen: boolean
  showAdvanced: boolean

  // Data
  conversations: Conversation[]
  documents: Document[]
  stats: Stats

  // Voice
  voiceEnabled: boolean

  // Actions
  setCallActive: (v: boolean) => void
  setCallStarting: (v: boolean) => void
  setSpeaking: (v: boolean) => void
  setListening: (v: boolean) => void
  setMuted: (v: boolean) => void
  setMessages: (m: Message[]) => void
  addMessage: (m: Message) => void
  setConversationId: (id: string | null) => void
  setChatOpen: (v: boolean) => void
  setSidebarOpen: (v: boolean) => void
  setShowAdvanced: (v: boolean) => void
  setConversations: (c: Conversation[]) => void
  setDocuments: (d: Document[]) => void
  setStats: (s: Partial<Stats>) => void
  setVoiceEnabled: (v: boolean) => void
  toggleMute: () => void
  resetCall: () => void
}

export const useStore = create<AppState>((set, get) => ({
  isCallActive: false,
  isCallStarting: false,
  isSpeaking: false,
  isListening: false,
  isMuted: false,

  messages: [],
  conversationId: null,

  chatOpen: false,
  sidebarOpen: false,
  showAdvanced: false,

  conversations: [],
  documents: [],
  stats: {
    model: 'Groq Llama 3.1 8B',
    tokens: 0,
    sources: [],
    responseTime: 0,
  },

  voiceEnabled: true,

  setCallActive: (v) => set({ isCallActive: v, isCallStarting: false }),
  setCallStarting: (v) => set({ isCallStarting: v }),
  setSpeaking: (v) => set({ isSpeaking: v }),
  setListening: (v) => set({ isListening: v }),
  setMuted: (v) => set({ isMuted: v }),
  setMessages: (m) => set({ messages: m }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  setConversationId: (id) => set({ conversationId: id }),
  setChatOpen: (v) => set({ chatOpen: v }),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
  setShowAdvanced: (v) => set({ showAdvanced: v }),
  setConversations: (c) => set({ conversations: c }),
  setDocuments: (d) => set({ documents: d }),
  setStats: (s) => set((state) => ({ stats: { ...state.stats, ...s } })),
  setVoiceEnabled: (v) => set({ voiceEnabled: v }),
  toggleMute: () => set((s) => ({ isMuted: !s.isMuted })),
  resetCall: () => set({
    isCallActive: false,
    isCallStarting: false,
    isSpeaking: false,
    isListening: false,
    isMuted: false,
  }),
}))
