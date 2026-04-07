import { ChevronRight, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';

interface GraphBreadcrumbProps {
  domainId: string;
}

/**
 * Breadcrumb trail: Home > Domain > Subdomain > Concept
 * Appears at top-left of graph page when a concept is selected.
 */
export function GraphBreadcrumb({ domainId }: GraphBreadcrumbProps) {
  const navigate = useNavigate();
  const { getActiveDomainInfo } = useDomainStore();
  const { selectedNode, selectNode } = useGraphStore();
  const domainInfo = getActiveDomainInfo();

  const crumbs = [
    {
      label: '首页',
      icon: <Home size={12} />,
      onClick: () => navigate('/'),
    },
    {
      label: domainInfo?.name || domainId,
      icon: <span className="text-xs">{domainInfo?.icon || '🌐'}</span>,
      onClick: () => {
        selectNode(null);
        navigate(`/domain/${domainId}`);
      },
    },
  ];

  if (selectedNode) {
    // Add subdomain if available
    if (selectedNode.subdomain_id) {
      crumbs.push({
        label: selectedNode.subdomain_id.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        icon: <span className="text-xs">📁</span>,
        onClick: () => {
          selectNode(null);
          navigate(`/domain/${domainId}`);
        },
      });
    }
    // Add concept name
    crumbs.push({
      label: selectedNode.label,
      icon: <span className="text-xs">📖</span>,
      onClick: () => {},
    });
  }

  return (
    <nav
      className="absolute top-4 left-4 z-20 flex items-center gap-1 pointer-events-auto animate-fade-in"
      style={{
        padding: '8px 14px',
        borderRadius: 12,
        background: 'rgba(245,245,242,0.90)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(0,0,0,0.08)',
        boxShadow: '0 1px 6px rgba(0,0,0,0.04)',
        maxWidth: '60vw',
      }}
      aria-label="Breadcrumb"
    >
      {crumbs.map((crumb, i) => (
        <div key={i} className="flex items-center gap-1">
          {i > 0 && (
            <ChevronRight
              size={11}
              className="flex-shrink-0"
              style={{ color: 'var(--color-text-tertiary)' }}
            />
          )}
          <button
            onClick={crumb.onClick}
            className="flex items-center gap-1.5 text-xs font-medium truncate transition-colors rounded-md px-1.5 py-0.5 hover:bg-black/5"
            style={{
              color: i === crumbs.length - 1 ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
              fontWeight: i === crumbs.length - 1 ? 600 : 400,
              maxWidth: i === crumbs.length - 1 ? 160 : 120,
              cursor: i === crumbs.length - 1 ? 'default' : 'pointer',
            }}
            disabled={i === crumbs.length - 1}
          >
            {crumb.icon}
            <span className="truncate">{crumb.label}</span>
          </button>
        </div>
      ))}
    </nav>
  );
}