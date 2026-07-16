import { motion } from 'framer-motion'
import {
  Mic, MicOff, MessageSquare, History, Settings, PhoneOff, FileUp, Square
} from 'lucide-react'
import { useStore } from '../../store/useStore'

interface ControlButtonProps {
  icon: React.ReactNode
  label: string
  onClick?: () => void
  active?: boolean
  danger?: boolean
  disabled?: boolean
}

function ControlButton({ icon, label, onClick, active, danger, disabled }: ControlButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      disabled={disabled}
      className={`relative flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all duration-200
        ${danger
          ? 'bg-cyber-danger/15 text-cyber-danger hover:bg-cyber-danger/25'
          : active
            ? 'bg-cyber-primary/15 text-cyber-primary'
            : 'text-cyber-muted hover:text-cyber-text hover:bg-white/5'
        }
        ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors
        ${danger ? 'bg-cyber-danger/10' : active ? 'bg-cyber-primary/10' : ''}
      `}>
        {icon}
      </div>
      <span className="text-[10px] font-medium tracking-wider uppercase">{label}</span>
    </motion.button>
  )
}

export default function ControlBar() {
  const isCallActive = useStore((s) => s.isCallActive)
  const isMuted = useStore((s) => s.isMuted)
  const isListening = useStore((s) => s.isListening)
  const chatOpen = useStore((s) => s.chatOpen)
  const setChatOpen = useStore((s) => s.setChatOpen)
  const toggleMute = useStore((s) => s.toggleMute)
  const setShowAdvanced = useStore((s) => s.setShowAdvanced)
  const resetCall = useStore((s) => s.resetCall)
  const setSidebarOpen = useStore((s) => s.setSidebarOpen)

  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.6, duration: 0.5 }}
      className="glass rounded-2xl px-2 py-2 flex items-center gap-1 glow-border"
    >
      {/* Mic */}
      <ControlButton
        icon={isMuted ? <MicOff size={18} /> : <Mic size={18} />}
        label={isMuted ? 'Silencio' : isListening ? 'Grabando' : 'Micrófono'}
        active={isListening}
        onClick={toggleMute}
      />

      <div className="w-px h-8 bg-white/5" />

      {/* Chat */}
      <ControlButton
        icon={<MessageSquare size={18} />}
        label="Chat"
        active={chatOpen}
        onClick={() => setChatOpen(!chatOpen)}
      />

      {/* History */}
      <ControlButton
        icon={<History size={18} />}
        label="Historial"
        onClick={() => setSidebarOpen(true)}
      />

      {/* Upload */}
      <ControlButton
        icon={<FileUp size={18} />}
        label="Documentos"
        onClick={() => {
          setSidebarOpen(true)
          useStore.getState().setShowAdvanced(true)
        }}
      />

      {/* Settings */}
      <ControlButton
        icon={<Settings size={18} />}
        label="Ajustes"
        onClick={() => setShowAdvanced(true)}
      />

      {isCallActive && (
        <>
          <div className="w-px h-8 bg-white/5" />

          {/* End Call */}
          <ControlButton
            icon={<PhoneOff size={18} />}
            label="Colgar"
            danger
            onClick={resetCall}
          />
        </>
      )}
    </motion.div>
  )
}
