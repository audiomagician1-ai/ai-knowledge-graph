import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';
import { Globe, ChevronDown, Check, Loader } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export function DomainSwitcher() {
  const { domains, activeDomain, switchDomain, loading } = useDomainStore();
  const { loadGraphData } = useGraphStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  const activeDomainInfo = domains.find((d) => d.id === activeDomain);
  const activeDomains = domains.filter((d) => (d as any).is_active !== false);

  const handleSwitch = (domainId: string) => {
    if (domainId === activeDomain) { setOpen(false); return; }
    switchDomain(domainId);
    loadGraphData(domainId);
    setOpen(false);
  };

  // Don't render if only one domain or still loading
  if (loading && domains.length === 0) {
    return (
      <div className="px-4 mb-2">
        <div className="flex items-center gap-3 rounded-lg px-4 py-3" style={{ backgroundColor: 'var(--color-surface-2)' }}>
          <Loader size={16} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
          <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>加载知识域...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 mb-2" ref={ref}>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 rounded-lg px-4 py-3 transition-colors"
        style={{
          backgroundColor: open ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
          border: '1px solid var(--color-border)',
          minHeight: 48,
        }}
        onMouseEnter={(e) => { if (!open) e.currentTarget.style.backgroundColor = 'var(--color-surface-3)'; }}
        onMouseLeave={(e) => { if (!open) e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
      >
        <span className="text-lg" role="img" aria-label="domain icon">
          {activeDomainInfo?.icon || '🌐'}
        </span>
        <div className="flex-1 min-w-0 text-left">
          <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
            {activeDomainInfo?.name || activeDomain}
          </div>
          {activeDomainInfo?.concept_count != null && (
            <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              {activeDomainInfo.concept_count} 个概念
            </div>
          )}
        </div>
        <ChevronDown
          size={16}
          className="shrink-0 transition-transform duration-200"
          style={{
            color: 'var(--color-text-tertiary)',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        />
      </button>

      {/* Dropdown */}
      {open && activeDomains.length > 0 && (
        <div
          className="mt-1 rounded-lg overflow-hidden animate-fade-in"
          style={{
            backgroundColor: 'var(--color-surface-1)',
            border: '1px solid var(--color-border)',
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
          }}
        >
          {activeDomains.map((domain) => {
            const isActive = domain.id === activeDomain;
            return (
              <button
                key={domain.id}
                onClick={() => handleSwitch(domain.id)}
                className="w-full flex items-center gap-3 px-4 py-3 transition-colors"
                style={{
                  backgroundColor: isActive ? 'var(--color-surface-3)' : 'transparent',
                  borderBottom: '1px solid var(--color-border)',
                }}
                onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
                onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = isActive ? 'var(--color-surface-3)' : 'transparent'; }}
              >
                <span className="text-lg" role="img" aria-label={domain.name}>
                  {domain.icon}
                </span>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
                    {domain.name}
                  </div>
                  <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                    {domain.description}
                  </div>
                </div>
                {isActive && (
                  <Check size={16} className="shrink-0" style={{ color: 'var(--color-accent-primary)' }} />
                )}
              </button>
            );
          })}

          {/* Placeholder for future domains */}
          {activeDomains.length <= 1 && (
            <div className="px-4 py-3 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              <Globe size={12} className="inline mr-1.5" style={{ verticalAlign: 'middle' }} />
              更多知识域即将推出...
            </div>
          )}
        </div>
      )}
    </div>
  );
}