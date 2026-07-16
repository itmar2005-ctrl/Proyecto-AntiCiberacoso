import { useState } from 'react';
import { motion } from 'framer-motion';
import useStore from '../../store/useStore';
import {
  Home, MessageSquare, FileText, FolderGit2, Shield,
  BarChart3, Settings, ChevronLeft, Plus, Trash2, Upload, Globe,
  FileUp, X
} from 'lucide-react';
import { deleteConversation, getHistory } from '../../services/api';

const navItems = [
  { id: 'chat', icon: MessageSquare, label: 'Conversaciones' },
  { id: 'documents', icon: FileText, label: 'Documentos' },
  { id: 'projects', icon: FolderGit2, label: 'Proyectos' },
  { id: 'labs', icon: Shield, label: 'Laboratorios' },
  { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
  { id: 'settings', icon: Settings, label: 'Configuración' },
];

function ConversationItem({ conv, onSelect, onDelete }) {
  return (
    <div
      className="group flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cyber-surface/80 cursor-pointer transition-colors text-sm"
      onClick={() => onSelect(conv.id)}
    >
      <MessageSquare size={14} className="text-cyber-muted flex-shrink-0" />
      <span className="flex-1 truncate text-cyber-text/80">{conv.title}</span>
      <button
        onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
        className="opacity-0 group-hover:opacity-100 text-cyber-muted hover:text-cyber-danger transition-all"
      >
        <Trash2 size={12} />
      </button>
    </div>
  );
}

export default function Sidebar() {
  const [urlInput, setUrlInput] = useState('');
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const toggleSidebar = useStore((s) => s.toggleSidebar);
  const currentView = useStore((s) => s.currentView);
  const setCurrentView = useStore((s) => s.setCurrentView);
  const conversations = useStore((s) => s.conversations);
  const setConversations = useStore((s) => s.setConversations);
  const documents = useStore((s) => s.documents);
  const setDocuments = useStore((s) => s.setDocuments);
  const setMessages = useStore((s) => s.setMessages);
  const setConversationId = useStore((s) => s.setConversationId);
  const addMessage = useStore((s) => s.addMessage);

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setCurrentView('chat');
  };

  const handleSelectConversation = async (id) => {
    try {
      const { getConversation } = await import('../../services/api');
      const conv = await getConversation(id);
      setMessages(conv.messages || []);
      setConversationId(id);
      setCurrentView('chat');
    } catch {}
  };

  const handleDeleteConversation = async (id) => {
    await deleteConversation(id);
    const hist = await getHistory();
    setConversations(hist);
  };

  const handleUploadFiles = async (e) => {
    const { uploadDocument, getDocuments } = await import('../../services/api');
    for (const file of e.target.files) {
      await uploadDocument(file);
    }
    const docs = await getDocuments();
    setDocuments(docs);
  };

  const handleUploadUrl = async () => {
    if (!urlInput.trim()) return;
    const { uploadUrl, getDocuments } = await import('../../services/api');
    await uploadUrl(urlInput.trim());
    setUrlInput('');
    const docs = await getDocuments();
    setDocuments(docs);
  };

  return (
    <motion.aside
      initial={{ width: 0, opacity: 0 }}
      animate={{ width: 280, opacity: 1 }}
      exit={{ width: 0, opacity: 0 }}
      className="h-full bg-cyber-surface/60 backdrop-blur-xl border-r border-cyber-border/50 flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-cyber-border/50">
        <div className="flex items-center gap-2">
          <Shield size={20} className="text-cyber-primary" />
          <span className="font-mono text-sm text-cyber-primary font-bold glow-text">CYBERAI</span>
        </div>
        <button onClick={toggleSidebar} className="p-1 rounded-lg text-cyber-muted hover:text-cyber-primary hover:bg-cyber-primary/10">
          <ChevronLeft size={18} />
        </button>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-cyber-primary/10 border border-cyber-primary/30 text-cyber-primary hover:bg-cyber-primary/20 transition-colors text-sm font-mono"
        >
          <Plus size={16} />
          Nueva conversación
        </button>
      </div>

      {/* Nav */}
      <div className="px-3 mb-2">
        {navItems.slice(0, 3).map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentView(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors mb-0.5 ${
              currentView === item.id
                ? 'bg-cyber-primary/10 text-cyber-primary'
                : 'text-cyber-muted hover:text-cyber-text hover:bg-cyber-surface/80'
            }`}
          >
            <item.icon size={16} />
            {item.label}
          </button>
        ))}
      </div>

      {/* Content based on view */}
      <div className="flex-1 overflow-y-auto px-3">
        {currentView === 'chat' && (
          <div>
            <div className="text-xs text-cyber-muted uppercase tracking-wider px-3 mb-2 font-mono">
              Historial
            </div>
            {conversations.map((conv) => (
              <ConversationItem
                key={conv.id}
                conv={conv}
                onSelect={handleSelectConversation}
                onDelete={handleDeleteConversation}
              />
            ))}
            {conversations.length === 0 && (
              <p className="text-xs text-cyber-muted/50 px-3">Sin conversaciones aún</p>
            )}
          </div>
        )}

        {currentView === 'documents' && (
          <div>
            <div className="text-xs text-cyber-muted uppercase tracking-wider px-3 mb-2 font-mono">
              Base de conocimientos
            </div>

            {/* Upload buttons */}
            <div className="px-3 mb-3 space-y-2">
              <label className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-dashed border-cyber-border/50 text-cyber-muted hover:text-cyber-primary hover:border-cyber-primary/50 cursor-pointer transition-colors text-xs">
                <FileUp size={14} />
                Subir archivos
                <input type="file" className="hidden" multiple accept=".pdf,.docx,.txt,.csv,.xlsx,.pptx,.html" onChange={handleUploadFiles} />
              </label>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="URL de página web..."
                  className="flex-1 bg-cyber-bg border border-cyber-border/50 rounded-lg px-3 py-1.5 text-xs text-cyber-text outline-none focus:border-cyber-primary/50 placeholder:text-cyber-muted/30 font-mono"
                  onKeyDown={(e) => e.key === 'Enter' && handleUploadUrl()}
                />
                <button onClick={handleUploadUrl} className="p-1.5 rounded-lg bg-cyber-primary/10 text-cyber-primary hover:bg-cyber-primary/20">
                  <Globe size={14} />
                </button>
              </div>
            </div>

            {/* Document list */}
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center gap-2 px-3 py-2 text-xs text-cyber-text/70 hover:bg-cyber-surface/80 rounded-lg">
                <FileText size={12} className="text-cyber-primary/60" />
                <span className="flex-1 truncate">{doc.filename}</span>
              </div>
            ))}
            {documents.length === 0 && (
              <p className="text-xs text-cyber-muted/50 px-3">Sube documentos para crear tu base de conocimiento RAG</p>
            )}
          </div>
        )}

        {currentView === 'projects' && (
          <div className="text-center py-8">
            <FolderGit2 size={32} className="text-cyber-muted/30 mx-auto mb-2" />
            <p className="text-xs text-cyber-muted/50">Gestión de proyectos próximamente</p>
          </div>
        )}

        {currentView === 'labs' && (
          <div className="text-center py-8">
            <Shield size={32} className="text-cyber-muted/30 mx-auto mb-2" />
            <p className="text-xs text-cyber-muted/50">Laboratorios próximamente</p>
          </div>
        )}

        {currentView === 'dashboard' && (
          <div className="text-center py-8">
            <BarChart3 size={32} className="text-cyber-muted/30 mx-auto mb-2" />
            <p className="text-xs text-cyber-muted/50">Dashboard próximamente</p>
          </div>
        )}

        {currentView === 'settings' && (
          <div className="space-y-3 px-3">
            <div className="text-xs text-cyber-muted uppercase tracking-wider mb-2 font-mono">Configuración</div>
            <label className="flex items-center justify-between text-xs text-cyber-text/70">
              <span>Respuesta por voz</span>
              <input type="checkbox" defaultChecked className="accent-cyber-primary" onChange={() => useStore.getState().setVoiceEnabled(!useStore.getState().voiceEnabled)} />
            </label>
            <label className="flex items-center justify-between text-xs text-cyber-text/70">
              <span>Usar base de conocimiento</span>
              <input type="checkbox" defaultChecked className="accent-cyber-primary" />
            </label>
            <div className="pt-2 text-xs text-cyber-muted/40">
              <p>Modelo: Groq Llama 3 70B</p>
              <p>Base vectorial: ChromaDB</p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom */}
      <div className="p-3 border-t border-cyber-border/50">
        <div className="text-xs text-cyber-muted/40 text-center font-mono">
          CyberAI v1.0.0
        </div>
      </div>
    </motion.aside>
  );
}
