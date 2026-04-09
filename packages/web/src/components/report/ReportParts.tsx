export interface ReportData {
  generated_at: string;
  overview: {
    total_concepts_available: number;
    mastered: number;
    learning: number;
    not_started: number;
    completion_percentage: number;
    total_sessions: number;
    avg_score: number;
    active_days_90d: number;
  };
  streak: { current: number; longest: number };
  domains: Array<{
    domain_id: string;
    domain_name: string;
    mastered: number;
    learning: number;
    total: number;
    percentage: number;
    avg_score: number;
    total_sessions: number;
  }>;
  strengths: Array<{ domain_id: string; domain_name: string; percentage: number; mastered: number }>;
  weaknesses: Array<{ concept_id: string; name: string; domain_id: string; score: number; sessions: number }>;
  recommendations: string[];
  domains_started: number;
  domains_total: number;
}

export function StatCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string | number; sub: string }) {
  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-4 flex flex-col gap-2">
      <div className="flex items-center gap-2">{icon}<span className="text-xs text-gray-400">{label}</span></div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <span className="text-xs text-gray-500">{sub}</span>
    </div>
  );
}
