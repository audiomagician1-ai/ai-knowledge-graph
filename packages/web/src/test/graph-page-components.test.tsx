import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GraphSearchOverlay } from '../components/graph/GraphSearchOverlay';
import { GraphRecommendPanel, type Recommendation } from '../components/graph/GraphRecommendPanel';
import { GraphConceptHeader } from '../components/graph/GraphConceptHeader';
import type { GraphData, GraphNode } from '@akg/shared';

/* ── Helpers ── */
const makeNode = (id: string, label: string, opts?: Partial<GraphNode>): GraphNode => ({
  id, label, difficulty: 3, subdomain: 'sub-a',
  estimated_minutes: 10, is_milestone: false, status: 'not_started',
  ...opts,
} as GraphNode);

const mockGraphData: GraphData = {
  nodes: [
    makeNode('a', 'Alpha'),
    makeNode('b', 'Beta', { is_milestone: true }),
    makeNode('c', 'Gamma'),
  ],
  edges: [],
};

/* ── GraphSearchOverlay ── */
describe('GraphSearchOverlay', () => {
  it('renders search input', () => {
    render(<GraphSearchOverlay graphData={mockGraphData} onNodeClick={vi.fn()} />);
    expect(screen.getByPlaceholderText('搜索知识节点...')).toBeDefined();
  });

  it('filters nodes by query', () => {
    render(<GraphSearchOverlay graphData={mockGraphData} onNodeClick={vi.fn()} />);
    const input = screen.getByPlaceholderText('搜索知识节点...');
    fireEvent.change(input, { target: { value: 'Alpha' } });
    expect(screen.getByText('Alpha')).toBeDefined();
    expect(screen.queryByText('Gamma')).toBeNull();
  });

  it('calls onNodeClick when result is clicked', () => {
    const onClick = vi.fn();
    render(<GraphSearchOverlay graphData={mockGraphData} onNodeClick={onClick} />);
    fireEvent.change(screen.getByPlaceholderText('搜索知识节点...'), { target: { value: 'Beta' } });
    fireEvent.click(screen.getByText('Beta'));
    expect(onClick).toHaveBeenCalledWith(expect.objectContaining({ id: 'b', label: 'Beta' }));
  });

  it('shows nothing when graphData is null', () => {
    render(<GraphSearchOverlay graphData={null} onNodeClick={vi.fn()} />);
    fireEvent.change(screen.getByPlaceholderText('搜索知识节点...'), { target: { value: 'test' } });
    // no results rendered
    expect(screen.queryByText('Alpha')).toBeNull();
  });
});

/* ── GraphRecommendPanel ── */
describe('GraphRecommendPanel', () => {
  const recs: Recommendation[] = [
    { concept_id: 'a', name: 'Alpha', difficulty: 2, estimated_minutes: 10, is_milestone: false, score: 80, reason: 'prereq', status: 'not_started' },
    { concept_id: 'b', name: 'Beta', difficulty: 7, estimated_minutes: 20, is_milestone: true, score: 90, reason: 'next', status: 'not_started' },
  ];

  it('renders loading state', () => {
    render(<GraphRecommendPanel recommendations={[]} loading={true} chatOpen={false} graphData={null} onNodeClick={vi.fn()} onClose={vi.fn()} />);
    // Loader spinner should be in DOM (animated spin)
    expect(document.querySelector('.animate-spin')).toBeTruthy();
  });

  it('renders empty state', () => {
    render(<GraphRecommendPanel recommendations={[]} loading={false} chatOpen={false} graphData={null} onNodeClick={vi.fn()} onClose={vi.fn()} />);
    expect(screen.getByText('暂无推荐')).toBeDefined();
  });

  it('renders recommendation list', () => {
    render(<GraphRecommendPanel recommendations={recs} loading={false} chatOpen={false} graphData={mockGraphData} onNodeClick={vi.fn()} onClose={vi.fn()} />);
    expect(screen.getByText('Alpha')).toBeDefined();
    expect(screen.getByText('Beta')).toBeDefined();
    expect(screen.getByText('Lv.7')).toBeDefined();
  });

  it('calls onClose when close button clicked', () => {
    const onClose = vi.fn();
    render(<GraphRecommendPanel recommendations={recs} loading={false} chatOpen={false} graphData={mockGraphData} onNodeClick={vi.fn()} onClose={onClose} />);
    // Close button is in the header row — find all buttons, the first non-recommendation one
    const buttons = screen.getAllByRole('button');
    // First button is the X close button (before recommendation items)
    fireEvent.click(buttons[0]);
    expect(onClose).toHaveBeenCalled();
  });
});

/* ── GraphConceptHeader ── */
describe('GraphConceptHeader', () => {
  it('renders node info with difficulty', () => {
    const node = makeNode('a', 'Variables', { difficulty: 2, estimated_minutes: 15 });
    render(<GraphConceptHeader node={node} progress={{}} onClose={vi.fn()} />);
    expect(screen.getByText('Variables')).toBeDefined();
    expect(screen.getByText(/Lv\.2/)).toBeDefined();
    expect(screen.getByText('15min')).toBeDefined();
  });

  it('shows mastered status', () => {
    const node = makeNode('a', 'Variables');
    render(<GraphConceptHeader node={node} progress={{ a: { status: 'mastered' } }} onClose={vi.fn()} />);
    expect(screen.getByText('已掌握')).toBeDefined();
  });

  it('shows learning status', () => {
    const node = makeNode('a', 'Variables');
    render(<GraphConceptHeader node={node} progress={{ a: { status: 'learning' } }} onClose={vi.fn()} />);
    expect(screen.getByText('学习中')).toBeDefined();
  });

  it('shows milestone star', () => {
    const node = makeNode('a', 'Milestone', { is_milestone: true });
    const { container } = render(<GraphConceptHeader node={node} progress={{}} onClose={vi.fn()} />);
    // Star icon should be present (SVG)
    expect(container.querySelector('svg')).toBeTruthy();
  });

  it('calls onClose when X clicked', () => {
    const onClose = vi.fn();
    const node = makeNode('a', 'Test');
    render(<GraphConceptHeader node={node} progress={{}} onClose={onClose} />);
    // The close button is the last button
    const buttons = screen.getAllByRole('button');
    fireEvent.click(buttons[buttons.length - 1]);
    expect(onClose).toHaveBeenCalled();
  });

  it('shows recommended badge when not mastered or learning', () => {
    const node = makeNode('a', 'Variables', { is_recommended: true });
    render(<GraphConceptHeader node={node} progress={{}} onClose={vi.fn()} />);
    expect(screen.getByText('推荐')).toBeDefined();
  });
});
