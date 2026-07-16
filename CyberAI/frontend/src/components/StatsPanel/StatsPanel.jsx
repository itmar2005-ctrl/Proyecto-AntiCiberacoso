import useStore from '../../store/useStore';
import { Cpu, MemoryStick, Brain, Activity, BookOpen, Clock, Database, Zap } from 'lucide-react';

function StatItem({ icon: Icon, label, value, color = 'text-cyber-primary' }) {
  return (
    <div className="flex items-center gap-2 px-3 py-2">
      <Icon size={14} className={`${color} flex-shrink-0`} />
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-cyber-muted uppercase tracking-wider">{label}</div>
        <div className="text-xs text-cyber-text font-mono truncate">{value}</div>
      </div>
    </div>
  );
}

export default function StatsPanel() {
  const stats = useStore((s) => s.stats);

  return (
    <div className="w-56 border-l border-cyber-border/50 bg-cyber-surface/30 backdrop-blur-sm flex flex-col overflow-y-auto">
      <div className="p-3 border-b border-cyber-border/50">
        <h3 className="text-xs font-mono text-cyber-primary uppercase tracking-wider glow-text">
          Sistema
        </h3>
      </div>

      <div className="divide-y divide-cyber-border/30">
        <StatItem icon={Brain} label="Modelo" value={stats.model} />
        <StatItem icon={Activity} label="Tiempo Resp." value={`${stats.responseTime || 0}s`} />
        <StatItem icon={Zap} label="Tokens" value={stats.tokens?.toLocaleString() || '0'} />
        <StatItem icon={BookOpen} label="Fuentes" value={stats.sources?.length > 0 ? stats.sources.join(', ') : 'Ninguna'} />
        <StatItem icon={Database} label="Base Vectorial" value="ChromaDB" />
        <StatItem icon={Cpu} label="CPU" value={stats.cpu} color="text-cyber-accent" />
        <StatItem icon={MemoryStick} label="RAM" value={stats.ram} color="text-cyber-accent" />
        <StatItem icon={Clock} label="Proveedor" value="Groq API" />
      </div>

      {stats.sources?.length > 0 && (
        <div className="p-3 border-t border-cyber-border/50">
          <div className="text-[10px] text-cyber-muted uppercase tracking-wider mb-2 font-mono">
            Documentos consultados
          </div>
          {stats.sources.map((src, i) => (
            <div key={i} className="flex items-center gap-1.5 text-xs text-cyber-text/60 py-1">
              <BookOpen size={10} className="text-cyber-primary/60" />
              <span className="truncate">{src}</span>
            </div>
          ))}
        </div>
      )}

      <div className="mt-auto p-3 border-t border-cyber-border/50">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyber-success animate-pulse" />
          <span className="text-[10px] text-cyber-muted font-mono">API Conectada</span>
        </div>
      </div>
    </div>
  );
}
