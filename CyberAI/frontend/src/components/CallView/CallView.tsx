import { motion, AnimatePresence } from 'framer-motion'
import { Mic, Phone, Loader2 } from 'lucide-react'
import { useStore } from '../../store/useStore'
import { startCall, sendMessage } from '../../services/api'

export default function CallView() {
  const isCallActive = useStore((s) => s.isCallActive)
  const isCallStarting = useStore((s) => s.isCallStarting)
  const setCallActive = useStore((s) => s.setCallActive)
  const setCallStarting = useStore((s) => s.setCallStarting)
  const setSpeaking = useStore((s) => s.setSpeaking)
  const addMessage = useStore((s) => s.addMessage)
  const setConversationId = useStore((s) => s.setConversationId)
  const messages = useStore((s) => s.messages)
  const conversationId = useStore((s) => s.conversationId)
  const setStats = useStore((s) => s.setStats)

  const handleStartCall = async () => {
    setCallStarting(true)
    try {
      const res = await startCall()
      setCallActive(true)
      setConversationId(res.conversation_id)
      addMessage({ role: 'assistant', content: res.reply })
      setStats({
        tokens: res.tokens_used,
        sources: res.sources,
        responseTime: res.processing_time,
      })

      // Auto-speak the greeting
      await speakText(res.reply)
    } catch {
      setCallStarting(false)
    }
  }

  const speakText = async (text: string) => {
    setSpeaking(true)
    try {
      const { textToSpeech } = await import('../../services/api')
      const audioRes = await textToSpeech(text)
      if (audioRes.audio) {
        const audio = new Audio(`data:audio/wav;base64,${audioRes.audio}`)
        await audio.play()
      }
    } catch {}
    setSpeaking(false)
  }

  const handleSendVoiceMessage = async (text: string) => {
    addMessage({ role: 'user', content: text })
    setSpeaking(true)
    try {
      const res = await sendMessage(text, conversationId)
      addMessage({ role: 'assistant', content: res.reply })
      setStats({
        tokens: res.tokens_used,
        sources: res.sources,
        responseTime: res.processing_time,
      })
      await speakText(res.reply)
    } catch {}
    setSpeaking(false)
  }

  if (isCallActive) {
    return null // Avatar takes full space
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="idle"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col items-center justify-center text-center px-6"
      >
        {/* Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="mb-8"
        >
          <div className="relative">
            <div className="w-20 h-20 rounded-full glass flex items-center justify-center glow-border">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-cyber-primary/20 to-cyber-secondary/20 flex items-center justify-center">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z" />
                  <path d="M16 14H8a4 4 0 0 0-4 4v2h16v-2a4 4 0 0 0-4-4z" />
                  <circle cx="12" cy="16" r="1" fill="#00f0ff" />
                </svg>
              </div>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-cyber-primary animate-pulse-slow" />
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-4xl md:text-5xl font-display font-bold text-gradient mb-3"
        >
          CyberAI Assistant
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-base md:text-lg text-cyber-muted/80 mb-10 max-w-md"
        >
          Tu asistente inteligente de ciberseguridad
        </motion.p>

        {/* Start button */}
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleStartCall}
          disabled={isCallStarting}
          className="group relative px-8 py-4 rounded-2xl bg-gradient-to-r from-cyber-primary/20 to-cyber-secondary/20 border border-cyber-primary/30 text-white font-medium text-lg flex items-center gap-3 hover:from-cyber-primary/30 hover:to-cyber-secondary/30 transition-all duration-300 glow-primary disabled:opacity-50"
        >
          {isCallStarting ? (
            <>
              <Loader2 size={22} className="animate-spin" />
              Conectando...
            </>
          ) : (
            <>
              <div className="w-10 h-10 rounded-full bg-cyber-primary/20 flex items-center justify-center group-hover:bg-cyber-primary/30 transition-colors">
                <Mic size={20} className="text-cyber-primary" />
              </div>
              Iniciar conversación
            </>
          )}
        </motion.button>

        {/* Bottom hint */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.6 }}
          className="mt-8 text-xs text-cyber-muted/40 flex items-center gap-2"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-cyber-success animate-pulse-slow" />
          Sistema listo · Groq Llama 3.1 8B
        </motion.p>
      </motion.div>
    </AnimatePresence>
  )
}
