import { useEffect, useRef } from 'react';
import {
  X, Globe, Check, Loader, Home, BarChart3, Settings, Trophy,
  MessageCircle, LogIn, User, AlertTriangle, RotateCcw,
  Route as RouteIcon, Compass,
} from 'lucide-react';

interface DomainInfo {
  id: string;
  name: string;
  icon: string;
  description?: string;
  is_active?: boolean;
}

interface GraphHubBarProps {
  chatOpen: boolean;
  activeDomain: string;
  activeDomains: DomainInfo[];
  isUsingFreeAPI: boolean;
  isLoggedIn: boolean;
  supabaseConfigured: boolean;
  achievementBadge: number;
  dueReviewCount: number;
  showDashboard: boolean;
  showSettings: boolean;
  showAchievements: boolean;
  showDomainPicker: boolean;
  showRecommend: boolean;
  onToggleDashboard: () => void;
  onToggleSettings: () => void;
  onToggleAchievements: () => void;
  onToggleDomainPicker: () => void;
  onToggleRecommend: () => void;
  onDomainSwitch: (domainId: string) => void;
  onNavigate: (path: string) => void;
  onSignOut: () => void;
}

function HubButton({ icon: Icon, label, active, onClick }: { icon: typeof BarChart3; label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="flex flex-col items-center justify-center rounded-xl transition-all whitespace-nowrap"
      style={{
        width: 56, height: 48,
        backgroundColor: active ? 'rgba(0,0,0,0.06)' : 'transparent',
        color: active ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
      }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)'; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'transparent'; }}>
      <Icon size={18} strokeWidth={active ? 2.5 : 2} />
      <span style={{ fontSize: 10, fontWeight: 500, marginTop: 2, lineHeight: 1 }}>{label}</span>
    </button>
  );
}

export function GraphHubBar(props: GraphHubBarProps) {
  const {
    chatOpen, activeDomain, activeDomains, isUsingFreeAPI, isLoggedIn,
    supabaseConfigured, achievementBadge, dueReviewCount,
    showDashboard, showSettings, showAchievements, showDomainPicker, showRecommend,
    onToggleDashboard, onToggleSettings, onToggleAchievements,
    onToggleDomainPicker, onToggleRecommend, onDomainSwitch, onNavigate, onSignOut,
  } = props;

  const domainPickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!showDomainPicker) return;
    function handleClick(e: MouseEvent) {
      if (domainPickerRef.current && !domainPickerRef.current.contains(e.target as Node)) onToggleDomainPicker();
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showDomainPicker, onToggleDomainPicker]);

  return (
    <div className="absolute bottom-6 z-30 pointer-events-auto transition-all duration-500 ease-out" style={chatOpen ? { left: '25%', transform: 'translateX(-50%)' } : { left: '50%', transform: 'translateX(-50%)' }} ref={domainPickerRef}>
      <div className="flex items-center" style={{
        padding: '0 8px', height: 64, borderRadius: 20, background: 'rgba(245,245,242,0.92)', backdropFilter: 'blur(20px)',
        border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 8px 32px rgba(0,0,0,0.08)', gap: 4,
      }}>
        <HubButton icon={Home} label="首页" active={false} onClick={() => onNavigate('/')} />
        <HubButton icon={Globe} label="知域" active={showDomainPicker} onClick={onToggleDomainPicker} />
        <HubButton icon={BarChart3} label="进度" active={showDashboard} onClick={onToggleDashboard} />
        <div style={{ position: 'relative' }}>
          <HubButton icon={Trophy} label="成就" active={showAchievements} onClick={onToggleAchievements} />
          {achievementBadge > 0 && (
            <span style={{
              position: 'absolute', top: 2, right: 4,
              width: 16, height: 16, borderRadius: '50%',
              backgroundColor: 'var(--color-accent-rose)',
              color: '#fff', fontSize: 10, fontWeight: 700,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              lineHeight: 1,
            }}>{achievementBadge > 9 ? '9+' : achievementBadge}</span>
          )}
        </div>
        <div style={{ position: 'relative' }}>
          <HubButton icon={RotateCcw} label="复习" active={false} onClick={() => onNavigate(activeDomain ? `/review/${activeDomain}` : '/review')} />
          {dueReviewCount > 0 && (
            <span style={{
              position: 'absolute', top: 2, right: 4,
              minWidth: 16, height: 16, borderRadius: '50%',
              backgroundColor: 'var(--color-accent-amber)',
              color: '#fff', fontSize: 10, fontWeight: 700,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              lineHeight: 1, padding: '0 3px',
            }}>{dueReviewCount > 99 ? '99+' : dueReviewCount}</span>
          )}
        </div>
        <HubButton icon={RouteIcon} label="路径" active={false} onClick={() => onNavigate(`/path/${activeDomain}`)} />
        <button onClick={onToggleRecommend} className="flex items-center gap-2 rounded-2xl transition-all font-semibold whitespace-nowrap" style={{
          padding: '8px 20px', height: 48,
          backgroundColor: showRecommend ? 'var(--color-accent-primary)' : 'rgba(16,185,129,0.1)',
          color: showRecommend ? '#ffffff' : 'var(--color-accent-primary)', fontSize: 14,
        }}>
          <Compass size={18} />
          <span>推荐</span>
        </button>
        <HubButton icon={Settings} label="设置" active={showSettings} onClick={onToggleSettings} />
        {supabaseConfigured && isLoggedIn ? (
          <HubButton icon={User} label="我的" active={false} onClick={onSignOut} />
        ) : (
          <HubButton icon={LogIn} label="登录" active={false} onClick={() => onNavigate('/login')} />
        )}
        <HubButton icon={MessageCircle} label="交流" active={false} onClick={() => onNavigate('/community')} />
      </div>

      {/* Free API warning banner */}
      {isUsingFreeAPI && (
        <div
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap flex items-center gap-2 rounded-full animate-fade-in"
          style={{
            padding: '6px 16px',
            background: 'rgba(245, 158, 11, 0.12)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            fontSize: 12,
            color: 'var(--color-accent-amber)',
            fontWeight: 500,
          }}
        >
          <AlertTriangle size={13} />
          <span>正在使用免费 API，质量和稳定性可能不佳</span>
          <button
            onClick={onToggleSettings}
            className="underline font-semibold"
            style={{ color: 'var(--color-accent-amber)', textUnderlineOffset: 2 }}
          >
            去设置
          </button>
        </div>
      )}

      {/* Domain Picker Panel */}
      {showDomainPicker && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 animate-fade-in-scale" style={{ width: 320 }}>
          <div style={{
            borderRadius: 16, overflow: 'hidden', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(20px)',
            border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 12px 48px rgba(0,0,0,0.1)',
          }}>
            <div className="flex items-center justify-between" style={{ padding: '14px 20px', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-center gap-2">
                <Globe size={14} style={{ color: 'var(--color-accent-primary)' }} />
                <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>知识域</span>
              </div>
              <button onClick={onToggleDomainPicker} className="p-1.5 rounded-full hover:bg-black/5" style={{ color: 'var(--color-text-tertiary)' }}><X size={14} /></button>
            </div>
            <div style={{ maxHeight: 320, overflowY: 'auto' }}>
              {activeDomains.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 px-5" style={{ gap: 8 }}>
                  <Loader size={18} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
                  <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>请启动后端服务以加载知识域</span>
                </div>
              ) : activeDomains.map((domain) => {
                const isActive = domain.id === activeDomain;
                return (
                  <button key={domain.id} onClick={() => onDomainSwitch(domain.id)}
                    className="w-full text-left flex items-center gap-3 transition-colors"
                    style={{ padding: '10px 20px', backgroundColor: isActive ? 'rgba(0,0,0,0.04)' : 'transparent', borderBottom: '1px solid rgba(0,0,0,0.04)' }}
                    onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = isActive ? 'rgba(0,0,0,0.04)' : 'transparent'; }}>
                    <span className="text-lg">{domain.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{domain.name}</div>
                      <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{domain.description}</div>
                    </div>
                    {isActive && <Check size={15} className="shrink-0" style={{ color: 'var(--color-accent-primary)' }} />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}