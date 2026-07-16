import { create } from 'zustand';

const useStore = create((set, get) => ({
  messages: [],
  conversationId: null,
  conversations: [],
  documents: [],
  isRecording: false,
  isProcessing: false,
  voiceEnabled: true,
  sidebarOpen: true,
  currentView: 'chat',
  stats: {
    cpu: '12%',
    ram: '3.2/16 GB',
    model: 'Groq Llama 3 70B',
    tokens: 0,
    sources: [],
    responseTime: 0,
  },

  setMessages: (messages) => set({ messages }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setConversationId: (id) => set({ conversationId: id }),
  setConversations: (convs) => set({ conversations: convs }),
  setDocuments: (docs) => set({ documents: docs }),
  setIsRecording: (v) => set({ isRecording: v }),
  setIsProcessing: (v) => set({ isProcessing: v }),
  setVoiceEnabled: (v) => set({ voiceEnabled: v }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setCurrentView: (v) => set({ currentView: v }),
  setStats: (stats) => set((s) => ({ stats: { ...s.stats, ...stats } })),
}));

export default useStore;
