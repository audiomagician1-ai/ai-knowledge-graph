import { Download } from 'lucide-react';
import { PROXY_SCRIPT_SRC, generateSelfContainedBat, downloadBlob } from '@/lib/store/settings';

interface Props {
  showGuide: boolean;
  onToggleGuide: () => void;
}

export function SettingsProxyActions({ showGuide, onToggleGuide }: Props) {
  return (
    <>
      <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
        <button onClick={onToggleGuide} className="btn-ghost" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
          {showGuide ? '收起指南' : '使用指南'}
        </button>
        <button onClick={() => downloadBlob(generateSelfContainedBat(), 'start-proxy.bat', 'application/bat')}
          className="btn-ghost flex items-center gap-1" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
          <Download size={11} /> start-proxy.bat
        </button>
        <button onClick={() => downloadBlob(PROXY_SCRIPT_SRC, 'cors-proxy.cjs', 'text/javascript')}
          className="btn-ghost flex items-center gap-1" style={{ fontSize: 12, padding: '6px 12px', borderRadius: 8 }}>
          <Download size={11} /> cors-proxy.cjs
        </button>
      </div>
      {showGuide && (
        <div style={{ marginTop: 12, padding: '12px 14px', borderRadius: 8, backgroundColor: 'var(--color-surface-1)', fontSize: 12, lineHeight: 1.8, color: 'var(--color-text-secondary)' }}>
          <strong>快速开始：</strong><br/>
          1. 下载 <code style={{ padding: '1px 5px', borderRadius: 4, backgroundColor: 'var(--color-surface-3)' }}>start-proxy.bat</code><br/>
          2. 双击运行（需已安装 <a href="https://nodejs.org" target="_blank" rel="noopener" style={{ color: 'var(--color-accent-primary)' }}>Node.js</a>）<br/>
          3. 看到 <em>"CORS proxy running on port 9876"</em> 即成功<br/>
          4. 回来点击「测试」按钮验证连接
        </div>
      )}
    </>
  );
}
