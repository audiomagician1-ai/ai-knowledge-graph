import { useRef, useState } from 'react';
import { Download, Upload, Shield, Info } from 'lucide-react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useSettingsStore, PROVIDER_INFO, getDefaultModel } from '@/lib/store/settings';
import type { LLMConfig } from '@/lib/store/settings';

declare const __BUILD_HASH__: string;

export function SettingsDataIO() {
  const { llmConfig, setLLMConfig } = useSettingsStore();
  const isUsingDefault = useSettingsStore((s) => s.isUsingDefaultLLM());
  const { graphData } = useGraphStore();
  const { progress, history, streak, importData } = useLearningStore();
  const { savedConversations, importConversations } = useDialogueStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [importMessage, setImportMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <>
      {/* About */}
      <div style={{ borderRadius: 10, padding: '16px 20px', backgroundColor: 'var(--color-surface-2)' }}>
        <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
          <Info size={13} style={{ color: 'var(--color-accent-primary)' }} />
          <span className="text-sm font-semibold">关于</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            { label: '版本', value: 'v0.1.0' },
            { label: '知识节点', value: `${totalNodes}` },
            { label: '已掌握', value: `${masteredCount}` },
            { label: '学习记录', value: `${history.length}` },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between text-sm">
              <span style={{ color: 'var(--color-text-tertiary)' }}>{label}</span>
              <span className="font-mono" style={{ color: 'var(--color-text-secondary)' }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Export & Import */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button onClick={() => {
          const data = {
            version: 1,
            progress,
            history,
            streak,
            conversations: savedConversations,
            settings: {
              provider: llmConfig.provider,
              model: llmConfig.model || '',
              baseUrl: llmConfig.baseUrl || '',
              useProxy: llmConfig.useProxy ?? false,
            },
            exportedAt: new Date().toISOString(),
          };
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob); const a = document.createElement('a');
          a.href = url; a.download = `akg-data-${new Date().toISOString().slice(0, 10)}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 10_000);
        }} className="btn-ghost flex-1 flex items-center justify-center gap-2 rounded-xl py-3 text-sm">
          <Download size={14} /> 导出
        </button>
        <button onClick={() => fileInputRef.current?.click()}
          className="btn-ghost flex-1 flex items-center justify-center gap-2 rounded-xl py-3 text-sm">
          <Upload size={14} /> 导入
        </button>
        <input ref={fileInputRef} type="file" accept=".json" style={{ display: 'none' }} onChange={(e) => {
          const file = e.target.files?.[0];
          if (!file) return;
          const reader = new FileReader();
          reader.onload = (ev) => {
            try {
              const data = JSON.parse(ev.target?.result as string);
              if (!data || typeof data !== 'object') throw new Error('无效的数据格式');
              const results: string[] = [];
              if (data.progress || data.history || data.streak) {
                const { imported, merged } = importData({ progress: data.progress, history: data.history, streak: data.streak });
                results.push(`学习进度: ${imported} 新增, ${merged} 更新`);
              }
              if (data.conversations && Array.isArray(data.conversations)) {
                const { imported } = importConversations(data.conversations);
                results.push(`对话记录: ${imported} 条导入`);
              }
              if (data.settings) {
                const partial: Partial<LLMConfig> = {};
                if (data.settings.provider) partial.provider = data.settings.provider;
                if (data.settings.model) partial.model = data.settings.model;
                if (data.settings.baseUrl) partial.baseUrl = data.settings.baseUrl;
                if (data.settings.useProxy !== undefined) partial.useProxy = data.settings.useProxy;
                if (Object.keys(partial).length > 0) {
                  setLLMConfig(partial);
                  results.push('设置已恢复（API Key 需手动输入）');
                }
              }
              setImportStatus('success');
              setImportMessage(results.length > 0 ? results.join('；') : '无可导入的数据');
              setTimeout(() => setImportStatus('idle'), 5000);
            } catch (err) {
              setImportStatus('error');
              setImportMessage(err instanceof Error ? err.message : '导入失败');
              setTimeout(() => setImportStatus('idle'), 5000);
            }
          };
          reader.readAsText(file);
          e.target.value = '';
        }} />
      </div>

      {importStatus !== 'idle' && (
        <p className="text-xs rounded-xl px-3.5 py-2.5" style={{
          color: importStatus === 'success' ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)',
          backgroundColor: importStatus === 'success' ? 'rgba(138,173,122,0.06)' : 'rgba(201,123,123,0.06)',
        }}>{importMessage}</p>
      )}

      {/* Security */}
      <div className="flex items-start gap-3" style={{ borderRadius: 10, padding: '14px 18px', backgroundColor: 'var(--color-tint-emerald)' }}>
        <Shield size={13} className="shrink-0" style={{ marginTop: 1, color: 'var(--color-accent-emerald)' }} />
        <p className="text-xs leading-relaxed text-[var(--color-text-tertiary)]">
          {isUsingDefault
            ? '免费服务由服务器代理调用，你的浏览器不会接触 API Key。'
            : `Key 仅存在浏览器本地。${llmConfig.useProxy ? '本地代理模式下，请求通过本机代理转发，不经过任何外部服务器。' : '直连模式下，请求直接从浏览器发往 LLM API。'}`}
        </p>
      </div>

      {/* Build Info */}
      <div className="text-center" style={{ paddingTop: 8 }}>
        <p className="text-[11px] text-[var(--color-text-quaternary)]">
          AI知识图谱 v0.1.0 · Build {typeof __BUILD_HASH__ !== 'undefined' ? __BUILD_HASH__ : 'dev'}
        </p>
      </div>
    </>
  );
}
