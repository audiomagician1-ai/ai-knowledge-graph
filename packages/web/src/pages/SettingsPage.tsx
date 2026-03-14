import { useState } from 'react';
import { useSettingsStore, PROVIDER_INFO, getLLMHeaders } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';
import {
  Eye, EyeOff, Check, Trash2, Shield,
  Key, Server, Cpu, Wifi, WifiOff, Loader2, Globe, Box,
  Info, Download, Network,
} from 'lucide-react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek', 'custom'];

export function SettingsPage() {
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const { graphData } = useGraphStore();
  const { progress, history, streak } = useLearningStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTestConnection = async () => {
    if (!llmConfig.apiKey) {
      setTestStatus('error');
      setTestMessage('请先输入 API Key');
      return;
    }
    setTestStatus('testing');
    setTestMessage('');
    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
      const res = await fetch(`${API_BASE}/dialogue/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
        body: JSON.stringify({ concept_id: 'prompt-basics' }),
      });
      if (res.ok) {
        setTestStatus('success');
        setTestMessage('连接成功，API 可用');
        setTimeout(() => setTestStatus('idle'), 4000);
      } else {
        const data = await res.json().catch(() => ({}));
        setTestStatus('error');
        setTestMessage(data.detail || `HTTP ${res.status}`);
      }
    } catch (err) {
      setTestStatus('error');
      setTestMessage(err instanceof Error ? err.message : '网络错误');
    }
  };

  const info = PROVIDER_INFO[llmConfig.provider];

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-xl font-semibold mb-1">API 设置</h1>
          <p className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>
            配置 LLM 服务以启用对话功能
          </p>
        </div>

        {/* Provider Selection */}
        <div className="mb-6 animate-fade-in stagger-1">
          <label className="text-[11px] font-mono font-medium uppercase tracking-wider mb-2.5 flex items-center gap-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            <Server size={11} />
            服务商
          </label>
          <div className="grid grid-cols-4 gap-2">
            {PROVIDERS.map((p) => {
              const pInfo = PROVIDER_INFO[p];
              const isActive = llmConfig.provider === p;
              return (
                <button
                  key={p}
                  onClick={() => setLLMConfig({ provider: p })}
                  className="rounded-lg py-2.5 px-3 text-center transition-all"
                  style={{
                    backgroundColor: isActive ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
                    border: isActive ? '1px solid var(--color-accent-primary)' : '1px solid var(--color-border)',
                    color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)',
                  }}
                >
                  <div className="text-[13px] font-semibold">{pInfo.name}</div>
                </button>
              );
            })}
          </div>
          <p className="text-[12px] mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
            {info.hint}
          </p>
        </div>

        {/* API Key */}
        <div className="mb-5 animate-fade-in stagger-2">
          <label className="text-[11px] font-mono font-medium uppercase tracking-wider mb-2.5 flex items-center gap-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            <Key size={11} />
            API Key
          </label>
          <div
            className="flex items-center rounded-lg overflow-hidden"
            style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
          >
            <input
              type={showKey ? 'text' : 'password'}
              value={llmConfig.apiKey}
              onChange={(e) => setLLMConfig({ apiKey: e.target.value })}
              placeholder={info.placeholder}
              className="flex-1 bg-transparent px-3.5 py-2.5 text-[13px] outline-none font-mono"
              style={{ color: 'var(--color-text-primary)', border: 'none' }}
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="px-3 shrink-0"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
            {llmConfig.apiKey && (
              <button
                onClick={clearApiKey}
                className="px-3 shrink-0"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Base URL (always shown — gives power users full control) */}
        <div className="mb-5 animate-fade-in stagger-3">
          <label className="text-[11px] font-mono font-medium uppercase tracking-wider mb-2.5 flex items-center gap-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            <Globe size={11} />
            API Base URL
          </label>
          <input
            type="text"
            value={llmConfig.baseUrl || ''}
            onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
            placeholder={info.defaultBase || 'https://your-api.example.com/v1'}
            className="w-full rounded-lg px-3.5 py-2.5 text-[13px] font-mono outline-none"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
            }}
          />
          <p className="text-[11px] mt-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            留空使用默认地址{info.defaultBase ? `（${info.defaultBase}）` : ''}。支持内网 / 代理 / OneAPI 等 OpenAI 兼容接口。
          </p>
        </div>

        {/* Model */}
        <div className="mb-6 animate-fade-in stagger-4">
          <label className="text-[11px] font-mono font-medium uppercase tracking-wider mb-2.5 flex items-center gap-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            <Box size={11} />
            模型名称
          </label>
          <input
            type="text"
            value={llmConfig.model || ''}
            onChange={(e) => setLLMConfig({ model: e.target.value })}
            placeholder={
              llmConfig.provider === 'openrouter' ? 'openai/gpt-4o' :
              llmConfig.provider === 'openai' ? 'gpt-4o' :
              llmConfig.provider === 'deepseek' ? 'deepseek-chat' :
              'your-model-name'
            }
            className="w-full rounded-lg px-3.5 py-2.5 text-[13px] font-mono outline-none"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
            }}
          />
          <p className="text-[11px] mt-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
            留空使用默认模型。自定义服务商必须填写。
          </p>
        </div>

        {/* Action row */}
        <div className="flex gap-2.5 mb-5 animate-fade-in stagger-5">
          <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-2">
            {saved ? <><Check size={14} /> 已保存</> : '保存配置'}
          </button>
          {llmConfig.apiKey && (
            <button
              onClick={handleTestConnection}
              disabled={testStatus === 'testing'}
              className="btn-ghost flex items-center gap-2 px-4"
              style={{
                color: testStatus === 'success' ? 'var(--color-accent-emerald)'
                  : testStatus === 'error' ? 'var(--color-accent-rose)'
                  : undefined,
              }}
            >
              {testStatus === 'testing' ? <Loader2 size={14} className="animate-spin" />
                : testStatus === 'success' ? <Wifi size={14} />
                : testStatus === 'error' ? <WifiOff size={14} />
                : <Wifi size={14} />}
              {testStatus === 'testing' ? '测试...'
                : testStatus === 'success' ? '可用'
                : testStatus === 'error' ? '失败'
                : '测试连接'}
            </button>
          )}
        </div>

        {testMessage && testStatus !== 'idle' && (
          <p
            className="text-[12px] mb-5 rounded-lg px-3.5 py-2.5"
            style={{
              color: testStatus === 'success' ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)',
              backgroundColor: testStatus === 'success' ? 'rgba(52,211,153,0.06)' : 'rgba(244,63,94,0.06)',
              border: `1px solid ${testStatus === 'success' ? 'rgba(52,211,153,0.12)' : 'rgba(244,63,94,0.12)'}`,
            }}
          >
            {testMessage}
          </p>
        )}

        {/* How to use */}
        <div className="card-static p-5 mb-5 animate-fade-in stagger-5">
          <h3 className="text-[13px] font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>
            使用流程
          </h3>
          <div className="space-y-2">
            {[
              '选择服务商并输入 API Key（自定义需填写 Base URL + 模型名）',
              '回到图谱页面，点击任意知识节点',
              'AI 先讲解概念，然后向你提问，你来解答',
              '对话 4 轮后可请求评估，获得掌握度打分',
            ].map((text, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <span className="text-[11px] font-mono font-bold mt-px shrink-0" style={{ color: 'var(--color-accent-primary)' }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                  {text}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* About section */}
        <div className="card-static p-5 mb-5 animate-fade-in stagger-6">
          <div className="flex items-center gap-2 mb-3">
            <Info size={13} style={{ color: 'var(--color-accent-primary)' }} />
            <h3 className="text-[13px] font-semibold" style={{ color: 'var(--color-text-primary)' }}>关于</h3>
          </div>
          <div className="space-y-2">
            {[
              { label: '版本', value: 'v0.1.0' },
              { label: '知识节点', value: `${totalNodes} 个` },
              { label: '已掌握', value: `${masteredCount} 个` },
              { label: '学习记录', value: `${history.length} 条` },
              { label: '连续学习', value: `${streak.current} 天 (最高 ${streak.longest} 天)` },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>{label}</span>
                <span className="text-[12px] font-mono" style={{ color: 'var(--color-text-secondary)' }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Data export */}
        <button
          onClick={() => {
            const data = { progress, history, streak, exportedAt: new Date().toISOString() };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `akg-learning-data-${new Date().toISOString().slice(0, 10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="btn-ghost w-full flex items-center justify-center gap-2 mb-5 animate-fade-in stagger-6"
        >
          <Download size={14} />
          导出学习数据
        </button>

        {/* Security note */}
        <div
          className="rounded-lg px-4 py-3 flex items-start gap-2.5 animate-fade-in stagger-6"
          style={{ backgroundColor: 'rgba(52, 211, 153, 0.04)', border: '1px solid rgba(52, 211, 153, 0.08)' }}
        >
          <Shield size={13} className="shrink-0 mt-0.5" style={{ color: 'var(--color-accent-emerald)' }} />
          <p className="text-[11px] leading-relaxed" style={{ color: 'var(--color-text-tertiary)' }}>
            Key 存储在浏览器 localStorage，仅通过加密请求头传递。后端不存储 Key。
          </p>
        </div>

      </div>
    </div>
  );
}