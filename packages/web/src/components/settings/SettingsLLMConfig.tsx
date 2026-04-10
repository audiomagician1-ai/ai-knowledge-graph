import { useState } from 'react';
import {
  Eye, EyeOff, Check, Trash2, Key, Server, Wifi, WifiOff,
  Loader2, Globe, Box, MonitorDown,
} from 'lucide-react';
import {
  PROVIDER_INFO, resolveBaseUrl, probeCORS, probeProxy,
  validateModelId, getDefaultModel,
} from '@/lib/store/settings';
import type { LLMProvider, LLMConfig } from '@/lib/store/settings';
import { SettingsProxyActions } from './SettingsProxyGuide';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek', 'custom'];

interface SettingsLLMConfigProps {
  llmConfig: LLMConfig;
  setLLMConfig: (partial: Partial<LLMConfig>) => void;
  clearApiKey: () => void;
  onCollapse: () => void;
}

export function SettingsLLMConfig({ llmConfig, setLLMConfig, clearApiKey, onCollapse }: SettingsLLMConfigProps) {
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const [showProxyGuide, setShowProxyGuide] = useState(false);

  const info = PROVIDER_INFO[llmConfig.provider];

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };

  const handleTestConnection = async () => {
    if (!llmConfig.apiKey) { setTestStatus('error'); setTestMessage('请先输入 API Key'); return; }
    setTestStatus('testing'); setTestMessage('正在连接，请稍候…');
    try {
      const effectiveUrl = resolveBaseUrl(
        llmConfig.baseUrl || PROVIDER_INFO[llmConfig.provider].defaultBase,
        !!llmConfig.useProxy,
      );
      const testModel = llmConfig.model || getDefaultModel(llmConfig.provider);
      const result = await probeCORS(effectiveUrl, llmConfig.apiKey, testModel);
      if (result.ok) {
        setTestStatus('success');
        setTestMessage(llmConfig.useProxy ? '通过本地代理连接成功' : '连接成功');
        setTimeout(() => setTestStatus('idle'), 4000);
        return;
      }
      let errMsg = result.detail ? `连接失败: ${result.detail}` : '连接失败';
      if (llmConfig.useProxy) {
        const alive = await probeProxy();
        errMsg = alive
          ? `代理在运行但 API 返回错误${result.detail ? ` (${result.detail})` : ''}，请检查 URL / Key / 模型名。`
          : '本地代理未运行。请先下载并启动代理脚本。';
      } else {
        errMsg = `连接失败${result.detail ? `: ${result.detail}` : ''}。如果是内网 API，请启用「本地代理」并启动代理脚本。`;
      }
      setTestStatus('error');
      setTestMessage(errMsg);
      setTimeout(() => setTestStatus('idle'), 6000);
    } catch (err) {
      setTestStatus('error');
      setTestMessage(err instanceof Error ? err.message : '网络错误');
      setTimeout(() => setTestStatus('idle'), 6000);
    }
  };

  return (
    <>
      {/* Provider */}
      <div>
        <label className="form-label">
          <Server size={12} /> 服务商
        </label>
        <div className="grid grid-cols-4 gap-2">
          {PROVIDERS.map((p) => {
            const pInfo = PROVIDER_INFO[p];
            const isActive = llmConfig.provider === p;
            return (
              <button key={p} onClick={() => setLLMConfig({ provider: p })}
                className={`rounded-xl py-2.5 px-2 text-center text-sm font-medium cursor-pointer transition-all ${isActive ? 'bg-[var(--color-surface-3)] border-[1.5px] border-[var(--color-accent-primary)] text-[var(--color-accent-primary)]' : 'bg-[var(--color-surface-2)] border border-transparent text-[var(--color-text-secondary)]'}`}>
                {pInfo.name}
              </button>
            );
          })}
        </div>
        <p className="text-xs mt-2 leading-normal text-[var(--color-text-tertiary)]">{info.hint}</p>
      </div>

      {/* API Key */}
      <div>
        <label className="form-label">
          <Key size={12} /> API Key
        </label>
        <div className="flex items-center overflow-hidden rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)]">
          <input type={showKey ? 'text' : 'password'} value={llmConfig.apiKey}
            onChange={(e) => setLLMConfig({ apiKey: e.target.value })} placeholder={info.placeholder}
            className="flex-1 bg-transparent outline-none font-mono py-3 px-4 text-sm text-[var(--color-text-primary)] border-none" />
          <button onClick={() => setShowKey(!showKey)} style={{ padding: '0 14px', flexShrink: 0, color: 'var(--color-text-tertiary)', cursor: 'pointer', background: 'none', border: 'none' }}>
            {showKey ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
          {llmConfig.apiKey && <button onClick={() => { clearApiKey(); onCollapse(); }} style={{ padding: '0 14px', flexShrink: 0, color: 'var(--color-text-tertiary)', cursor: 'pointer', background: 'none', border: 'none' }}><Trash2 size={15} /></button>}
        </div>
      </div>

      {/* Base URL */}
      <div>
        <label className="form-label">
          <Globe size={12} /> API Base URL
        </label>
        <input type="text" value={llmConfig.baseUrl || ''} onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
          placeholder={info.defaultBase || 'https://your-api.example.com/v1'}
          className="form-input font-mono" />
      </div>

      {/* Model */}
      <div>
        <label className="form-label">
          <Box size={12} /> 模型名称
        </label>
        <input type="text" value={llmConfig.model || ''}
          onChange={(e) => setLLMConfig({ model: e.target.value })}
          placeholder={llmConfig.provider === 'openrouter' ? 'openai/gpt-4o' : llmConfig.provider === 'openai' ? 'gpt-4o' : llmConfig.provider === 'deepseek' ? 'deepseek-chat' : 'model-name'}
          className="form-input font-mono" />
        {info.modelHint && (
          <p className="text-[11px] mt-1.5 leading-normal text-[var(--color-text-tertiary)]">{info.modelHint}</p>
        )}
        {(() => { const warn = validateModelId(llmConfig.provider, llmConfig.model || ''); return warn ? (
          <p className="text-[11px] mt-1 leading-normal text-[var(--color-accent-rose)]">⚠️ {warn}</p>
        ) : null; })()}
      </div>

      {/* Local Proxy Toggle */}
      <div style={{ borderRadius: 10, padding: '14px 18px', backgroundColor: 'var(--color-surface-2)', border: llmConfig.useProxy ? '1.5px solid var(--color-accent-primary)' : '1px solid var(--color-border)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
          <label className="form-label">
            <MonitorDown size={12} /> 本地代理模式
          </label>
          <button onClick={() => setLLMConfig({ useProxy: !llmConfig.useProxy })}
            style={{
              width: 44, height: 24, borderRadius: 12, padding: 2, cursor: 'pointer', border: 'none',
              backgroundColor: llmConfig.useProxy ? 'var(--color-accent-primary)' : 'var(--color-surface-3)',
              transition: 'background-color 0.2s', position: 'relative',
            }}>
            <div style={{
              width: 20, height: 20, borderRadius: '50%', backgroundColor: 'var(--color-text-on-accent)',
              transform: llmConfig.useProxy ? 'translateX(20px)' : 'translateX(0)',
              transition: 'transform 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }} />
          </button>
        </div>
        <p className="text-xs leading-relaxed text-[var(--color-text-tertiary)]">
          {llmConfig.useProxy
            ? '✅ 已开启 — 通过本地代理绕过 CORS 限制，适合内网/私有 API'
            : '关闭时浏览器直接调用 API。如果遇到 CORS 错误，请开启并下载代理脚本。'}
        </p>
        {llmConfig.useProxy && (
          <SettingsProxyActions showGuide={showProxyGuide} onToggleGuide={() => setShowProxyGuide(!showProxyGuide)} />
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2.5">
        <button onClick={handleSave} className="btn-primary flex-1 flex items-center justify-center gap-2 rounded-xl py-3 text-sm">
          {saved ? <><Check size={14} /> 已保存</> : '保存配置'}
        </button>
        {llmConfig.apiKey && (
          <button onClick={handleTestConnection} disabled={testStatus === 'testing'}
            className="btn-ghost flex items-center gap-1.5 rounded-xl py-3 px-4 text-sm" style={{ color: testStatus === 'success' ? 'var(--color-accent-emerald)' : testStatus === 'error' ? 'var(--color-accent-rose)' : undefined }}>
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
    </>
  );
}
