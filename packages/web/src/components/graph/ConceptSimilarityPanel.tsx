import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, ArrowRight, Sparkles } from 'lucide-react';

interface SimilarConcept {
  concept_id: string;
  name: string;
  domain_id: string;
  domain_name: string;
  subdomain: string;
  difficulty: number;
  similarity_score: number;
  reasons: string[];
  is_cross_domain: boolean;
}

/**
 * Concept Similarity Panel — shows related concepts based on graph topology + tags.
 * Powered by GET /api/analytics/concept-similarity/{concept_id}.
 */
export function ConceptSimilarityPanel({ conceptId }: { conceptId: string }) {
  const [similar, setSimilar] = useState<SimilarConcept[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!conceptId) return;
    let cancelled = false;
    setLoading(true);

    (async () => {
      try {
        const settings = localStorage.getItem('akg-settings');
        const baseUrl = settings ? JSON.parse(settings)?.apiBaseUrl : '';
        if (!baseUrl) return;
        const resp = await fetch(`${baseUrl}/api/analytics/concept-similarity/${encodeURIComponent(conceptId)}?limit=6`);
        if (resp.ok && !cancelled) {
          const data = await resp.json();
          setSimilar(data.similar || []);
        }
      } catch { /* silent */ } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [conceptId]);

  if (loading) {
    return (
      <div className="bg-white/5 rounded-xl border border-white/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Layers className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-medium text-white">相似概念</span>
        </div>
        <div className="flex justify-center py-4">
          <div className="w-5 h-5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  if (similar.length === 0) return null;

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Layers className="w-4 h-4 text-violet-400" />
        <span className="text-sm font-medium text-white">相似概念</span>
        <span className="text-xs text-gray-500 ml-auto">{similar.length} 个</span>
      </div>
      <div className="space-y-2">
        {similar.map((s) => (
          <button
            key={s.concept_id}
            onClick={() => navigate(`/learn/${s.domain_id}/${s.concept_id}`)}
            className="w-full text-left bg-white/5 hover:bg-white/10 rounded-lg p-3 transition-colors group"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-white">{s.name}</span>
              <div className="flex items-center gap-1.5">
                {s.is_cross_domain && (
                  <Sparkles className="w-3 h-3 text-amber-400" />
                )}
                <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-violet-400 transition-colors" />
              </div>
            </div>
            <div className="text-xs text-gray-400">{s.domain_name} · 难度 {s.difficulty}</div>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {s.reasons.slice(0, 3).map((r, i) => (
                <span key={i} className="px-1.5 py-0.5 bg-violet-500/10 text-violet-300 text-[10px] rounded">
                  {r}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
