---
id: "guiux-typo-subtitle-design"
concept: "字幕设计"
domain: "game-ui-ux"
subdomain: "typography"
subdomain_name: "字体排版"
difficulty: 2
is_milestone: false
tags: ["typography", "字幕设计"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 51.3
generation_method: "ai-batch-v1"
unique_content_ratio: 0.85
last_scored: "2026-03-21"
sources: []
---
# 字幕设计

> **领域**: 游戏UI/UX > 字体排版 | **难度**: ⭐⭐ | **预计学习时间**: 21分钟

## 核心概念

过场字幕、对话字幕的位置、样式和无障碍标准

## 字体选择

1. **无衬线体** — 清晰现代，适合UI正文(Noto Sans, Inter)
2. **衬线体** — 古典庄重，适合RPG/奇幻风格标题
3. **像素字体** — 复古风格游戏的首选
4. **手写体** — 增加个性，适合手绘风格游戏

## 排版层级

- **H1(标题)** — 24-36px, Bold, 用于页面/面板标题
- **H2(副标题)** — 18-24px, SemiBold, 用于分组标题
- **Body(正文)** — 14-16px, Regular, 用于描述和说明
- **Caption(注释)** — 10-12px, Light, 用于辅助信息

## 实践要点

- 游戏正文最小字号不低于14px(移动端16px)
- 深色背景上的浅色文字需要2px+描边或半透明底板
- 多语言支持需考虑CJK字体的巨大文件体积
- 使用SDF渲染确保缩放不失真

## 工具链

- **BMFont** — 位图字体生成器
- **msdfgen** — SDF字体生成
- **Google Fonts** — 开源字体库

## 关键术语

- **字幕设计**: 过场字幕、对话字幕的位置、样式和无障碍标准

## 学习建议

1. 先理解基本概念和设计原则
2. 分析优秀游戏中的实际案例
3. 尝试在自己的项目中实践
4. 收集用户反馈并迭代优化

## 参考资源

- Game UI Database (gameuidatabase.com) — 游戏UI截图参考库
- Laws of UX — UX设计法则集合
- GDC UI/UX Summit — 年度游戏UI/UX峰会演讲
