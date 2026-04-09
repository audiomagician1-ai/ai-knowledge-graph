import { useState, useEffect, useCallback } from 'react';
import { FileText, Download, ChevronRight, Award, AlertTriangle, TrendingUp, Flame, Target, BookOpen } from 'lucide-react';
import { type ReportData, StatCard } from '@/components/report/ReportParts';

/**
 * Learning Report Page — comprehensive, printable learning summary.
 * Fetches data from GET /api/analytics/learning-report.
 * Route: /report
 */
export function LearningReportPage() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchReport = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const settings = localStorage.getItem('akg-settings');
      const baseUrl = settings ? JSON.parse(settings)?.apiBaseUrl : '';
      if (!baseUrl) {
        setError('请先在设置中配置 API 地址');
        return;
      }
      const resp = await fetch(`${baseUrl}/api/analytics/learning-report`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      setReport(await resp.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const handleExport = useCallback(() => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `learning-report-${report.generated_at.split(' ')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [report]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <AlertTriangle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
        <p className="text-gray-300">{error || '无法加载报告'}</p>
      </div>
    );
  }

  const { overview: o, streak: s } = report;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8 print:py-2 print:space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FileText className="w-7 h-7 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">学习报告</h1>
            <p className="text-sm text-gray-400">生成于 {report.generated_at}</p>
          </div>
        </div>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg text-sm transition-colors print:hidden"
        >
          <Download className="w-4 h-4" />
          导出 JSON
        </button>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard icon={<BookOpen className="w-5 h-5 text-blue-400" />} label="已掌握" value={o.mastered} sub={`${o.completion_percentage}%`} />
        <StatCard icon={<Target className="w-5 h-5 text-amber-400" />} label="学习中" value={o.learning} sub={`${o.total_sessions} 次评估`} />
        <StatCard icon={<Flame className="w-5 h-5 text-orange-400" />} label="连续学习" value={`${s.current}天`} sub={`最长 ${s.longest}天`} />
        <StatCard icon={<TrendingUp className="w-5 h-5 text-green-400" />} label="平均分" value={o.avg_score} sub={`活跃 ${o.active_days_90d} 天`} />
      </div>

      {/* Domain Breakdown */}
      <section className="bg-white/5 rounded-xl border border-white/10 p-5">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-purple-400" />
          领域进度 ({report.domains_started}/{report.domains_total} 已开始)
        </h2>
        <div className="space-y-3">
          {report.domains.slice(0, 12).map((d) => (
            <div key={d.domain_id} className="flex items-center gap-3">
              <span className="text-sm text-gray-300 w-32 truncate">{d.domain_name}</span>
              <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                  style={{ width: `${Math.min(100, d.percentage)}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 w-16 text-right">{d.mastered}/{d.total}</span>
              <span className="text-xs text-gray-500 w-12 text-right">{d.percentage}%</span>
            </div>
          ))}
        </div>
      </section>

      {/* Strengths */}
      {report.strengths.length > 0 && (
        <section className="bg-green-500/5 rounded-xl border border-green-500/20 p-5">
          <h2 className="text-lg font-semibold text-green-300 mb-3">💪 优势领域</h2>
          <div className="flex flex-wrap gap-2">
            {report.strengths.map((s) => (
              <span key={s.domain_id} className="px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full text-sm text-green-300">
                {s.domain_name} — {s.mastered} 已掌握 ({s.percentage}%)
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Weaknesses */}
      {report.weaknesses.length > 0 && (
        <section className="bg-red-500/5 rounded-xl border border-red-500/20 p-5">
          <h2 className="text-lg font-semibold text-red-300 mb-3">⚠️ 需要巩固 ({report.weaknesses.length})</h2>
          <div className="space-y-2">
            {report.weaknesses.slice(0, 5).map((w) => (
              <div key={w.concept_id} className="flex items-center justify-between bg-white/5 rounded-lg px-3 py-2">
                <span className="text-sm text-gray-300">{w.name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{w.sessions} 次尝试</span>
                  <span className="text-xs text-red-400 font-mono">{w.score}分</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <section className="bg-blue-500/5 rounded-xl border border-blue-500/20 p-5">
          <h2 className="text-lg font-semibold text-blue-300 mb-3">💡 个性化建议</h2>
          <ul className="space-y-2">
            {report.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <ChevronRight className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
