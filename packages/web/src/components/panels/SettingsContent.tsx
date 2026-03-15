import { useState, useRef } from 'react';
import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, probeCORS, probeProxy, PROXY_SCRIPT_SRC, generateSelfContainedBat, downloadBlob } from '@/lib/store/settings';
import type { LLMProvider } from '@/lib/store/settings';
import { Eye, EyeOff, Check, Trash2, Shield, Key, Server, Wifi, WifiOff, Loader2, Globe, Box, Info, Download, Upload, MonitorDown } from 'lucide-react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useDialogueStore } from '@/lib/store/dialogue';

const PROVIDERS: LLMProvider[] = ['openrouter', 'openai', 'deepseek', 'custom'];

export function SettingsContent() {
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const [connError, setConnError] = useState('');
  const { graphData } = useGraphStore();
  const { progress, history, streak, importData } = useLearningStore();
  const { savedConversations, importConversations } = useDialogueStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [importMessage, setImportMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };

  const [showProxyGuide, setShowProxyGuide] = useState(false);

  const handleTestConnection = async () => {
    if (!llmConfig.apiKey) { setTestStatus('error'); setTestMessage('请先输入 API Key'); return; }
    setTestStatus('testing'); setTestMessage('');
    try {
      const effectiveUrl = resolveBaseUrl(
        llmConfig.baseUrl || PROVIDER_INFO[llmConfig.provider].defaultBase,
        !!llmConfig.useProxy,
      );
      const result = await probeCORS(effectiveUrl, llmConfig.apiKey, llmConfig.model || 'gpt-4o');
      if (result.ok) {
        setTestStatus('success');
        setTestMessage(llmConfig.useProxy ? '通过本地代理连接成功' : '连接成功');
        setTimeout(() => setTestStatus('idle'), 4000);
        return;
      }
      // Failed — give specific hints with detailed error info
      let errMsg = result.detail ? `连接失败: ${result.detail}` : '连接失败';
      if (llmConfig.useProxy) {
        const alive = await probeProxy();
        errMsg = alive
          ? `代理在运行但 API 返回错误${result.detail ? ` (${result.detail})` : ''}，请检查 URL / Key / 模型名。`
          : '本地代理未运行。请先下载并启动代理脚本。';
      } else {
        errMsg = `连接失败${result.detail ? `: ${result.detail}` : ''}。如果是内网 API，请启用「本地代理」并启动代理脚本。`;
      }
      setConnError(errMsg);
      setTestStatus('error');
      setTestMessage(errMsg);
      setTimeout(() => setTestStatus('idle'), 6000);
    } catch (err) {
      setTestStatus('error');
      setTestMessage(err instanceof Error ? err.message : '网络错误');
      setTimeout(() => setTestStatus('idle'), 6000);
    }
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

      {/* Local Proxy Toggle */}
      <div style={{ borderRadius: 10, padding: '14px 18px', backgroundColor: 'var(--color-surface-2)', border: llmConfig.useProxy ? '1.5px solid var(--color-accent-primary)' : '1px solid var(--color-border)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
          <label className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex' }}>
            <MonitorDown size={12} /> 本地代理模式
          </label>
          <button onClick={() => setLLMConfig({ useProxy: !llmConfig.useProxy })}
            style={{
              width: 44, height: 24, borderRadius: 12, padding: 2, cursor: 'pointer', border: 'none',
              backgroundColor: llmConfig.useProxy ? 'var(--color-accent-primary)' : 'var(--color-surface-3)',
              transition: 'background-color 0.2s', position: 'relative',
            }}>
            <div style={{
              width: 20, height: 20, borderRadius: '50%', backgroundColor: '#fff',
              transform: llmConfig.useProxy ? 'translateX(20px)' : 'translateX(0)',
              transition: 'transform 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
            }} />
          </button>
        </div>
        <p style={{ color: 'var(--color-text-tertiary)', fontSize: 12, lineHeight: 1.6 }}>
          {llmConfig.useProxy
            ? '✅ 已开启 — 通过本地代理绕过 CORS 限制，适合内网/私有 API'
            : '关闭时浏览器直接调用 API。如果遇到 CORS 错误，请开启并下载代理脚本。'}
        </p>
        {llmConfig.useProxy && (
          <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
            <button onClick={() => setShowProxyGuide(!showProxyGuide)}
              className="btn-ghost" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
              {showProxyGuide ? '收起指南' : '使用指南'}
            </button>
            <button onClick={() => downloadBlob(generateSelfContainedBat(), 'start-proxy.bat', 'application/bat')}
              className="btn-ghost flex items-center gap-1" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
              <Download size={11} /> start-proxy.bat（一键启动）
            </button>
            <button onClick={() => downloadBlob(PROXY_SCRIPT_SRC, 'cors-proxy.cjs', 'text/javascript')}
              className="btn-ghost flex items-center gap-1" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
              <Download size={11} /> cors-proxy.cjs（手动）
            </button>
          </div>
        )}
        {showProxyGuide && llmConfig.useProxy && (
          <div style={{ marginTop: 12, padding: '12px 14px', borderRadius: 8, backgroundColor: 'var(--color-surface-1)', fontSize: 12, lineHeight: 1.8, color: 'var(--color-text-secondary)' }}>
            <strong>快速开始：</strong><br/>
            1. 下载 <code style={{ padding: '1px 5px', borderRadius: 4, backgroundColor: 'var(--color-surface-3)' }}>start-proxy.bat</code>（自包含，无需其他文件）<br/>
            2. 双击运行（需已安装 <a href="https://nodejs.org" target="_blank" rel="noopener" style={{ color: 'var(--color-accent-primary)' }}>Node.js</a>）<br/>
            3. 看到 <em>"CORS proxy running on port 9876"</em> 即成功<br/>
            4. 回来点击「测试」按钮验证连接
          </div>
        )}
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
          a.href = url; a.download = `akg-data-${new Date().toISOString().slice(0, 10)}.json`; a.click(); URL.revokeObjectURL(url);
        }} className="btn-ghost flex-1 flex items-center justify-center gap-2" style={{ borderRadius: 10, padding: '12px 0', fontSize: 13 }}>
          <Download size={14} /> 导出
        </button>
        <button onClick={() => fileInputRef.current?.click()}
          className="btn-ghost flex-1 flex items-center justify-center gap-2" style={{ borderRadius: 10, padding: '12px 0', fontSize: 13 }}>
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
              // Import learning data
              if (data.progress || data.history || data.streak) {
                const { imported, merged } = importData({
                  progress: data.progress,
                  history: data.history,
                  streak: data.streak,
                });
                results.push(`学习进度: ${imported} 新增, ${merged} 更新`);
              }
              // Import conversations
              if (data.conversations && Array.isArray(data.conversations)) {
                const { imported } = importConversations(data.conversations);
                results.push(`对话记录: ${imported} 条导入`);
              }
              // Import settings (except API key for security)
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
          e.target.value = ''; // Reset file input
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
        <p style={{ fontSize: 12, lineHeight: 1.6, color: 'var(--color-text-tertiary)' }}>
          Key 仅存在浏览器本地。{llmConfig.useProxy ? '本地代理模式下，请求通过本机代理转发，不经过任何外部服务器。' : '直连模式下，请求直接从浏览器发往 LLM API。'}
        </p>
      </div>
    </div>
  );
}
