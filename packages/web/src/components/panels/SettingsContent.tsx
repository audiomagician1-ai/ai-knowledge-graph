import { useState } from 'react';
import { useSettingsStore, PROVIDER_INFO, getLLMHeaders } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';
import { Eye, EyeOff, Check, Trash2, Shield, Key, Server, Cpu, Wifi, WifiOff, Loader2, Globe, Box, Info, Download } from 'lucide-react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek', 'custom'];

export function SettingsContent() {
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const { graphData } = useGraphStore();
  const { progress, history, streak } = useLearningStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };

  const handleTestConnection = async () => {
    if (!llmConfig.apiKey) { setTestStatus('error'); setTestMessage('请先输入 API Key'); return; }
    setTestStatus('testing'); setTestMessage('');
    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
      const res = await fetch(`${API_BASE}/dialogue/conversations`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
        body: JSON.stringify({ concept_id: 'prompt-basics' }),
      });
      if (res.ok) { setTestStatus('success'); setTestMessage('连接成功'); setTimeout(() => setTestStatus('idle'), 4000); }
      else { const d = await res.json().catch(() => ({})); setTestStatus('error'); setTestMessage(d.detail || `HTTP ${res.status}`); }
    } catch (err) { setTestStatus('error'); setTestMessage(err instanceof Error ? err.message : '网络错误'); }
  };

  const info = PROVIDER_INFO[llmConfig.provider];

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Provider */}
      <div>
        <label className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, display: 'flex' }}>
          <Server size={12} /> 服务商
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
          {PROVIDERS.map((p) => {
            const pInfo = PROVIDER_INFO[p];
            const isActive = llmConfig.provider === p;
            return (
              <button key={p} onClick={() => setLLMConfig({ provider: p })}
                style={{
                  borderRadius: 10, padding: '10px 8px', textAlign: 'center', fontSize: 13, fontWeight: 500,
                  backgroundColor: isActive ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
                  border: isActive ? '1.5px solid var(--color-accent-primary)' : '1px solid transparent',
                  color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}>
                {pInfo.name}
              </button>
            );
          })}
        </div>
        <p style={{ color: 'var(--color-text-tertiary)', fontSize: 12, marginTop: 8, lineHeight: 1.5 }}>{info.hint}</p>
      </div>

      {/* API Key */}
      <div>
        <label className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, display: 'flex' }}>
          <Key size={12} /> API Key
        </label>
        <div className="flex items-center overflow-hidden" style={{ borderRadius: 10, backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}>
          <input type={showKey ? 'text' : 'password'} value={llmConfig.apiKey}
            onChange={(e) => setLLMConfig({ apiKey: e.target.value })} placeholder={info.placeholder}
            className="flex-1 bg-transparent outline-none font-mono" style={{ padding: '12px 16px', fontSize: 13, color: 'var(--color-text-primary)', border: 'none' }} />
          <button onClick={() => setShowKey(!showKey)} style={{ padding: '0 14px', flexShrink: 0, color: 'var(--color-text-tertiary)', cursor: 'pointer', background: 'none', border: 'none' }}>
            {showKey ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
          {llmConfig.apiKey && <button onClick={clearApiKey} style={{ padding: '0 14px', flexShrink: 0, color: 'var(--color-text-tertiary)', cursor: 'pointer', background: 'none', border: 'none' }}><Trash2 size={15} /></button>}
        </div>
      </div>

      {/* Base URL */}
      <div>
        <label className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, display: 'flex' }}>
          <Globe size={12} /> API Base URL
        </label>
        <input type="text" value={llmConfig.baseUrl || ''} onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
          placeholder={info.defaultBase || 'https://your-api.example.com/v1'}
          className="w-full outline-none font-mono"
          style={{ borderRadius: 10, padding: '12px 16px', fontSize: 13, backgroundColor: 'var(--color-surface-2)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)' }} />
      </div>

      {/* Model */}
      <div>
        <label className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, display: 'flex' }}>
          <Box size={12} /> 模型名称
        </label>
        <input type="text" value={llmConfig.model || ''}
          onChange={(e) => setLLMConfig({ model: e.target.value })}
          placeholder={llmConfig.provider === 'openrouter' ? 'openai/gpt-4o' : llmConfig.provider === 'openai' ? 'gpt-4o' : llmConfig.provider === 'deepseek' ? 'deepseek-chat' : 'model-name'}
          className="w-full outline-none font-mono"
          style={{ borderRadius: 10, padding: '12px 16px', fontSize: 13, backgroundColor: 'var(--color-surface-2)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)' }} />
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-2" style={{ borderRadius: 10, padding: '12px 0', fontSize: 14 }}>
          {saved ? <><Check size={14} /> 已保存</> : '保存配置'}
        </button>
        {llmConfig.apiKey && (
          <button onClick={handleTestConnection} disabled={testStatus === 'testing'}
            className="btn-ghost flex items-center gap-1.5" style={{ borderRadius: 10, padding: '12px 16px', fontSize: 13, color: testStatus === 'success' ? 'var(--color-accent-emerald)' : testStatus === 'error' ? 'var(--color-accent-rose)' : undefined }}>
            {testStatus === 'testing' ? <Loader2 size={13} className="animate-spin" /> : testStatus === 'success' ? <Wifi size={13} /> : testStatus === 'error' ? <WifiOff size={13} /> : <Wifi size={13} />}
            {testStatus === 'testing' ? '测试...' : testStatus === 'success' ? '可用' : testStatus === 'error' ? '失败' : '测试'}
          </button>
        )}
      </div>

      {testMessage && testStatus !== 'idle' && (
        <p className="text-xs rounded-xl px-3.5 py-2.5" style={{
          color: testStatus === 'success' ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)',
          backgroundColor: testStatus === 'success' ? 'rgba(138,173,122,0.06)' : 'rgba(201,123,123,0.06)',
        }}>{testMessage}</p>
      )}

      {/* About */}
      <div style={{ borderRadius: 10, padding: '16px 20px', backgroundColor: 'var(--color-surface-2)' }}>
        <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
          <Info size={13} style={{ color: 'var(--color-accent-primary)' }} />
          <span style={{ fontSize: 13, fontWeight: 600 }}>关于</span>
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

      {/* Export */}
      <button onClick={() => {
        const data = { progress, history, streak, exportedAt: new Date().toISOString() };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob); const a = document.createElement('a');
        a.href = url; a.download = `akg-data-${new Date().toISOString().slice(0, 10)}.json`; a.click(); URL.revokeObjectURL(url);
      }} className="btn-ghost w-full flex items-center justify-center gap-2" style={{ borderRadius: 10, padding: '12px 0', fontSize: 13 }}>
        <Download size={14} /> 导出数据
      </button>

      {/* Security */}
      <div className="flex items-start gap-3" style={{ borderRadius: 10, padding: '14px 18px', backgroundColor: 'var(--color-tint-emerald)' }}>
        <Shield size={13} className="shrink-0" style={{ marginTop: 1, color: 'var(--color-accent-emerald)' }} />
        <p style={{ fontSize: 12, lineHeight: 1.6, color: 'var(--color-text-tertiary)' }}>
          Key 仅存在浏览器本地，不会发送到后端。
        </p>
      </div>
    </div>
  );
}
