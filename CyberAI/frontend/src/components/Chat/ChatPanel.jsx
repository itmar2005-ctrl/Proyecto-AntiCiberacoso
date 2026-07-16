import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import useStore from '../../store/useStore';
import { sendMessage, stt as sttApi, tts } from '../../services/api';
import {
  Mic, MicOff, Send, Paperclip, Globe, StopCircle, Image,
  Square, Loader2, Bot, User, MoreVertical, Trash2
} from 'lucide-react';

function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 px-4 py-3 message-enter">
      <div className="w-8 h-8 rounded-full bg-cyber-primary/20 flex items-center justify-center">
        <Bot size={16} className="text-cyber-primary" />
      </div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div key={i} className="typing-dot w-2 h-2 rounded-full bg-cyber-primary" />
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-3 px-4 py-3 message-enter ${isUser ? '' : 'bg-cyber-surface/30'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-cyber-accent/20' : 'bg-cyber-primary/20'}`}>
        {isUser ? <User size={16} className="text-cyber-accent" /> : <Bot size={16} className="text-cyber-primary" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs text-cyber-muted mb-1 font-mono">
          {isUser ? 'TÚ' : 'CYBERAI'}
        </div>
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {msg.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default function ChatPanel() {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const messagesEndRef = useRef(null);

  const messages = useStore((s) => s.messages);
  const addMessage = useStore((s) => s.addMessage);
  const conversationId = useStore((s) => s.conversationId);
  const setConversationId = useStore((s) => s.setConversationId);
  const setStats = useStore((s) => s.setStats);
  const voiceEnabled = useStore((s) => s.voiceEnabled);
  const setConversations = useStore((s) => s.setConversations);
  const getConversations = useStore((s) => s.getConversations);
  const conversations = useStore((s) => s.conversations);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  }, []);

  useEffect(() => scrollToBottom(), [messages]);

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;
    const text = input.trim();
    setInput('');
    addMessage({ role: 'user', content: text });
    setIsProcessing(true);

    try {
      const res = await sendMessage(text, conversationId);
      addMessage({ role: 'assistant', content: res.reply });
      setConversationId(res.conversation_id);
      setStats({
        tokens: res.tokens_used,
        sources: res.sources,
        responseTime: res.processing_time,
      });

      if (voiceEnabled) {
        try {
          const audioRes = await tts(res.reply);
          if (audioRes.audio) {
            const audio = new Audio(`data:audio/wav;base64,${audioRes.audio}`);
            audio.play();
          }
        } catch {}
      }

      const hist = await (await import('../../services/api')).getHistory();
      useStore.getState().setConversations(hist);
    } catch (err) {
      addMessage({ role: 'assistant', content: '⚠️ Error al conectar con el servidor. Verifica que el backend esté corriendo.' });
    }
    setIsProcessing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setIsProcessing(true);
        try {
          const text = await sttApi(blob);
          setInput(text);
        } catch {
          setInput('');
        }
        setIsProcessing(false);
        stream.getTracks().forEach((t) => t.stop());
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch {
      console.error('Mic access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col relative" style={{ marginTop: '200px' }}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-2">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center px-8">
            <Bot size={48} className="text-cyber-primary/40 mb-4" />
            <h2 className="text-xl text-cyber-primary font-mono glow-text mb-2">CyberAI Assistant</h2>
            <p className="text-cyber-muted text-sm max-w-md">
              Asistente de ciberseguridad con IA. Haz preguntas sobre hacking ético, redes, Linux, Wazuh, Suricata, pfSense y más.
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
      <div className="border-t border-cyber-border/50 p-3 bg-cyber-bg/80 backdrop-blur">
        <div className="flex items-center gap-2 bg-cyber-surface border border-cyber-border/50 rounded-xl px-4 py-2 focus-within:border-cyber-primary/50 transition-colors">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-1.5 rounded-lg transition-colors ${isRecording ? 'text-cyber-danger bg-cyber-danger/10 animate-pulse' : 'text-cyber-muted hover:text-cyber-primary hover:bg-cyber-primary/10'}`}
            title={isRecording ? 'Detener grabación' : 'Grabar voz'}
          >
            {isRecording ? <Square size={18} /> : <Mic size={18} />}
          </button>

          <label className="p-1.5 rounded-lg text-cyber-muted hover:text-cyber-primary hover:bg-cyber-primary/10 cursor-pointer" title="Subir documento">
            <Paperclip size={18} />
            <input type="file" className="hidden" accept=".pdf,.docx,.txt,.csv,.xlsx,.pptx,.html" multiple
              onChange={async (e) => {
                for (const file of e.target.files) {
                  const { uploadDocument } = await import('../../services/api');
                  await uploadDocument(file);
                }
                const { getDocuments } = await import('../../services/api');
                const docs = await getDocuments();
                useStore.getState().setDocuments(docs);
              }}
            />
          </label>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu mensaje..."
            className="flex-1 bg-transparent text-cyber-text outline-none resize-none text-sm py-1 max-h-32 placeholder:text-cyber-muted/50 font-mono"
            rows={1}
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || isProcessing}
            className="p-1.5 rounded-lg bg-cyber-primary/20 text-cyber-primary hover:bg-cyber-primary/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>

        <div className="flex items-center justify-between mt-2 px-1">
          <div className="flex items-center gap-3 text-xs text-cyber-muted">
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={voiceEnabled}
                onChange={() => useStore.getState().setVoiceEnabled(!voiceEnabled)}
                className="accent-cyber-primary"
              />
              Voz
            </label>
            <span>|</span>
            <span className="text-cyber-muted/60">Groq Llama 3</span>
          </div>
          <div className="text-xs text-cyber-muted/40">
            {messages.length} mensajes
          </div>
        </div>
      </div>
    </div>
  );
}
