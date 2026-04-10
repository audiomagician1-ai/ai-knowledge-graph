/**
 * PortfolioExportWidget — Learning portfolio preview with Markdown/JSON export.
 * V4.3: Fetches comprehensive portfolio data (skills radar, milestones, timeline)
 * and provides download buttons for sharing/resume use.
 */
import { useState, useEffect, useCallback } from 'react';
import { Briefcase, Download, FileText, FileJson, TrendingUp, Award } from 'lucide-react';

interface SkillRadar {
  domain_id: string; domain_name: string; icon: string;
  mastered: number; total: number; mastery_pct: number; avg_score: number;
}
interface Milestone {
  type: string; label: string; value: string | number; date?: string;
}
interface PortfolioData {
  skills_radar: SkillRadar[];
  milestones: Milestone[];
  strengths: string[];
  growth_areas: string[];
  overview: {
    total_concepts: number; total_mastered: number; domains_explored: number;
    mastery_pct: number; total_domains: number; avg_score: number;
    current_streak: number; longest_streak: number; learning_days: number;
  };
  timeline: { first_activity: number; last_activity: number; total_days: number; total_sessions: number };
}

function downloadFile(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

function toMarkdown(d: PortfolioData): string {
  const lines = ['# 🧠 学习档案\n'];
  const o = d.overview;
  lines.push(`## 概览\n- 掌握概念: **${o.total_mastered}** / ${o.total_concepts} (${o.mastery_pct}%)`);
  lines.push(`- 活跃领域: ${o.domains_explored} / ${o.total_domains}`);
  lines.push(`- 学习天数: ${o.learning_days}\n`);
  if (d.skills_radar.length) {
    lines.push('## 技能雷达\n| 领域 | 掌握度 | 均分 |\n|------|--------|------|');
    d.skills_radar.slice(0, 12).forEach(s =>
      lines.push(`| ${s.icon} ${s.domain_name} | ${s.mastery_pct}% (${s.mastered}/${s.total}) | ${s.avg_score} |`));
    lines.push('');
  }
  if (d.strengths.length) lines.push(`## 💪 强项\n${d.strengths.map(s => `- ${s}`).join('\n')}\n`);
  if (d.growth_areas.length) lines.push(`## 📈 成长空间\n${d.growth_areas.map(s => `- ${s}`).join('\n')}\n`);
  if (d.milestones.length) {
    lines.push('## 🏆 里程碑\n');
    d.milestones.slice(0, 10).forEach(m => lines.push(`- **${m.label}**: ${m.value}`));
  }
  lines.push(`\n---\n*导出于 ${new Date().toLocaleDateString('zh-CN')}*`);
  return lines.join('\n');
}

export function PortfolioExportWidget() {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetch('/api/learning/portfolio')
      .then(r => r.ok ? r.json() : null)
      .then(d => d?.portfolio && setData(d.portfolio))
      .catch(() => {});
  }, []);

  const exportMd = useCallback(() => {
    if (!data) return;
    setExporting(true);
    downloadFile(toMarkdown(data), 'learning-portfolio.md', 'text/markdown');
    setTimeout(() => setExporting(false), 500);
  }, [data]);

  const exportJson = useCallback(() => {
    if (!data) return;
    setExporting(true);
    downloadFile(JSON.stringify(data, null, 2), 'learning-portfolio.json', 'application/json');
    setTimeout(() => setExporting(false), 500);
  }, [data]);

  if (!data) return null;

  const o = data.overview;
  const topSkills = data.skills_radar.filter(s => s.mastery_pct > 0).slice(0, 5);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Briefcase size={16} className="text-indigo-400" />
        <h3 className="text-sm font-semibold">学习档案</h3>
        <div className="ml-auto flex gap-1">
          <button onClick={exportMd} disabled={exporting} title="导出 Markdown"
            className="p-1 hover:bg-white/10 rounded transition-colors disabled:opacity-30">
            <FileText size={14} className="text-blue-400" />
          </button>
          <button onClick={exportJson} disabled={exporting} title="导出 JSON"
            className="p-1 hover:bg-white/10 rounded transition-colors disabled:opacity-30">
            <FileJson size={14} className="text-amber-400" />
          </button>
        </div>
      </div>

      {/* Overview grid */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-emerald-400">{o.total_mastered}</div>
          <div className="text-[10px] opacity-40">已掌握</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{o.domains_explored}</div>
          <div className="text-[10px] opacity-40">活跃领域</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{o.mastery_pct}%</div>
          <div className="text-[10px] opacity-40">总掌握度</div>
        </div>
      </div>

      {/* Top skills */}
      {topSkills.length > 0 && (
        <div className="space-y-1.5 mb-3">
          {topSkills.map(s => (
            <div key={s.domain_id} className="flex items-center gap-2">
              <span className="text-xs w-28 truncate">{s.icon} {s.domain_name}</span>
              <div className="flex-1 bg-white/10 rounded-full h-1.5">
                <div className="h-full rounded-full bg-indigo-400"
                  style={{ width: `${Math.min(s.mastery_pct, 100)}%` }} />
              </div>
              <span className="text-[10px] opacity-50 w-10 text-right">{s.mastery_pct}%</span>
            </div>
          ))}
        </div>
      )}

      {/* Strengths & Growth */}
      <div className="flex gap-2 text-[10px]">
        {data.strengths.length > 0 && (
          <div className="flex items-start gap-1 flex-1 bg-emerald-500/10 rounded-lg p-1.5">
            <Award size={10} className="text-emerald-400 mt-0.5 shrink-0" />
            <span className="opacity-60 line-clamp-2">{data.strengths.slice(0, 2).join('、')}</span>
          </div>
        )}
        {data.growth_areas.length > 0 && (
          <div className="flex items-start gap-1 flex-1 bg-amber-500/10 rounded-lg p-1.5">
            <TrendingUp size={10} className="text-amber-400 mt-0.5 shrink-0" />
            <span className="opacity-60 line-clamp-2">{data.growth_areas.slice(0, 2).join('、')}</span>
          </div>
        )}
      </div>
    </div>
  );
}
