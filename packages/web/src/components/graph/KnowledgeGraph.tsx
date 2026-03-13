import { useEffect, useRef, useCallback } from 'react';
import cytoscape from 'cytoscape';
import type { GraphData, GraphNode } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';

interface KnowledgeGraphProps {
  data: GraphData;
  onNodeClick: (node: GraphNode) => void;
  selectedNodeId?: string | null;
  activeSubdomain?: string | null;
}

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;

/**
 * Cytoscape.js 知识图谱可视化组件
 * - 力导向布局 (cose)
 * - 里程碑节点高亮发光
 * - 子域着色
 * - 点击/缩放/平移
 */
export function KnowledgeGraph({ data, onNodeClick, selectedNodeId, activeSubdomain }: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  // Build Cytoscape elements from GraphData
  const buildElements = useCallback(() => {
    const nodes = data.nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        subdomain_id: n.subdomain_id,
        difficulty: n.difficulty,
        status: n.status,
        is_milestone: n.is_milestone,
        estimated_minutes: n.estimated_minutes || 0,
        content_type: n.content_type || 'theory',
      },
    }));

    const edges = data.edges.map((e) => ({
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        relation_type: e.relation_type,
        strength: e.strength,
      },
    }));

    return [...nodes, ...edges];
  }, [data]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: buildElements(),
      minZoom: GRAPH_VISUAL.ZOOM_MIN,
      maxZoom: GRAPH_VISUAL.ZOOM_MAX,
      wheelSensitivity: 0.3,
      style: [
        // Default node style
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'font-size': '9px',
            'font-family': 'system-ui, -apple-system, sans-serif',
            'color': '#cbd5e1',
            'text-margin-y': 6,
            'text-outline-width': 2,
            'text-outline-color': '#0f172a',
            'width': 'mapData(difficulty, 1, 9, 20, 40)',
            'height': 'mapData(difficulty, 1, 9, 20, 40)',
            'background-color': (ele: cytoscape.NodeSingular) => {
              const sd = ele.data('subdomain_id') as string;
              return SUBDOMAIN_COLORS[sd] || '#6366f1';
            },
            'border-width': 1,
            'border-color': '#1e293b',
            'opacity': 0.85,
          } as cytoscape.Css.Node,
        },
        // Milestone node — golden glow
        {
          selector: 'node[?is_milestone]',
          style: {
            'border-width': 3,
            'border-color': GRAPH_VISUAL.MILESTONE_RING,
            'opacity': 1,
            'font-size': '11px',
            'font-weight': 'bold',
            'color': '#fde68a',
            'text-outline-color': '#1e293b',
            'width': 'mapData(difficulty, 1, 9, 28, 48)',
            'height': 'mapData(difficulty, 1, 9, 28, 48)',
            'shadow-blur': 15,
            'shadow-color': GRAPH_VISUAL.MILESTONE_GLOW,
            'shadow-opacity': 0.8,
            'shadow-offset-x': 0,
            'shadow-offset-y': 0,
          } as cytoscape.Css.Node,
        },
        // Mastered node
        {
          selector: 'node[status = "mastered"]',
          style: {
            'background-color': '#10b981',
            'opacity': 1,
          } as cytoscape.Css.Node,
        },
        // Learning node
        {
          selector: 'node[status = "learning"]',
          style: {
            'background-color': '#f59e0b',
            'opacity': 1,
          } as cytoscape.Css.Node,
        },
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#3b82f6',
            'opacity': 1,
            'font-size': '12px',
          } as cytoscape.Css.Node,
        },
        // Default edge
        {
          selector: 'edge',
          style: {
            'width': 'mapData(strength, 0.3, 1.0, 0.5, 2)',
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.6,
            'opacity': 0.4,
          } as cytoscape.Css.Edge,
        },
        // Prerequisite edge
        {
          selector: 'edge[relation_type = "prerequisite"]',
          style: {
            'line-color': '#475569',
            'target-arrow-color': '#475569',
          } as cytoscape.Css.Edge,
        },
        // Related edge (dashed)
        {
          selector: 'edge[relation_type = "related_to"]',
          style: {
            'line-style': 'dashed',
            'line-color': '#4b5563',
            'target-arrow-shape': 'none',
            'opacity': 0.25,
          } as cytoscape.Css.Edge,
        },
        // Highlighted neighbor edges
        {
          selector: '.highlighted',
          style: {
            'opacity': 1,
          },
        },
        {
          selector: '.dimmed',
          style: {
            'opacity': 0.15,
          },
        },
      ] as unknown as cytoscape.StylesheetCSS[],
      layout: {
        name: 'cose',
        idealEdgeLength: 80,
        nodeOverlap: 30,
        refresh: 20,
        fit: true,
        padding: 40,
        randomize: false,
        componentSpacing: 60,
        nodeRepulsion: 8000,
        edgeElasticity: 100,
        nestingFactor: 1.2,
        gravity: 0.5,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
        animate: false,
      } as cytoscape.CoseLayoutOptions,
    });

    // Node click handler
    cy.on('tap', 'node', (evt) => {
      const nodeData = evt.target.data();
      onNodeClick({
        id: nodeData.id,
        label: nodeData.label,
        domain_id: 'ai-engineering',
        subdomain_id: nodeData.subdomain_id,
        difficulty: nodeData.difficulty,
        status: nodeData.status,
        is_milestone: nodeData.is_milestone,
        estimated_minutes: nodeData.estimated_minutes,
        content_type: nodeData.content_type,
      } as GraphNode);

      // Highlight neighbors
      cy.elements().removeClass('highlighted dimmed');
      const selected = evt.target;
      const neighborhood = selected.neighborhood().add(selected);
      cy.elements().addClass('dimmed');
      neighborhood.removeClass('dimmed').addClass('highlighted');
    });

    // Click background to reset
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted dimmed');
        onNodeClick(null as unknown as GraphNode);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [data, buildElements, onNodeClick]);

  // Handle selected node externally
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (selectedNodeId) {
      const node = cy.getElementById(selectedNodeId);
      if (node.length) {
        cy.animate({
          center: { eles: node },
          zoom: 2,
        } as cytoscape.AnimateOptions, { duration: 300 });
      }
    }
  }, [selectedNodeId]);

  // Filter by subdomain
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (activeSubdomain) {
      cy.nodes().forEach((node) => {
        if (node.data('subdomain_id') === activeSubdomain) {
          node.style('opacity', 1);
        } else {
          node.style('opacity', 0.15);
        }
      });
    } else {
      cy.nodes().forEach((node) => {
        const isMilestone = node.data('is_milestone');
        node.style('opacity', isMilestone ? 1 : 0.85);
      });
    }
  }, [activeSubdomain]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full"
      style={{ backgroundColor: '#0f172a' }}
    />
  );
}