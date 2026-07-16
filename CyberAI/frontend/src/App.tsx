import { useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import { useStore } from './store/useStore'
import { getHistory, getDocuments } from './services/api'
import SOCBackground from './components/Background/SOCBackground'
import CyberAvatar from './components/Avatar/CyberAvatar'
import CallView from './components/CallView/CallView'
import ControlBar from './components/Controls/ControlBar'
import ChatPanel from './components/Chat/ChatPanel'
import Sidebar from './components/Sidebar/Sidebar'

export default function App() {
  const chatOpen = useStore((s) => s.chatOpen)
  const sidebarOpen = useStore((s) => s.sidebarOpen)
  const isCallActive = useStore((s) => s.isCallActive)
  const setConversations = useStore((s) => s.setConversations)
  const setDocuments = useStore((s) => s.setDocuments)

  useEffect(() => {
    getHistory().then(setConversations).catch(() => {})
    getDocuments().then(setDocuments).catch(() => {})
  }, [])

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-cyber-black">
      {/* SOC Background - always visible */}
      <div className={`absolute inset-0 transition-all duration-1000 ${isCallActive ? 'scale-100' : 'scale-105'}`}>
        <SOCBackground />
      </div>

      {/* Scanline overlay effect */}
      <div className="absolute inset-0 pointer-events-none z-[1] opacity-[0.03]"
        style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,240,255,0.3) 2px, rgba(0,240,255,0.3) 4px)',
        }}
      />

      {/* Main content */}
      <div className="relative z-10 h-full flex">
        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && <Sidebar />}
        </AnimatePresence>

        {/* Center area */}
        <div className="flex-1 flex flex-col h-full relative">
          {/* AI Label - top left */}
          <div className="absolute top-6 left-6 z-30">
            <div className="flex items-center gap-2 glass rounded-full px-4 py-1.5">
              <div className="w-2 h-2 rounded-full bg-cyber-primary animate-pulse-slow" />
              <span className="text-xs font-medium text-cyber-primary/80 tracking-wider">AI</span>
            </div>
          </div>

          {/* Avatar / Call View */}
          <div className="flex-1 flex items-center justify-center relative">
            {/* Avatar (always visible behind UI) */}
            <div className={`absolute inset-0 flex items-center justify-center transition-all duration-700 ${
              isCallActive ? 'opacity-100 scale-100' : 'opacity-40 scale-95 blur-sm'
            }`}>
              <CyberAvatar />
            </div>

            {/* Call View overlay */}
            <CallView />
          </div>

          {/* Control Bar */}
          <div className="flex justify-center pb-6 relative z-20">
            <ControlBar />
          </div>

          {/* Advanced button - bottom right */}
          <div className="absolute bottom-6 right-6 z-30">
            <button
              onClick={() => useStore.getState().setShowAdvanced(true)}
              className="w-10 h-10 rounded-full glass flex items-center justify-center text-cyber-muted hover:text-cyber-primary hover:border-cyber-primary/30 transition-all"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
              </svg>
            </button>
          </div>
        </div>

        {/* Chat Panel - slides from right */}
        <AnimatePresence>
          {chatOpen && <ChatPanel />}
        </AnimatePresence>
      </div>
    </div>
  )
}
