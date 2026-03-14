import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, probeCORS, probeProxy } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';
import {
  Eye, EyeOff, Check, Trash2, Shield,
  Key, Server, Wifi, WifiOff, Loader2, Globe, Box,
  Info, Download, Upload, ArrowLeft,
} from 'lucide-react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useDialogueStore } from '@/lib/store/dialogue';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek', 'custom'];

export function SettingsPage() {
  const navigate = useNavigate();
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const { graphData } = useGraphStore();
  const { progress, history, streak, importData } = useLearningStore();
  const { savedConversations, importConversations } = useDialogueStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [importMessage, setImportMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      const effectiveUrl = resolveBaseUrl(
        llmConfig.baseUrl || PROVIDER_INFO[llmConfig.provider].defaultBase,
        !!llmConfig.useProxy,
      );
      const ok = await probeCORS(effectiveUrl, llmConfig.apiKey, llmConfig.model || 'gpt-4o');
      if (ok) {
        setTestStatus('success');
        setTestMessage(llmConfig.useProxy ? '通过本地代理连接成功 ✨' : '连接成功 ✨ API 可用');
        setTimeout(() => setTestStatus('idle'), 4000);
      } else {
        let errMsg = '连接失败';
        if (llmConfig.useProxy) {
          const alive = await probeProxy();
          errMsg = alive
            ? '代理在运行但 API 返回错误，请检查 URL / Key / 模型名。'
            : '本地代理未运行。请先下载并启动代理脚本。';
        } else {
          errMsg = '连接失败。如果是内网 API，请启用「本地代理」并启动代理脚本。';
        }
        setTestStatus('error');
        setTestMessage(errMsg);
      }
    } catch (err) {
      setTestStatus('error');
      setTestMessage(err instanceof Error ? err.message : '网络错误');
    }
  };

  const info = PROVIDER_INFO[llmConfig.provider];

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-2xl mx-auto px-8 py-10">

        {/* Header with back nav */}
        <div className="mb-10 animate-fade-in">
          <button
            onClick={() => navigate('/graph')}
            className="flex items-center gap-2 text-base mb-4 transition-colors"
            style={{ color: 'var(--color-text-secondary)' }}
            onMouseEnter={(e: React.MouseEvent<HTMLButtonElement>) => (e.currentTarget.style.color = 'var(--color-accent-primary)')}
            onMouseLeave={(e: React.MouseEvent<HTMLButtonElement>) => (e.currentTarget.style.color = 'var(--color-text-secondary)')}
          >
            <ArrowLeft size={20} />
            <span className="font-medium">返回图谱</span>
          </button>
          <h1 className="text-3xl font-bold mb-2">API 设置</h1>
          <p className="text-lg" style={{ color: 'var(--color-text-secondary)' }}>
            配置 LLM 服务以启用对话功能
          </p>
        </div>

        {/* Provider Selection */}
        <div className="mb-8 animate-fade-in stagger-1">
          <label className="text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-secondary)' }}>
            <Server size={14} />
            服务商
          </label>
          <div className="grid grid-cols-4 gap-3">
            {PROVIDERS.map((p) => {
              const pInfo = PROVIDER_INFO[p];
              const isActive = llmConfig.provider === p;
              return (
                <button
                  key={p}
                  onClick={() => setLLMConfig({ provider: p })}
                  className="rounded-md py-3 px-4 text-center transition-all min-h-[48px]"
                  style={{
                    backgroundColor: isActive ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
                    border: isActive ? '1px solid var(--color-accent-primary)' : '1px solid var(--color-border)',
                    color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)',
                  }}
                >
                  <div className="text-[15px] font-semibold">{pInfo.name}</div>
                </button>
              );
            })}
          </div>
          <p className="text-sm mt-3" style={{ color: 'var(--color-text-tertiary)' }}>
            {info.hint}
          </p>
        </div>

        {/* API Key */}
        <div className="mb-7 animate-fade-in stagger-2">
          <label className="text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-secondary)' }}>
            <Key size={14} />
            API Key
          </label>
          <div
            className="flex items-center rounded-md overflow-hidden"
            style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
          >
            <input
              type={showKey ? 'text' : 'password'}
              value={llmConfig.apiKey}
              onChange={(e) => setLLMConfig({ apiKey: e.target.value })}
              placeholder={info.placeholder}
              className="flex-1 bg-transparent px-4 py-3 text-[15px] outline-none font-mono"
              style={{ color: 'var(--color-text-primary)', border: 'none' }}
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="px-4 shrink-0 py-3"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
            {llmConfig.apiKey && (
              <button
                onClick={clearApiKey}
                className="px-3 shrink-0"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Base URL (always shown — gives power users full control) */}
        <div className="mb-7 animate-fade-in stagger-3">
          <label className="text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-secondary)' }}>
            <Globe size={14} />
            API Base URL
          </label>
          <input
            type="text"
            value={llmConfig.baseUrl || ''}
            onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
            placeholder={info.defaultBase || 'https://your-api.example.com/v1'}
            className="w-full rounded-md px-4 py-3 text-[15px] font-mono outline-none"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
            }}
          />
          <p className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
            留空使用默认地址{info.defaultBase ? `（${info.defaultBase}）` : ''}。支持内网 / 代理 / OneAPI 等 OpenAI 兼容接口。
          </p>
        </div>

        {/* Model */}
        <div className="mb-8 animate-fade-in stagger-4">
          <label className="text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: 'var(--color-text-secondary)' }}>
            <Box size={14} />
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
            className="w-full rounded-md px-4 py-3 text-[15px] font-mono outline-none"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
            }}
          />
          <p className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
            留空使用默认模型。自定义服务商必须填写。
          </p>
        </div>

        {/* Action row */}
        <div className="flex gap-3 mb-7 animate-fade-in stagger-5">
          <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-2.5 text-base">
            {saved ? <><Check size={16} /> 已保存</> : '保存配置'}
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
        <div className="card-static p-6 rounded-lg mb-7 animate-fade-in stagger-5">
          <h3 className="text-base font-bold mb-4" style={{ color: 'var(--color-text-primary)' }}>
            使用流程
          </h3>
          <div className="space-y-3">
            {[
              '选择服务商并输入 API Key（自定义需填写 Base URL + 模型名）',
              '回到图谱页面，点击任意知识节点',
              'AI 先讲解概念，然后向你提问，你来解答',
              '对话 4 轮后可请求评估，获得掌握度打分',
            ].map((text, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <span className="text-sm font-mono font-bold mt-px shrink-0" style={{ color: 'var(--color-accent-primary)' }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="text-[15px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                  {text}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* About section */}
        <div className="card-static p-6 rounded-lg mb-7 animate-fade-in stagger-6">
          <div className="flex items-center gap-2.5 mb-4">
            <Info size={16} style={{ color: 'var(--color-accent-primary)' }} />
            <h3 className="text-base font-bold" style={{ color: 'var(--color-text-primary)' }}>关于</h3>
          </div>
          <div className="space-y-3">
            {[
              { label: '版本', value: 'v0.1.0' },
              { label: '知识节点', value: `${totalNodes} 个` },
              { label: '已掌握', value: `${masteredCount} 个` },
              { label: '学习记录', value: `${history.length} 条` },
              { label: '连续学习', value: `${streak.current} 天 (最高 ${streak.longest} 天)` },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between py-1">
                <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>{label}</span>
                <span className="text-sm font-mono font-medium" style={{ color: 'var(--color-text-secondary)' }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Data export & import */}
        <div className="flex gap-3 mb-3 animate-fade-in stagger-6">
          <button
            onClick={() => {
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
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `akg-data-${new Date().toISOString().slice(0, 10)}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
            className="btn-ghost flex-1 flex items-center justify-center gap-2.5 text-base"
          >
            <Download size={18} />
            导出数据
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-ghost flex-1 flex items-center justify-center gap-2.5 text-base"
          >
            <Upload size={18} />
            导入数据
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
                  const partial: Record<string, unknown> = {};
                  if (data.settings.provider) partial.provider = data.settings.provider;
                  if (data.settings.model) partial.model = data.settings.model;
                  if (data.settings.baseUrl) partial.baseUrl = data.settings.baseUrl;
                  if (data.settings.useProxy !== undefined) partial.useProxy = data.settings.useProxy;
                  if (Object.keys(partial).length > 0) {
                    setLLMConfig(partial as any);
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
          <p
            className="text-sm mb-5 rounded-lg px-3.5 py-2.5 animate-fade-in"
            style={{
              color: importStatus === 'success' ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)',
              backgroundColor: importStatus === 'success' ? 'rgba(52,211,153,0.06)' : 'rgba(244,63,94,0.06)',
              border: `1px solid ${importStatus === 'success' ? 'rgba(52,211,153,0.12)' : 'rgba(244,63,94,0.12)'}`,
            }}
          >
            {importMessage}
          </p>
        )}

        {/* Security note */}
        <div
          className="rounded-md px-4 py-3 flex items-start gap-3 animate-fade-in stagger-6"
          style={{ backgroundColor: 'var(--color-tint-emerald)', border: '1px solid rgba(138, 173, 122, 0.1)' }}
        >
          <Shield size={16} className="shrink-0 mt-0.5" style={{ color: 'var(--color-accent-emerald)' }} />
          <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-tertiary)' }}>
            Key 存储在浏览器 localStorage，仅通过加密请求头传递。后端不存储 Key。
          </p>
        </div>

      </div>
    </div>
  );
}