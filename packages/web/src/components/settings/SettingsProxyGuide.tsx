import { Download } from 'lucide-react';
import { PROXY_SCRIPT_SRC, generateSelfContainedBat, downloadBlob } from '@/lib/store/settings';

interface Props {
  showGuide: boolean;
  onToggleGuide: () => void;
}

export function SettingsProxyActions({ showGuide, onToggleGuide }: Props) {
  return (
    <>
      <div className="mt-2.5 flex gap-2">
        <button onClick={onToggleGuide} className="btn-ghost text-xs py-1.5 px-3 rounded-lg">
          {showGuide ? '收起指南' : '使用指南'}
        </button>
        <button onClick={() => downloadBlob(generateSelfContainedBat(), 'start-proxy.bat', 'application/bat')}
          className="btn-ghost flex items-center gap-1 text-xs py-1.5 px-3 rounded-lg">
          <Download size={11} /> start-proxy.bat
        </button>
        <button onClick={() => downloadBlob(PROXY_SCRIPT_SRC, 'cors-proxy.cjs', 'text/javascript')}
          className="btn-ghost flex items-center gap-1 text-xs py-1.5 px-3 rounded-lg">
          <Download size={11} /> cors-proxy.cjs
        </button>
      </div>
      {showGuide && (
        <div className="mt-3 p-3 rounded-lg bg-[var(--color-surface-1)] text-xs leading-relaxed text-[var(--color-text-secondary)]">
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
