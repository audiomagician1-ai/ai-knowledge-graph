import { Compass, Lightbulb, Zap, BarChart3 } from 'lucide-react';
import type { ChoiceOption } from '@/lib/store/dialogue';

const TYPE_CONFIG: Record<string, { icon: typeof Compass; label: string }> = {
  explore: { icon: Compass, label: '方向' },
  answer:  { icon: Lightbulb, label: '回答' },
  action:  { icon: Zap, label: '行动' },
  level:   { icon: BarChart3, label: '水平' },
};

interface Props {
  choices: ChoiceOption[];
  onSelect: (choiceId: string) => void;
  disabled?: boolean;
  dimmed?: boolean; // true when user is typing
}

export function ChoiceButtons({ choices, onSelect, disabled, dimmed }: Props) {
  return (
    <div
      className="flex flex-col gap-2 transition-opacity duration-200"
      style={{ opacity: dimmed ? 0.4 : 1 }}
    >
      {choices.map((choice) => {
        const cfg = TYPE_CONFIG[choice.type] || TYPE_CONFIG.explore;
        const Icon = cfg.icon;
        return (
          <button
            key={choice.id}
            onClick={() => onSelect(choice.id)}
            disabled={disabled}
            className="group flex items-center gap-3.5 px-5 py-3.5 rounded-lg text-left transition-all duration-150 active:scale-[0.98]"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              border: '1px solid var(--color-border)',
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.5 : 1,
            }}
            onMouseEnter={(e) => {
              if (!disabled) {
                e.currentTarget.style.borderColor = 'var(--color-accent-primary)';
                e.currentTarget.style.backgroundColor = 'var(--color-tint-primary)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border)';
              e.currentTarget.style.backgroundColor = 'var(--color-surface-2)';
            }}
          >
            <div
              className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
              style={{ backgroundColor: 'var(--color-surface-3)' }}
            >
              <Icon size={14} style={{ color: 'var(--color-text-secondary)' }} />
            </div>
            <span
              className="text-[13px] leading-snug"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {choice.text}
            </span>
          </button>
        );
      })}
    </div>
  );
}