import { useState } from 'react';
import { useSettingsStore, PROVIDER_INFO } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek'];

/**
 * 设置页面 — LLM API Key 配置
 * 无需登录，Key 存储在本地 localStorage
 */
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
    <div className="min-h-dvh" style={{ backgroundColor: '#0f172a' }}>
      {/* Header */}
      <header
        className="flex items-center px-4"
        style={{
          height: '48px',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
        }}
      >
        <h1 className="text-base font-bold" style={{ color: '#f1f5f9' }}>
          ⚙ 设置
        </h1>
      </header>

      <div className="px-4 py-6 space-y-6">
        {/* LLM 配置卡片 */}
        <div
          className="rounded-2xl p-4"
          style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
        >
          <h2 className="text-sm font-semibold mb-1" style={{ color: '#f1f5f9' }}>
            🤖 LLM 配置
          </h2>
          <p className="text-[11px] mb-4" style={{ color: '#94a3b8' }}>
            配置你的 API Key 即可使用费曼对话。Key 仅存储在本地浏览器中，不会上传到服务器。
          </p>

          {/* Provider 选择 */}
          <label className="text-[11px] font-medium mb-1.5 block" style={{ color: '#94a3b8' }}>
            服务商
          </label>
          <div className="flex gap-2 mb-4">
            {PROVIDERS.map((p) => {
              const info = PROVIDER_INFO[p];
              const isActive = llmConfig.provider === p;
              return (
                <button
                  key={p}
                  onClick={() => setLLMConfig({ provider: p })}
                  className="flex-1 rounded-xl py-2.5 text-xs font-medium transition-colors"
                  style={{
                    backgroundColor: isActive ? '#8b5cf6' : '#334155',
                    color: isActive ? '#fff' : '#94a3b8',
                    border: isActive ? '1px solid #8b5cf6' : '1px solid #475569',
                  }}
                >
                  {info.name}
                </button>
              );
            })}
          </div>

          {/* Provider hint */}
          <p className="text-[10px] mb-3" style={{ color: '#64748b' }}>
            💡 {PROVIDER_INFO[llmConfig.provider].hint}
          </p>

          {/* API Key 输入 */}
          <label className="text-[11px] font-medium mb-1.5 block" style={{ color: '#94a3b8' }}>
            API Key
          </label>
          <div className="flex gap-2 mb-2">
            <div className="relative flex-1">
              <input
                type={showKey ? 'text' : 'password'}
                value={llmConfig.apiKey}
                onChange={(e) => setLLMConfig({ apiKey: e.target.value })}
                placeholder={PROVIDER_INFO[llmConfig.provider].placeholder}
                className="w-full rounded-xl px-4 py-3 text-sm outline-none pr-12"
                style={{
                  backgroundColor: '#0f172a',
                  color: '#f1f5f9',
                  border: '1px solid #334155',
                }}
              />
              <button
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs"
                style={{ color: '#64748b' }}
              >
                {showKey ? '隐藏' : '显示'}
              </button>
            </div>
          </div>

          {/* 当前状态 */}
          {llmConfig.apiKey && (
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: '#10b981' }} />
              <span className="text-[11px]" style={{ color: '#10b981' }}>
                已配置: {maskedKey}
              </span>
            </div>
          )}

          {/* 自定义模型（高级） */}
          <details className="mb-4">
            <summary className="text-[11px] cursor-pointer" style={{ color: '#64748b' }}>
              高级选项
            </summary>
            <div className="mt-2">
              <label className="text-[11px] font-medium mb-1 block" style={{ color: '#94a3b8' }}>
                模型名称（可选，留空使用默认）
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
                className="w-full rounded-xl px-4 py-2.5 text-sm outline-none"
                style={{
                  backgroundColor: '#0f172a',
                  color: '#f1f5f9',
                  border: '1px solid #334155',
                }}
              />
            </div>
          </details>

          {/* 操作按钮 */}
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="flex-1 rounded-xl py-2.5 text-sm font-medium"
              style={{ backgroundColor: '#8b5cf6', color: '#fff' }}
            >
              {saved ? '✓ 已保存' : '保存配置'}
            </button>
            {llmConfig.apiKey && (
              <button
                onClick={clearApiKey}
                className="rounded-xl px-4 py-2.5 text-sm font-medium"
                style={{ backgroundColor: '#334155', color: '#94a3b8' }}
              >
                清除
              </button>
            )}
          </div>
        </div>

        {/* 使用说明 */}
        <div
          className="rounded-2xl p-4"
          style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
        >
          <h2 className="text-sm font-semibold mb-2" style={{ color: '#f1f5f9' }}>
            📖 使用说明
          </h2>
          <ul className="space-y-2 text-xs" style={{ color: '#94a3b8' }}>
            <li>1. 选择你的 LLM 服务商并输入 API Key</li>
            <li>2. 回到知识图谱，点击任意节点的"开始学习"</li>
            <li>3. AI 会作为好奇的学生，向你提问来帮你理解概念</li>
            <li>4. 对话 4 轮后可点击"评估"获取理解度打分</li>
          </ul>
          <div
            className="mt-3 rounded-lg p-2.5 text-[11px]"
            style={{ backgroundColor: '#0f172a', border: '1px solid #334155', color: '#64748b' }}
          >
            🔒 API Key 仅存储在浏览器本地 (localStorage)，通过加密请求头发送到后端，后端不保存 Key。
          </div>
        </div>

        {/* 关于 */}
        <div className="text-center text-[11px] py-4" style={{ color: '#475569' }}>
          AI Knowledge Graph v0.2.0 · Phase 2
        </div>
      </div>
    </div>
  );
}