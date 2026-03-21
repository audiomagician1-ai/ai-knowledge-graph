---
id: "guiux-platform-touch-design"
concept: "触屏UI设计"
domain: "game-ui-ux"
subdomain: "multiplatform"
subdomain_name: "多平台适配"
difficulty: 3
is_milestone: false
tags: ["multiplatform", "触屏UI设计"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 52.0
generation_method: "ai-batch-v1"
unique_content_ratio: 0.842
last_scored: "2026-03-21"
sources: []
---
# 触屏UI设计

> **领域**: 游戏UI/UX > 多平台适配 | **难度**: ⭐⭐⭐ | **预计学习时间**: 29分钟

## 核心概念

触摸目标大小(48dp+)、手势和虚拟摇杆设计

## 平台差异

| 平台 | 输入方式 | 屏幕距离 | 分辨率范围 | 特殊要求 |
|------|---------|---------|-----------|---------|
| PC | 键鼠 | 50cm | 1080p-4K | 精确点击、快捷键 |
| 主机 | 手柄 | 2-3m | 1080p-4K | 焦点导航、TRC认证 |
| 移动 | 触屏 | 30cm | 720p-1440p | 触控目标、刘海适配 |
| 掌机 | 手柄+触屏 | 30cm | 720p | 小屏优化 |

## 适配策略

1. **统一核心** — 保持核心UI逻辑一致
2. **平台层适配** — 输入/布局/字号按平台调整
3. **渐进增强** — 基础功能全平台可用, 高级特性按平台增强

## 实践要点

- 触屏最小点击目标: 48dp×48dp (iOS: 44pt)
- 主机字体最小: 18px (TV 3m距离)
- 手柄导航需要完整的焦点系统和可预测的焦点移动
- 输入模式切换应无缝(拔插手柄自动切换)

## 关键术语

- **触屏UI设计**: 触摸目标大小(48dp+)、手势和虚拟摇杆设计

## 学习建议

1. 先理解基本概念和设计原则
2. 分析优秀游戏中的实际案例
3. 尝试在自己的项目中实践
4. 收集用户反馈并迭代优化

## 参考资源

- Game UI Database (gameuidatabase.com) — 游戏UI截图参考库
- Laws of UX — UX设计法则集合
- GDC UI/UX Summit — 年度游戏UI/UX峰会演讲
