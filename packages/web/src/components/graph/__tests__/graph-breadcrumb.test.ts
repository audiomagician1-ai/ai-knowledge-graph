import { describe, it, expect } from 'vitest';

/**
 * Tests for GraphBreadcrumb component logic.
 * Tests the breadcrumb trail generation from domain/concept state.
 */

interface BreadcrumbItem {
  label: string;
  isLast: boolean;
}

function buildBreadcrumbs(params: {
  domainName: string;
  domainId: string;
  selectedNode?: { label: string; subdomain_id?: string } | null;
}): BreadcrumbItem[] {
  const { domainName, domainId, selectedNode } = params;
  
  const crumbs: BreadcrumbItem[] = [
    { label: '首页', isLast: false },
    { label: domainName || domainId, isLast: !selectedNode },
  ];

  if (selectedNode) {
    crumbs[1].isLast = false;
    if (selectedNode.subdomain_id) {
      crumbs.push({ label: selectedNode.subdomain_id, isLast: false });
    }
    crumbs.push({ label: selectedNode.label, isLast: true });
  }

  return crumbs;
}

describe('GraphBreadcrumb logic', () => {
  it('shows Home > Domain when no concept selected', () => {
    const crumbs = buildBreadcrumbs({ domainName: 'AI工程', domainId: 'ai-engineering' });
    expect(crumbs.length).toBe(2);
    expect(crumbs[0].label).toBe('首页');
    expect(crumbs[1].label).toBe('AI工程');
    expect(crumbs[1].isLast).toBe(true);
  });

  it('shows Home > Domain > Subdomain > Concept when concept selected', () => {
    const crumbs = buildBreadcrumbs({
      domainName: 'AI工程',
      domainId: 'ai-engineering',
      selectedNode: { label: 'CNN卷积神经网络', subdomain_id: 'deep-learning' },
    });
    expect(crumbs.length).toBe(4);
    expect(crumbs[2].label).toBe('deep-learning');
    expect(crumbs[3].label).toBe('CNN卷积神经网络');
    expect(crumbs[3].isLast).toBe(true);
  });

  it('skips subdomain when not available', () => {
    const crumbs = buildBreadcrumbs({
      domainName: '编程',
      domainId: 'programming',
      selectedNode: { label: '变量' },
    });
    expect(crumbs.length).toBe(3);
    expect(crumbs[2].label).toBe('变量');
  });

  it('falls back to domainId when domainName is empty', () => {
    const crumbs = buildBreadcrumbs({ domainName: '', domainId: 'math' });
    expect(crumbs[1].label).toBe('math');
  });

  it('marks only the last item as isLast', () => {
    const crumbs = buildBreadcrumbs({
      domainName: 'Test',
      domainId: 'test',
      selectedNode: { label: 'Node A', subdomain_id: 'sub1' },
    });
    const lastItems = crumbs.filter((c) => c.isLast);
    expect(lastItems.length).toBe(1);
    expect(lastItems[0].label).toBe('Node A');
  });
});
