import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import useStore from './store/useStore';
import SOCBackground from './components/Background/SOCBackground';
import CyberAvatar from './components/Avatar/CyberAvatar';
import ChatPanel from './components/Chat/ChatPanel';
import Sidebar from './components/Sidebar/Sidebar';
import StatsPanel from './components/StatsPanel/StatsPanel';
import { getHistory, getDocuments } from './services/api';

export default function App() {
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const currentView = useStore((s) => s.currentView);
  const setConversations = useStore((s) => s.setConversations);
  const setDocuments = useStore((s) => s.setDocuments);

  useEffect(() => {
    getHistory().then(setConversations).catch(() => {});
    getDocuments().then(setDocuments).catch(() => {});
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-cyber-bg">
      <SOCBackground />

      <div className="absolute inset-0 scanline pointer-events-none z-0" />

      <div className="relative z-10 flex h-full">
        <AnimatePresence>
          {sidebarOpen && <Sidebar />}
        </AnimatePresence>

        <div className="flex-1 flex flex-col h-full">
          <div className="flex-1 flex items-stretch">
            <div className="flex-1 flex flex-col relative">
              <CyberAvatar />
              <ChatPanel />
            </div>
            <StatsPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
