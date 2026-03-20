import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader, Sparkles } from 'lucide-react';

export function HomePage() {
  const navigate = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const activeDomains = domains.filter((d) => (d as any).is_active !== false);

  useEffect(() => {
    fetchDomains();
  }, [fetchDomains]);

  return (
    <div className="h-dvh w-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-5xl mx-auto" style={{ padding: '60px 24px 80px' }}>
        {/* Header */}
        <div className="text-center" style={{ marginBottom: 48 }}>
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 mb-5" style={{
            backgroundColor: 'rgba(16,185,129,0.08)', color: 'var(--color-accent-primary)', fontSize: 13, fontWeight: 600,
          }}>
            <Sparkles size={14} />
            <span>知识星球</span>
          </div>
          <h1 className="font-bold" style={{ fontSize: 32, color: 'var(--color-text-primary)', marginBottom: 12, lineHeight: 1.3 }}>
            选择你的知识领域
          </h1>
          <p style={{ fontSize: 15, color: 'var(--color-text-tertiary)', maxWidth: 420, margin: '0 auto', lineHeight: 1.6 }}>
            每个星球是一个完整的知识体系，点击进入 3D 知识图谱开始探索
          </p>
        </div>

        {/* Domain Grid */}
        {loading && activeDomains.length === 0 ? (
          <div className="flex items-center justify-center" style={{ padding: '80px 0' }}>
            <Loader size={24} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: 16,
          }}>
            {activeDomains.map((domain) => {
              const stats = (domain as any).stats as { total_concepts?: number; subdomains?: number } | undefined;
              return (
                <button
                  key={domain.id}
                  onClick={() => navigate(`/domain/${domain.id}`)}
                  className="text-left rounded-2xl transition-all group"
                  style={{
                    padding: 24,
                    backgroundColor: 'var(--color-surface-1)',
                    border: '1px solid var(--color-border-subtle)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = domain.color;
                    e.currentTarget.style.boxShadow = `0 4px 24px ${domain.color}18`;
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  {/* Icon + Color dot */}
                  <div className="flex items-center gap-3" style={{ marginBottom: 14 }}>
                    <span style={{ fontSize: 28 }}>{domain.icon}</span>
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: domain.color }} />
                  </div>

                  {/* Name */}
                  <h3 className="font-bold" style={{ fontSize: 18, color: 'var(--color-text-primary)', marginBottom: 6 }}>
                    {domain.name}
                  </h3>

                  {/* Description */}
                  <p className="line-clamp-2" style={{ fontSize: 13, color: 'var(--color-text-tertiary)', lineHeight: 1.5, marginBottom: 16 }}>
                    {domain.description}
                  </p>

                  {/* Stats */}
                  {stats && (
                    <div className="flex items-center gap-4" style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>
                      {stats.total_concepts != null && (
                        <span>{stats.total_concepts} 知识点</span>
                      )}
                      {stats.subdomains != null && (
                        <span>{stats.subdomains} 子领域</span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
