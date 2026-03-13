import { useState } from 'react';
import { useSettingsStore, PROVIDER_INFO } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';
import {
  Eye, EyeOff, Check, Trash2, ChevronDown, Shield,
  Key, Server, Cpu, ExternalLink, Info,
} from 'lucide-react';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek'];

export function SettingsPage() {
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const maskedKey = llmConfig.apiKey
    ? llmConfig.apiKey.slice(0, 8) + '•'.repeat(Math.max(0, llmConfig.apiKey.length - 12)) + llmConfig.apiKey.slice(-4)
    : '';

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-2xl mx-auto px-8 py-8">

        {/* Page header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--color-text-primary)' }}>
            设置
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
            Configure your LLM provider and API credentials
          </p>
        </div>

        {/* LLM Configuration Card */}
        <div className="card-static rounded-2xl overflow-hidden mb-6 animate-fade-in stagger-1">
          {/* Card header */}
          <div
            className="px-6 py-4 flex items-center gap-3"
            style={{
              borderBottom: '1px solid var(--color-border)',
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(139, 92, 246, 0.04))',
            }}
          >
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
              }}
            >
              <Cpu size={16} className="text-white" />
            </div>
            <div>
              <h2 className="text-[15px] font-bold" style={{ color: 'var(--color-text-primary)' }}>
                LLM 配置
              </h2>
              <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>
                配置 API Key 启用费曼对话功能
              </p>
            </div>
          </div>

          <div className="px-6 py-5 space-y-5">
            {/* Provider Selection */}
            <div>
              <label
                className="text-[11px] font-mono font-semibold uppercase tracking-wider mb-3 flex items-center gap-1.5"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <Server size={12} />
                Provider
              </label>
              <div className="grid grid-cols-3 gap-2">
                {PROVIDERS.map((p) => {
                  const info = PROVIDER_INFO[p];
                  const isActive = llmConfig.provider === p;
                  return (
                    <button
                      key={p}
                      onClick={() => setLLMConfig({ provider: p })}
                      className="rounded-xl py-3 px-4 text-left transition-all"
                      style={{
                        backgroundColor: isActive ? 'var(--color-surface-4)' : 'var(--color-surface-3)',
                        border: isActive ? '1px solid var(--color-accent-indigo)' : '1px solid var(--color-border)',
                        boxShadow: isActive ? '0 0 0 1px var(--color-accent-indigo), 0 0 12px var(--color-glow-indigo)' : 'none',
                      }}
                    >
                      <div className="text-[13px] font-semibold mb-0.5" style={{ color: isActive ? 'var(--color-accent-indigo)' : 'var(--color-text-primary)' }}>
                        {info.name}
                      </div>
                      <div className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
                        {p === 'openrouter' ? '多模型路由' : p === 'openai' ? 'GPT 系列' : 'DeepSeek 系列'}
                      </div>
                    </button>
                  );
                })}
              </div>
              <p className="text-[12px] mt-2 flex items-start gap-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
                <Info size={12} className="shrink-0 mt-0.5" />
                {PROVIDER_INFO[llmConfig.provider].hint}
              </p>
            </div>

            {/* API Key Input */}
            <div>
              <label
                className="text-[11px] font-mono font-semibold uppercase tracking-wider mb-3 flex items-center gap-1.5"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <Key size={12} />
                API Key
              </label>
              <div
                className="flex items-center rounded-xl overflow-hidden transition-all"
                style={{
                  backgroundColor: 'var(--color-surface-3)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <input
                  type={showKey ? 'text' : 'password'}
                  value={llmConfig.apiKey}
                  onChange={(e) => setLLMConfig({ apiKey: e.target.value })}
                  placeholder={PROVIDER_INFO[llmConfig.provider].placeholder}
                  className="flex-1 bg-transparent px-4 py-3 text-[14px] outline-none font-mono"
                  style={{ color: 'var(--color-text-primary)', border: 'none' }}
                />
                <button
                  onClick={() => setShowKey(!showKey)}
                  className="px-3 h-full transition-colors"
                  style={{ color: 'var(--color-text-tertiary)' }}
                >
                  {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>

              {/* Key status */}
              {llmConfig.apiKey && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: 'var(--color-accent-emerald)' }} />
                  <span className="text-[12px] font-mono" style={{ color: 'var(--color-accent-emerald)' }}>
                    已配置: {maskedKey}
                  </span>
                </div>
              )}
            </div>

            {/* Advanced: Custom Model */}
            <details className="group">
              <summary
                className="flex items-center gap-2 cursor-pointer select-none"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <ChevronDown size={14} className="transition-transform group-open:rotate-180" />
                <span className="text-[12px] font-medium">高级选项</span>
              </summary>
              <div className="mt-3 pl-6">
                <label
                  className="text-[11px] font-mono font-semibold uppercase tracking-wider mb-2 block"
                  style={{ color: 'var(--color-text-tertiary)' }}
                >
                  Custom Model Override
                </label>
                <input
                  type="text"
                  value={llmConfig.model || ''}
                  onChange={(e) => setLLMConfig({ model: e.target.value })}
                  placeholder={
                    llmConfig.provider === 'openrouter' ? 'openai/gpt-4o' :
                    llmConfig.provider === 'openai' ? 'gpt-4o' :
                    'deepseek-chat'
                  }
                  className="w-full rounded-xl px-4 py-2.5 text-[14px] font-mono outline-none"
                  style={{
                    backgroundColor: 'var(--color-surface-3)',
                    color: 'var(--color-text-primary)',
                    border: '1px solid var(--color-border)',
                  }}
                />
                <p className="text-[11px] mt-1.5" style={{ color: 'var(--color-text-tertiary)' }}>
                  留空使用默认模型
                </p>
              </div>
            </details>

            {/* Action buttons */}
            <div className="flex gap-3 pt-2">
              <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-2">
                {saved ? <><Check size={16} /> 已保存</> : '保存配置'}
              </button>
              {llmConfig.apiKey && (
                <button onClick={clearApiKey} className="btn-ghost flex items-center gap-2 px-5">
                  <Trash2 size={14} />
                  清除
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Usage Guide Card */}
        <div className="card-static rounded-2xl overflow-hidden mb-6 animate-fade-in stagger-2">
          <div className="px-6 py-5">
            <h2 className="text-[15px] font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
              使用说明
            </h2>
            <div className="space-y-3">
              {[
                { step: '01', text: '选择你的 LLM 服务商并输入 API Key' },
                { step: '02', text: '回到知识图谱，点击任意节点的"开始学习"' },
                { step: '03', text: 'AI 会作为好奇的学生，向你提问来帮你理解概念' },
                { step: '04', text: '对话 4 轮后可点击"评估"获取理解度打分' },
              ].map(({ step, text }) => (
                <div key={step} className="flex items-start gap-3">
                  <span
                    className="text-[11px] font-mono font-bold shrink-0 mt-0.5"
                    style={{ color: 'var(--color-accent-indigo)' }}
                  >
                    {step}
                  </span>
                  <span className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                    {text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Security note */}
        <div
          className="rounded-xl px-5 py-4 flex items-start gap-3 animate-fade-in stagger-3"
          style={{
            backgroundColor: 'rgba(52, 211, 153, 0.04)',
            border: '1px solid rgba(52, 211, 153, 0.1)',
          }}
        >
          <Shield size={16} className="shrink-0 mt-0.5" style={{ color: 'var(--color-accent-emerald)' }} />
          <p className="text-[12px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
            API Key 仅存储在浏览器本地 (localStorage)，通过加密请求头发送到后端。后端不保存 Key，仅用于实时代理请求。
          </p>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 pb-4">
          <p className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
            AI Knowledge Graph v0.3.0 · Phase 2 Complete
          </p>
        </div>
      </div>
    </div>
  );
}