// ========================================
// User Types
// ========================================

/** 用户资料 */
export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  avatar_url?: string;
  preferred_language: string;
  study_goal?: string;
  created_at: string;
  updated_at: string;
}

/** 用户设置 */
export interface UserSettings {
  user_id: string;
  theme: 'light' | 'dark' | 'system';
  daily_goal_minutes: number;
  notification_enabled: boolean;
  review_reminder_enabled: boolean;
  preferred_difficulty: 'easy' | 'medium' | 'hard' | 'adaptive';
}
