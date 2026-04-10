import { useState } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useSettingsStore, PROVIDER_INFO, getDefaultModel } from '@/lib/store/settings';
import { Server, Zap, Key, Check, AlertTriangle, Bell } from 'lucide-react';
import { useNotifications } from '@/lib/hooks/useNotifications';
import { SettingsLLMConfig } from '@/components/settings/SettingsLLMConfig';
import { SettingsDataIO } from '@/components/settings/SettingsDataIO';

const log = createLogger('SettingsContent');

export function SettingsContent() {
  const { llmConfig, setLLMConfig, clearApiKey } = useSettingsStore();
  const isUsingDefault = useSettingsStore((s) => s.isUsingDefaultLLM());
  const [showAdvancedLLM, setShowAdvancedLLM] = useState(!isUsingDefault);
  const { isSupported: notifSupported, permission: notifPermission, prefs: notifPrefs, toggleEnabled: toggleNotif, setReminderHour } = useNotifications();

  return (
    <div className="p-6 flex flex-col gap-5">
      {/* AI Service Mode Selector */}
      <div>
        <label className="form-label" style={{ marginBottom: 10 }}>
          <Server size={12} /> AI 服务模式
        </label>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => { if (!isUsingDefault) { clearApiKey(); setShowAdvancedLLM(false); } }}
            style={{
              borderRadius: 10, padding: '12px 14px', textAlign: 'left', cursor: isUsingDefault ? 'default' : 'pointer',
              backgroundColor: isUsingDefault ? 'var(--color-tint-emerald)' : 'var(--color-surface-2)',
              border: isUsingDefault ? '2px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
              opacity: isUsingDefault ? 1 : 0.75, transition: 'all 0.15s',
            }}
          >
            <div className="flex items-center gap-2" style={{ marginBottom: 4 }}>
              <div style={{
                width: 13, height: 13, borderRadius: '50%', border: `2px solid ${isUsingDefault ? 'var(--color-accent-emerald)' : 'var(--color-text-tertiary)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                {isUsingDefault && <div style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: 'var(--color-accent-emerald)' }} />}
              </div>
              <Zap size={12} style={{ color: isUsingDefault ? 'var(--color-accent-emerald)' : 'var(--color-text-tertiary)' }} />
              <span className="text-sm font-semibold text-[var(--color-text-primary)]">免费服务</span>
            </div>
            <p className="text-[11px] text-[var(--color-text-tertiary)] leading-snug">无需配置，开箱即用</p>
          </button>

          <button
            onClick={() => { setShowAdvancedLLM(true); }}
            style={{
              borderRadius: 10, padding: '12px 14px', textAlign: 'left', cursor: isUsingDefault ? 'pointer' : 'default',
              backgroundColor: !isUsingDefault ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
              border: !isUsingDefault ? '2px solid var(--color-accent-primary)' : '1px solid var(--color-border)',
              opacity: !isUsingDefault ? 1 : 0.75, transition: 'all 0.15s',
            }}
          >
            <div className="flex items-center gap-2" style={{ marginBottom: 4 }}>
              <div style={{
                width: 13, height: 13, borderRadius: '50%', border: `2px solid ${!isUsingDefault ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                {!isUsingDefault && <div style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: 'var(--color-accent-primary)' }} />}
              </div>
              <Key size={12} style={{ color: !isUsingDefault ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)' }} />
              <span className="text-sm font-semibold text-[var(--color-text-primary)]">自带 API Key</span>
            </div>
            <p className="text-[11px] text-[var(--color-text-tertiary)] leading-snug">更强模型，稳定可靠</p>
          </button>
        </div>

        {isUsingDefault ? (
          <div className="flex items-start gap-2" style={{ marginTop: 8, borderRadius: 8, padding: '8px 12px', backgroundColor: 'rgba(217, 169, 78, 0.06)', border: '1px solid rgba(217, 169, 78, 0.15)' }}>
            <AlertTriangle size={12} className="shrink-0" style={{ marginTop: 2, color: 'var(--color-accent-amber)' }} />
            <div>
              <p className="text-xs leading-normal text-[var(--color-text-secondary)]">
                免费服务<strong>稳定性有限</strong>，可能响应缓慢或偶尔不可用。
              </p>
              <p className="text-[11px] text-[var(--color-text-tertiary)] mt-0.5">推荐配置自己的 Key 获得更好体验。</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2" style={{ marginTop: 8, borderRadius: 8, padding: '8px 12px', backgroundColor: 'var(--color-tint-emerald)', border: '1px solid rgba(138, 173, 122, 0.15)' }}>
            <Check size={12} className="shrink-0" style={{ color: 'var(--color-accent-emerald)' }} />
            <p className="text-xs text-[var(--color-text-secondary)]">
              {PROVIDER_INFO[llmConfig.provider].name} · {llmConfig.model || getDefaultModel(llmConfig.provider)}
            </p>
          </div>
        )}
      </div>

      {showAdvancedLLM && (
        <SettingsLLMConfig
          llmConfig={llmConfig}
          setLLMConfig={setLLMConfig}
          clearApiKey={clearApiKey}
          onCollapse={() => setShowAdvancedLLM(false)}
        />
      )}

      {/* Notification Settings */}
      {notifSupported && (
        <div style={{ borderRadius: 10, padding: '16px 20px', backgroundColor: 'var(--color-surface-2)' }}>
          <div className="flex items-center gap-2 mb-3">
            <Bell size={13} className="text-[var(--color-accent-amber)]" />
            <span className="text-sm font-semibold">通知提醒</span>
          </div>
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm">学习目标提醒</div>
                <div className="text-[11px] text-[var(--color-text-tertiary)]">
                  {notifPermission === 'denied' ? '浏览器已阻止通知权限' : '每日提醒你完成学习目标'}
                </div>
              </div>
              <button
                onClick={() => toggleNotif(!notifPrefs.enabled)}
                disabled={notifPermission === 'denied'}
                style={{
                  width: 44, height: 24, borderRadius: 12, position: 'relative', cursor: notifPermission === 'denied' ? 'not-allowed' : 'pointer',
                  backgroundColor: notifPrefs.enabled ? 'var(--color-accent-emerald)' : 'var(--color-surface-3)',
                  transition: 'background-color 0.2s', border: 'none', opacity: notifPermission === 'denied' ? 0.4 : 1,
                }}
              >
                <div style={{
                  width: 18, height: 18, borderRadius: '50%', backgroundColor: 'var(--color-text-on-accent)',
                  position: 'absolute', top: 3, left: notifPrefs.enabled ? 23 : 3, transition: 'left 0.2s',
                }} />
              </button>
            </div>
            {notifPrefs.enabled && (
              <div className="flex items-center justify-between">
                <span className="text-sm">提醒时间</span>
                <select
                  value={notifPrefs.reminderHour}
                  onChange={(e) => setReminderHour(Number(e.target.value))}
                  style={{
                    fontSize: 13, padding: '4px 8px', borderRadius: 6,
                    backgroundColor: 'var(--color-surface-3)', color: 'var(--color-text-primary)',
                    border: '1px solid var(--color-border)',
                  }}
                >
                  {Array.from({ length: 24 }, (_, h) => (
                    <option key={h} value={h}>{String(h).padStart(2, '0')}:00</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      <SettingsDataIO />
    </div>
  );
}
