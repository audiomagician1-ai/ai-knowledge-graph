---
id: "guiux-motion-easing"
concept: "缓动曲线"
domain: "game-ui-ux"
subdomain: "motion-design"
subdomain_name: "动效设计"
difficulty: 2
is_milestone: true
tags: ["motion-design", "缓动曲线"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 50.2
generation_method: "ai-batch-v1"
unique_content_ratio: 0.833
last_scored: "2026-03-21"
sources: []
---
# 缓动曲线

> **领域**: 游戏UI/UX > 动效设计 | **难度**: ⭐⭐ | **预计学习时间**: 21分钟

## 核心概念

线性/ease-in/ease-out/弹性等缓动函数的选择和应用

## 动效原则

1. **有目的性** — 每个动画都应服务于功能(引导注意力/提供反馈/建立空间关系)
2. **自然性** — 使用符合物理直觉的缓动曲线
3. **节制性** — 动效应增强而非干扰游戏体验

## 缓动曲线分类

- **ease-out** — UI元素入场(快速出现, 缓慢停止)
- **ease-in** — UI元素退场(缓慢开始, 快速消失)
- **ease-in-out** — 位置移动(平滑开始和结束)
- **弹簧曲线** — 有弹性的交互反馈(按钮回弹)

## 时间标准

- **微交互** — 100-200ms(按钮、切换)
- **元素过渡** — 200-300ms(展开、折叠)
- **页面转场** — 300-500ms(界面切换)
- **庆祝动效** — 500-1500ms(升级、解锁)

## 性能优化

- 优先使用GPU加速属性(transform/opacity)
- 对屏幕外元素暂停动画
- 提供动效强度设置(减弱/关闭)

## 关键术语

- **缓动曲线**: 线性/ease-in/ease-out/弹性等缓动函数的选择和应用

## 学习建议

1. 先理解基本概念和设计原则
2. 分析优秀游戏中的实际案例
3. 尝试在自己的项目中实践
4. 收集用户反馈并迭代优化

## 参考资源

- Game UI Database (gameuidatabase.com) — 游戏UI截图参考库
- Laws of UX — UX设计法则集合
- GDC UI/UX Summit — 年度游戏UI/UX峰会演讲
